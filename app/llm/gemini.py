import os
from functools import lru_cache

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

# Override with the GEMINI_MODEL environment variable (or Streamlit secret).
DEFAULT_MODEL = "gemini-3.5-flash"
REQUEST_TIMEOUT_MS = 60_000


class LLMError(Exception):
    """Raised when the model cannot produce an answer."""


class LLMQuotaExceededError(LLMError):
    """Raised when the Gemini free/paid quota or rate limit is hit."""


class LLMNotConfiguredError(LLMError):
    """Raised when no GEMINI_API_KEY is available."""


def is_configured() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))


@lru_cache(maxsize=1)
def _get_client(api_key: str):
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS),
    )


def generate_answer(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise LLMNotConfiguredError("GEMINI_API_KEY is not set.")

    model = os.getenv("GEMINI_MODEL") or DEFAULT_MODEL

    try:
        response = _get_client(api_key).models.generate_content(
            model=model,
            contents=prompt,
        )
    except errors.APIError as exc:
        if exc.code == 429:
            raise LLMQuotaExceededError(
                "Gemini quota or rate limit exceeded."
            ) from exc

        raise LLMError(f"Gemini request failed: {exc}") from exc
    except Exception as exc:
        raise LLMError(f"Gemini request failed: {exc}") from exc

    text = (response.text or "").strip()

    if not text:
        raise LLMError("Gemini returned an empty response.")

    return text
