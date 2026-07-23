import os
import time
import logging
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

logger = logging.getLogger("GeminiModel")

# Priority list of verified active models
MODEL_PRIORITY = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.0-flash"
]

def generate_agent_response(prompt: str, system_prompt: str = "") -> str:
    """
    Sends prompt to Gemini using retry per model and fallback strategy.
    """
    contents = f"{system_prompt}\n\n{prompt}".strip() if system_prompt else prompt
    
    last_error = None
    for model_name in MODEL_PRIORITY:
        for attempt in range(1, 4):  # Try up to 3 times per model
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                err_str = str(e)
                logger.warning(f"Attempt {attempt} failed for {model_name}: {err_str[:100]}")
                
                # If 503 or 429 transient error, wait before retry
                if "503" in err_str or "429" in err_str or "UNAVAILABLE" in err_str:
                    time.sleep(attempt * 2)
                    continue
                else:
                    # 404 or other permanent error -> break retry loop and try next model
                    break
            
    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")
