"""JWT-protected API with credentials and signing key supplied by environment."""

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI(title="Assignment 3 - Protected API", version="1.0.0")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
ALGORITHM = "HS256"
TOKEN_LIFETIME_MINUTES = 30


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Server configuration is missing {name}",
        )
    return value


def _password_digest(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)


def authenticate(username: str, password: str) -> bool:
    configured_username = _required_setting("API_USERNAME")
    configured_password = _required_setting("API_PASSWORD")
    salt = _required_setting("PASSWORD_SALT").encode("utf-8")
    username_matches = hmac.compare_digest(username, configured_username)
    password_matches = hmac.compare_digest(
        _password_digest(password, salt),
        _password_digest(configured_password, salt),
    )
    return username_matches and password_matches


def issue_token(username: str) -> str:
    secret = _required_setting("JWT_SECRET")
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_LIFETIME_MINUTES
    )
    return jwt.encode(
        {"sub": username, "exp": expires_at},
        secret,
        algorithm=ALGORITHM,
    )


@app.post("/token", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    if not authenticate(form.username, form.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=issue_token(form.username))


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(
            token,
            _required_setting("JWT_SECRET"),
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject:
            raise jwt.InvalidTokenError("Missing subject")
        return subject
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/protected")
def protected(current_user: str = Depends(get_current_user)) -> dict[str, str]:
    return {"message": f"Authenticated as {current_user}"}
