from collections.abc import Callable

from google.genai import types

from models.claim_state_delta import ClaimStateDelta
from prompt_telemetry import log_prompt
from vertex_client import MODEL, client


def run_tool_loop(
    system_prompt: str,
    user_message: str,
    tools: list[Callable],
    delta: ClaimStateDelta,
) -> ClaimStateDelta:
    """Run a Gemini generate_content call with automatic function calling."""
    response = client.models.generate_content(
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
    log_prompt(
        system_prompt=system_prompt,
        user_message=user_message,
        response_text=response.text if response.text else None,
        model=MODEL,
        tools=[t.__name__ for t in tools],
    )
    return delta
