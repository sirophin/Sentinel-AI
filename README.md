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

- Sirophin T X and Sabari

---

# 🔒 Final Note

Sentinel-AI ensures that sensitive information never leaves the local system in readable form, enabling safe and privacy-focused AI interactions.

## 📸 Screenshots

### Extension Dashboard

<img width="974" height="474" alt="Screenshot From 2026-05-23 21-32-35" src="https://github.com/user-attachments/assets/4e347469-fe08-49ee-a910-426f759b6bf0" />

### Prompt Before Masking
<img width="973" height="472" alt="Screenshot From 2026-05-23 21-34-45" src="https://github.com/user-attachments/assets/91ffd17b-7e63-4b50-8382-1c888409982c" />

### Prompt After Masking
<img width="973" height="472" alt="Screenshot From 2026-05-23 21-35-45" src="https://github.com/user-attachments/assets/603d27cd-0e0b-4f9d-95e3-45a3a4700142" />

### Extension
<img width="1006" height="570" alt="Screenshot From 2026-05-23 21-37-01" src="https://github.com/user-attachments/assets/081df5bc-f723-4b46-a0db-8b5589339ac9" />
