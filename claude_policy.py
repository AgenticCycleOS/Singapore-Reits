"""Anthropic model policy and response handling for the 5.5 migration."""

HAIKU_MODEL = "claude-haiku-5-5"
SONNET_MODEL = "claude-sonnet-5-5"
ALLOWED_MODELS = frozenset({HAIKU_MODEL, SONNET_MODEL})


def request_options(model=SONNET_MODEL, *, effort="low", adaptive=False):
    """Validate the model before any API call; never enable model fallbacks."""
    if model not in ALLOWED_MODELS:
        raise ValueError(f"Anthropic model is outside the 5.5 policy: {model}")
    if effort not in {"low", "medium", "high"}:
        raise ValueError(f"Unsupported effort level: {effort}")
    thinking = "adaptive" if adaptive or model == HAIKU_MODEL else "between_tools"
    # extra_body supports SDK versions predating the new thinking/effort fields.
    return {
        "model": model,
        "extra_body": {
            "thinking": {"type": thinking},
            "output_config": {"effort": effort},
        },
    }


def response_text(response):
    """Return final text only; incomplete or unapproved responses use local fallback."""
    reason = getattr(response, "stop_reason", None)
    if reason is not None and reason != "end_turn":
        raise ValueError(f"Claude response is incomplete: {reason}")
    model = getattr(response, "model", None)
    if isinstance(model, str) and model not in ALLOWED_MODELS:
        raise ValueError(f"Claude response used an unapproved model: {model}")
    text = "\n".join(
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text" and block.text
    ).strip()
    if not text:
        raise ValueError("Claude response has no final text")
    return text
