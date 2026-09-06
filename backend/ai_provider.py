"""
Thin wrapper around Google's free-tier Gemini API.

Get a free key at https://aistudio.google.com/apikey and put it in backend/.env
as GEMINI_API_KEY (copy backend/.env.example to backend/.env first).

Model: gemini-2.5-flash — on Google's free tier as of writing.
If Google renames/retires it, swap MODEL_NAME below.
"""
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL_NAME = "gemini-3.6-flash"

_api_key = os.getenv("GEMINI_API_KEY")
_client = genai.Client(api_key=_api_key) if _api_key else None


class AIProviderError(Exception):
    pass


def _ensure_client():
    if _client is None:
        raise AIProviderError(
            "GEMINI_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and add a free key from https://aistudio.google.com/apikey"
        )


def generate_text(prompt: str, system_instruction: str = None) -> str:
    """Plain text generation."""
    _ensure_client()
    config = types.GenerateContentConfig(system_instruction=system_instruction) if system_instruction else None
    response = _client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config,
    )
    return (response.text or "").strip()


def generate_json(prompt: str, system_instruction: str = None) -> dict:
    """
    Ask Gemini to return strict JSON and parse it.
    We ask in the prompt AND set response_mime_type for reliability.
    """
    _ensure_client()
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
    )
    response = _client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config,
    )
    raw = (response.text or "{}").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: strip stray markdown fences if the model added them anyway
        cleaned = raw.strip("`").replace("json\n", "", 1)
        return json.loads(cleaned)


def generate_json_from_file(
    file_bytes: bytes, mime_type: str, prompt: str, system_instruction: str = None
) -> dict:
    """Multimodal: send a file (image/pdf/audio) + prompt, get structured JSON back."""
    _ensure_client()
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
    )
    response = _client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
            prompt,
        ],
        config=config,
    )
    raw = (response.text or "{}").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        cleaned = raw.strip("`").replace("json\n", "", 1)
        return json.loads(cleaned)
