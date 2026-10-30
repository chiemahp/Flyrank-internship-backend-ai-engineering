"""A small HTTP service that delegates a single prompt to OpenAI."""

import os

from fastapi import FastAPI, HTTPException, status
from openai import APIError, OpenAI
from pydantic import BaseModel, Field

app = FastAPI(title="Assignment 5 - AI API", version="1.0.0")


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)


class PromptResponse(BaseModel):
    model: str
    response: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate", response_model=PromptResponse)
def generate(payload: PromptRequest) -> PromptResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY is not configured",
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        result = OpenAI(api_key=api_key).chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": payload.prompt}],
            max_tokens=1000,
            temperature=0.2,
        )
    except APIError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI provider request failed: {exc.message}",
        ) from exc

    answer = result.choices[0].message.content
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI provider returned an empty response",
        )
    return PromptResponse(model=result.model, response=answer)
