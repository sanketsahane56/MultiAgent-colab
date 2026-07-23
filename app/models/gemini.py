import os
import time
import logging
from dotenv import load_dotenv
from google import genai

load_dotenv()

logger = logging.getLogger("GeminiModel")

# Priority list of active official Google Gemini models
MODEL_PRIORITY = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-8b"
]

def get_gemini_client():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing Gemini API Key. Please set GOOGLE_API_KEY or GEMINI_API_KEY in your environment / Vercel settings.")
    return genai.Client(api_key=api_key)

def generate_agent_response(prompt: str, system_prompt: str = "") -> str:
    """
    Sends prompt to Gemini using retry per model and fallback strategy.
    """
    contents = f"{system_prompt}\n\n{prompt}".strip() if system_prompt else prompt
    client = get_gemini_client()
    
    collected_errors = []
    for model_name in MODEL_PRIORITY:
        for attempt in range(1, 3):  # Try up to 2 times per model
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                err_str = str(e)
                logger.warning(f"Attempt {attempt} failed for {model_name}: {err_str[:150]}")
                collected_errors.append(f"[{model_name} attempt {attempt}]: {err_str[:150]}")
                
                # If invalid key / unauthenticated, fail early with clear guidance
                if "401" in err_str or "UNAUTHENTICATED" in err_str:
                    raise RuntimeError(
                        "Invalid or Unauthorized GOOGLE_API_KEY. "
                        "Please get a valid Gemini API Key from https://aistudio.google.com/app/apikey "
                        "and set it in your .env file or Vercel Environment Variables."
                    ) from e

                # If 503 or 429 transient error, wait before retry
                if "503" in err_str or "429" in err_str or "UNAVAILABLE" in err_str:
                    time.sleep(attempt * 2)
                    continue
                else:
                    # Permanent error for this model -> break inner loop to try next model
                    break
            
    raise RuntimeError(f"All Gemini models failed. Errors: {'; '.join(collected_errors)}")

