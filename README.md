# 🇮🇳 IndiTrade-ai: Advanced Trade Opportunities API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/AI-Gemini_2.0_Flash_Lite-4285F4.svg?style=flat&logo=google-gemini&logoColor=white)](https://aistudio.google.com/)
[![Render](https://img.shields.io/badge/Deploy-Render-46E3B7.svg?style=flat&logo=render&logoColor=white)](https://render.com)

**Real-time market scanning and AI-driven opportunity analysis for Indian trade sectors.**  

IndiTrade-ai is a production-grade FastAPI service that answers the critical question: *"What are the current trade opportunities for [sector] in India?"* It fetches live market data from DuckDuckGo, synthesizes it using Google Gemini's latest LLMs, and generates structured PDF-ready Markdown reports.

---

## 🚀 Live Demo & API Documentation
👉 **[Launch Interactive Swagger UI (Render)](https://trade-opportunities-api-64pk.onrender.com/docs)**
> **Note:** On the Render free tier, the first request may take ~30 seconds for the instance to "wake up" (cold start). Subsequent requests are instant.

---

## 📋 Assignment Requirements Checklist
This project fulfills and exceeds all requirements for the "Trade Opportunities API" assessment:

| Requirement | Implementation Detail | Status |
| :--- | :--- | :---: |
| **FastAPI Backend** | Python 3.13, Async-native, auto-docs | ✅ |
| **Web Search API** | Real-time scanning using `ddgs` (DuckDuckGo) | ✅ |
| **LLM Integration** | Gemini 3.1 Preview + 2.0 Flash Lite fallback | ✅ |
| **Session Tracking** | Stateless JWT-based Guest-ID sessions | ✅ |
| **Rate Limiting** | `slowapi` decorators (5/min for analysis, 10/min for auth) | ✅ |
| **Security Headers** | Custom Middleware (Nosniff, Frame-denial, XSS-prot) | ✅ |
| **Input Validation** | Strict regex for sector names (`^[a-zA-Z\s]{2,50}$`) | ✅ |
| **Error Handling** | Clean HTTP 429/503/500 mapping with logging | ✅ |
| **Environment Config** | Type-safe `pydantic-settings` from `.env` | ✅ |
| **Deployment** | Dockerized + `render.yaml` for one-click setup | ✅ |

---

## 🛡️ Getting Started (Local Development)

### 1. Pre-requisites
- **Python 3.11+** or **Docker Desktop**
- **Gemini API Key** ([Get one free here](https://aistudio.google.com/app/apikey))

### 2. Quick Install
```bash
# Clone the repository
git clone https://github.com/geeked-anshuk666/IndiTrade-ai.git
cd IndiTrade-ai

# Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Configure Environment
cp .env.example .env
# Open .env and add your GEMINI_API_KEY and a random JWT_SECRET
```

### 3. Launch Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interact via **`http://127.0.0.1:8000/docs`**

---

## 📖 How to Use (Evaluator Guide)

The API uses a **Guest JWT Flow**—no password is required, making it easy for reviewers to test.

1.  **Authorize**: Go to the `/auth/token` endpoint. 
    - Click **"Try it out"**.
    - Enter any string as your `client_id` (e.g., `test-evaluator-1`).
    - **Copy** the `access_token` from the response.
2.  **Authenticate**: Click the **"Authorize"** button at the top right of the Swagger UI.
    - Paste your token into the **Value** field and click **Authorize**.
3.  **Analyze**: Go to the `GET /analyze/{sector}` endpoint.
    - Click **"Try it out"**.
    - Enter a sector name (e.g. `pharmaceuticals`, `textiles`, `automotive`).
    - Click **Execute** and wait ~15s for your AI-generated report.

---

## 📁 Project Structure

```text
IndiTrade-ai/
├── app/                  # Main application source
│   ├── auth/             # JWT & Session logic
│   ├── middleware/       # Security & Rate Limit configs
│   ├── prompts/          # AI Prompt templates
│   ├── routers/          # FastAPI Route handlers
│   ├── services/         # Business logic (Gemini, DDG, Search)
│   └── main.py           # App entry point
├── test/                 # Automated test suite
│   ├── test_api_v3.py    # E2E Integration test
│   └── check_models.py   # Utility to verify Gemini availability
├── Dockerfile            # Production container config
├── render.yaml           # Deployment configuration
└── requirements.txt      # Dependency manifest
```

---

## ⚙️ Technical Architecture

- **Search Service (`ddgs`)**: Performs targeted queries for "export opportunities" and "growth trends."
- **AI Service (Gemini)**: Uses a 3-attempt exponential backoff retry mechanism to handle Gemini's free tier congestion (429/503 errors).
- **Stateless Auth**: Uses `HS256` JWTs. The server verifies the signature without needing a database, keeping the architecture clean and horizontally scalable.
- **Security Middleware**: Forces secure headers on every response to protect against XSS and clickjacking.

---

## 🔍 Verification
You can run the full automated integration test with:
```bash
python test/test_api_v3.py
```
This automatically tests the health check, gets a token, performs an analysis, and saves the final Markdown report to `test/results/`.

---

**Developed for the Trade Opportunities API hiring assessment.**  
*By [anshuk jirli](https://github.com/geeked-anshuk666)*
