from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os, uuid, logging

# ── Silence favicon noise ─────────────────────────────────────────────────────
class EndpointFilter(logging.Filter):
    def filter(self, record):
        return "favicon" not in record.getMessage()
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

# ── Presidio imports ──────────────────────────────────────────────────────────
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

app = FastAPI()

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Templates ─────────────────────────────────────────────────────────────────
template_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=template_path)

# ── NLP Engine (force SpaCy) ──────────────────────────────────────────────────
configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
}
provider  = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()
analyzer   = AnalyzerEngine(nlp_engine=nlp_engine, default_score_threshold=0.35)
anonymizer = AnonymizerEngine()

# ── Custom Recognizers ────────────────────────────────────────────────────────
def add(entity, name, regex, score=0.9):
    analyzer.registry.add_recognizer(
        PatternRecognizer(supported_entity=entity,
                          patterns=[Pattern(name=name, regex=regex, score=score)])
    )

add("IP_ADDRESS",   "ip_v4",       r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
add("API_KEY",      "sk_key",      r"sk-[a-zA-Z0-9]{20,}")
add("API_KEY",      "bearer",      r"Bearer\s+[A-Za-z0-9\-_\.]{20,}", 0.85)
add("API_KEY",      "github_pat",  r"ghp_[A-Za-z0-9]{36}")
add("API_KEY",      "aws_key",     r"AKIA[0-9A-Z]{16}")
add("FINANCE_INFO", "salary",      r"(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s?(?:salary|per month|rupees|INR|USD|LPA|CTC)", 0.8)
add("AADHAAR",      "aadhaar",     r"\b[2-9]\d{3}[\s\-]?\d{4}[\s\-]?\d{4}\b")
add("PAN_CARD",     "pan",         r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
add("CREDIT_CARD",  "cc",          r"\b(?:\d[ \-]?){13,16}\b", 0.6)
add("PASSPORT",     "passport_in", r"\b[A-Z][1-9][0-9]{7}\b")
add("VEHICLE_REG",  "vehicle",     r"\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?[A-Z]{1,2}[\s\-]?\d{4}\b")

ALL_ENTITIES = [
    "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION",
    "IP_ADDRESS", "API_KEY", "FINANCE_INFO", "AADHAAR",
    "PAN_CARD", "CREDIT_CARD", "PASSPORT", "VEHICLE_REG",
    "DATE_TIME", "NRP", "ORG",
]

# ── In-memory Vault (session → token map) ────────────────────────────────────
# vault[session_id] = { "<TOKEN>": "original_value" }
vault: dict[str, dict[str, str]] = {}

# ── Dashboard state ───────────────────────────────────────────────────────────
dashboard_stats   = {"total": 0, "leaks": 0}
pii_counts        = {e: 0 for e in ALL_ENTITIES}
interception_logs = []

# ── Pydantic models ───────────────────────────────────────────────────────────
class Prompt(BaseModel):
    text: str
    session_id: str = ""

class DemaskRequest(BaseModel):
    session_id: str
    response_text: str

# ── Helpers ───────────────────────────────────────────────────────────────────
def mask_text(text: str, session_id: str):
    """Detect PII, replace with tokens, store mapping in vault."""
    results = analyzer.analyze(text=text, entities=ALL_ENTITIES, language="en")
    if not results:
        return text, [], session_id

    # Sort descending so we can replace without offset drift
    results_sorted = sorted(results, key=lambda r: r.start, reverse=True)

    masked = text
    token_map: dict[str, str] = vault.get(session_id, {})
    found_types = []

    for r in results_sorted:
        original_value = text[r.start:r.end]
        entity         = r.entity_type

        # Build a unique token like <PERSON_1>
        count = sum(1 for k in token_map if k.startswith(f"<{entity}_"))
        token = f"<{entity}_{count + 1}>"

        token_map[token] = original_value
        masked = masked[:r.start] + token + masked[r.end:]
        found_types.append(entity)

    vault[session_id] = token_map
    return masked, found_types, session_id


def demask_text(text: str, session_id: str):
    """Swap tokens back to original values."""
    token_map = vault.get(session_id, {})
    restored  = text
    replaced  = 0
    for token, original in token_map.items():
        if token in restored:
            restored = restored.replace(token, original)
            replaced += 1
    return restored, replaced

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "stats":        dashboard_stats,
            "logs":         interception_logs[:15],
            "chart_labels": list(pii_counts.keys()),
            "chart_data":   list(pii_counts.values()),
        }
    )


@app.post("/process")
async def process_prompt(prompt: Prompt):
    text       = prompt.text
    session_id = prompt.session_id or str(uuid.uuid4())

    masked_text, found_types, session_id = mask_text(text, session_id)

    # ── Update dashboard ──────────────────────────────────────────────────
    dashboard_stats["total"] += 1
    if found_types:
        dashboard_stats["leaks"] += len(found_types)
        for e in found_types:
            pii_counts[e] = pii_counts.get(e, 0) + 1
        interception_logs.insert(0, {
            "time":           datetime.now().strftime("%H:%M:%S"),
            "entities":       list(set(found_types)),
            "masked_preview": masked_text[:60] + ("..." if len(masked_text) > 60 else ""),
        })

    print(f"\n[Sentinel-AI] Original  : {text}")
    print(f"[Sentinel-AI] Masked    : {masked_text}")
    print(f"[Sentinel-AI] Entities  : {list(set(found_types))}")
    print(f"[Sentinel-AI] SessionID : {session_id}")

    return {
        "processed_text": masked_text,
        "items_found":    list(set(found_types)),
        "session_id":     session_id,
    }


@app.post("/demask")
async def demask_response(req: DemaskRequest):
    restored, tokens_replaced = demask_text(req.response_text, req.session_id)

    print(f"\n[Sentinel-AI] Demasking session : {req.session_id}")
    print(f"[Sentinel-AI] Tokens replaced   : {tokens_replaced}")
    print(f"[Sentinel-AI] Restored          : {restored}")

    return {
        "restored_text":  restored,
        "tokens_replaced": tokens_replaced,
    }


@app.get("/vault/{session_id}")
async def get_vault(session_id: str):
    token_map = vault.get(session_id)
    if not token_map:
        return {"error": "Session not found"}
    return {"session_id": session_id, "token_map": token_map}


@app.get("/stats")
async def get_stats():
    return {"stats": dashboard_stats, "pii_counts": pii_counts}
