from common.bedrock_chat import (
    DEFAULT_GUARDRAIL_ID,
    DEFAULT_GUARDRAIL_VERSION,
    compact_guardrail_result,
    env,
    invoke_claude,
    parse_event,
    response,
)


def lambda_handler(event, context):
    request = parse_event(event)

    model_result = invoke_claude(
        request["message"],
        request["max_tokens"],
        guardrail_id=env("GUARDRAIL_ID", DEFAULT_GUARDRAIL_ID),
        guardrail_version=env("GUARDRAIL_VERSION", DEFAULT_GUARDRAIL_VERSION),
    )

    raw = model_result["raw"]
    amazon_bedrock_guardrail = raw.get("amazon-bedrock-guardrailAction")
    trace = raw.get("amazon-bedrock-trace", {})

    return response(
        200,
        {
            "lambda": "inline-guardrail-test-lambda",
            "stage": "complete",
            "guardrail_action": amazon_bedrock_guardrail,
            "message": model_result["text"],
            "model_response": raw,
            "guardrail_trace": trace,
            "guardrail_assessment": compact_guardrail_result(trace) if isinstance(trace, dict) else {},
        },
    )
