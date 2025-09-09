# app/routers/ai.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from starlette.responses import Content

from ..config import Settings
from loguru import logger

# OpenAI SDK v1.x
from openai import OpenAI
import httpx
import hvac

settings= Settings()
router = APIRouter(prefix="/ai", tags=["ai"])

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    system_prompt: Optional[str] = Field(
        default="You are a concise, helpful assistant.",
        description="Optoinal system instructions"
    )
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)

class ChatResponse(BaseModel):
    reply: str

def _get_openai_api_key() -> str | None:
    if settings.VAULT_ADDR and settings.VAULT_TOKEN:
        try:
            client = hvac.Client(url=settings.VAULT_ADDR, token=settings.VAULT_TOKEN)
            secret = client.secrets.kv.v2.read_secret_version(path=settings.VAULT_OPENAI_SECRET_PATH)
            key = secret["data"]["data"].get("OPENAI_API_KEY")
            if key:
                return key or None
            logger.warning("Vault path found but OPENAI_API_KEY missing in data")
        except Exception as e:
            logger.warning(f"Vault fetch for OPENAI_API_KEY failed: {e}")
    return settings.OPENAI_API_KEY


def _get_openai_client() -> OpenAI:

    key = _get_openai_api_key()
    if not isinstance(key,str) or not key.strip():
        raise HTTPException(status_code=503, detail="LLM not configured (OPENAI_API_KEY missing)")
    return OpenAI(api_key=key.strip(), timeout=httpx.Timeout(settings.OAI_TIMEOUT_SECONDS))
    # """
    # Build an OpenAI client with timeouts.
    # If no API key is configured, raise 503 so the API stays honest.
    # """
    # if not settings.OPENAI_API_KEY:
    #     raise HTTPException(
    #         status_code=503,
    #         detail = "LLM not configured (missing OPENAI_API_KEY)"
    #     )
    # # Use httpx timeout for safety
    # client = OpenAI(
    #     api_key=settings.OPENAI_API_KEY,
    #     timeout=httpx.Timeout(settings.OAI_TIMEOUT_SECONDS)
    # )
    # return client

@router.get("/health", summary="Quick check that LLM is configured")
def ai_health():
    # Don't call the model (costs $$), just confirm we have a key
    # configured = bool(settings.OPENAI_API_KEY)
    configured = _get_openai_api_key() is not None
    return {"llm_configured": configured, "model": settings.OAI_MODEL}

@router.post("/ask", response_model=ChatResponse, summary="Ask the LLM a question")
def ask_ai(payload: ChatRequest):
    client = _get_openai_client()
    try:
        #Chat completion API
        resp = client.chat.completions.create(
            model=settings.OAI_MODEL,
            messages=[
                {"role": "system", "content":payload.system_prompt or ""},
                {"role": "user", "content": payload.message},
            ],
            temperature = payload.temperature,
        )
        text = resp.choices[0].messages.content or ""
        return ChatResponse(reply=text.strip())
    except Exception as e:
        logger.exception("LLM call failed")
        raise HTTPException(status_code=502, detail=f"LLM upstream error {e}")