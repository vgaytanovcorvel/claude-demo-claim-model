from collections.abc import Callable

from google.genai import types

from models.claim_state_delta import ClaimStateDelta
from vertex_client import MODEL, client


def run_tool_loop(
    system_prompt: str,
    user_message: str,
    tools: list[Callable],
    delta: ClaimStateDelta,
) -> ClaimStateDelta:
    """Run a Gemini generate_content call with automatic function calling."""
    client.models.generate_content(
        model=MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False,
            ),
        ),
    )
    return delta
