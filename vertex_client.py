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

MODEL = "gemini-2.5-flash"


def generate(prompt: str) -> str:
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text
