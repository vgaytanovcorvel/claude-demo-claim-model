import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

_PROJECT = os.environ["VERTEX_PROJECT"]
_LOCATION = os.environ.get("VERTEX_LOCATION", "us-central1")

client = genai.Client(
    vertexai=True,
    project=_PROJECT,
    location=_LOCATION,
)

MODEL = "gemini-2.5-pro"


def generate(prompt: str) -> str:
    from prompt_telemetry import log_prompt_request, log_prompt_response

    log_prompt_request(user_message=prompt, model=MODEL)
    response = client.models.generate_content(model=MODEL, contents=prompt)
    log_prompt_response(response_text=response.text, model=MODEL)
    return response.text
