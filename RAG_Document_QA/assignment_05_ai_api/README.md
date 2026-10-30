# Assignment 5 — Integrate an AI API into a working service

The FastAPI endpoint `/generate` validates a prompt and returns text from the
OpenAI Chat Completions API. The API key is read only from the environment.

## Run (PowerShell)

```powershell
$env:OPENAI_API_KEY = "your-key"
# Optional: $env:OPENAI_MODEL = "gpt-4o-mini"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Send `POST /generate` with JSON `{"prompt":"Explain a simple concept."}`.
Interactive docs are at `http://127.0.0.1:8000/docs`. Provider failures are
reported as HTTP 502; missing key configuration is HTTP 503.
