# Assignment 3 — Protect endpoints with authentication

This API issues short-lived HS256 bearer tokens from `/token` and protects
`/protected`. It uses a single environment-configured account for a compact
demonstration; it is not a multi-user identity system.

## Configure and run (PowerShell)

Use unique values; do not commit the secrets:

```powershell
$env:API_USERNAME = "student"
$env:API_PASSWORD = "replace-with-a-strong-password"
$env:PASSWORD_SALT = "replace-with-a-random-salt"
$env:JWT_SECRET = "replace-with-at-least-32-random-bytes"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Missing configuration produces an explicit server error instead of silently
using a known development secret. Obtain a token in `/docs` by calling
`POST /token` with form fields `username` and `password`, then authorize with the returned bearer token.
