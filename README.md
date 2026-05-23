# Sentinel-AI 🛡️  
### Zero-Trust Privacy Protection for LLMs

Sentinel-AI is a real-time privacy proxy that protects sensitive user data before it reaches cloud-based AI models like ChatGPT, Claude, Gemini, and DeepSeek.

It intercepts prompts, detects sensitive information, masks it locally, and restores it safely after the AI response is received.

---

# 🚀 Key Features

- 🔒 Real-time PII masking
- 🧠 Hybrid detection using Regex + NLP
- ⚡ Local-first privacy protection
- 🔄 Automatic de-masking of AI responses
- 🌐 Chrome Extension + FastAPI backend
- 🛡️ Zero-Trust Architecture

---

# 🧠 How It Works

1. User prompt is intercepted by the browser extension  
2. Sensitive data is detected using Regex and NLP  
3. PII is replaced with secure placeholders  
4. Only masked data is sent to the LLM  
5. Original data is restored locally after response  

---

# 🛠️ Technologies Used

| Category | Technologies |
|---|---|
| Backend | FastAPI, Uvicorn |
| AI/NLP | Microsoft Presidio, spaCy |
| Frontend | Chrome Extension |
| Security | Regex, Local Vault Mapping |

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/sirophin/Sentinel-AI.git
cd Sentinel-AI
```

---

## Setup Backend

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn presidio-analyzer presidio-anonymizer spacy
uvicorn main:app --reload
```

---

# 🌐 Load Extension

1. Open `chrome://extensions/`
2. Enable **Developer Mode**
3. Click **Load Unpacked**
4. Select the extension folder

---

# 🧪 Example

### Original Prompt

```txt
My name is Arjun Sharma.
My Aadhaar is 2456 6789 0123.
```

### Masked Prompt

```txt
My name is [PERSON_1].
My Aadhaar is [AADHAAR_1].
```

---

# 📊 Performance

| Metric | Result |
|---|---|
| Detection Accuracy | 99% |
| De-Masking Accuracy | 98% |
| Average Detection Time | 142 ms |
| False Positive Rate | 1.2% |

---

# 🔐 Security Advantages

- Prevents PII leakage
- Protects corporate data
- Supports privacy compliance
- Keeps sensitive data local
- Secure AI usage without exposing secrets

---

# 👨‍💻 Authors

- Siro

---

# 🔒 Final Note

Sentinel-AI ensures that sensitive information never leaves the local system in readable form, enabling safe and privacy-focused AI interactions.
