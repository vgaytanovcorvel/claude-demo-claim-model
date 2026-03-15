from collections.abc import Callable

from google.genai import types

from models.claim_state_delta import ClaimStateDelta
from prompt_telemetry import log_prompt_request, log_prompt_response
from vertex_client import MODEL, client


def _extract_response_text(response: types.GenerateContentResponse) -> str | None:
    """Extract all model text from AFC history and the final response."""
    text_parts: list[str] = []

    if response.automatic_function_calling_history:
        for content in response.automatic_function_calling_history:
            if content.role == "model" and content.parts:
                for part in content.parts:
                    if part.text:
                        text_parts.append(part.text)

    if response.text:
        text_parts.append(response.text)

    return "\n".join(text_parts) if text_parts else None


def run_tool_loop(
    system_prompt: str,
    user_message: str,
    tools: list[Callable],
    delta: ClaimStateDelta,
) -> ClaimStateDelta:
    """Run a Gemini generate_content call with automatic function calling."""
    log_prompt_request(
        system_prompt=system_prompt,
        user_message=user_message,
        model=MODEL,
        tools=[t.__name__ for t in tools],
    )
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
    log_prompt_response(
        response_text=_extract_response_text(response),
        model=MODEL,
    )
    return delta
