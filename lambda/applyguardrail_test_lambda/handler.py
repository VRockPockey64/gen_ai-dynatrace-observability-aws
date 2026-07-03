from common.bedrock_chat import (
    apply_guardrail,
    compact_guardrail_result,
    guardrail_output_text,
    invoke_claude,
    parse_event,
    response,
)


def lambda_handler(event, context):
    request = parse_event(event)
    user_message = request["message"]

    input_guardrail = apply_guardrail("INPUT", user_message)
    if input_guardrail.get("action") == "GUARDRAIL_INTERVENED":
        return response(
            200,
            {
                "lambda": "applyguardrail-test-lambda",
                "stage": "input_guardrail",
                "blocked": True,
                "message": guardrail_output_text(input_guardrail, "Input blocked by guardrail."),
                "input_guardrail": compact_guardrail_result(input_guardrail),
            },
        )

    model_result = invoke_claude(user_message, request["max_tokens"])
    model_text = model_result["text"]

    output_guardrail = apply_guardrail("OUTPUT", model_text)
    final_text = guardrail_output_text(output_guardrail, model_text)

    return response(
        200,
        {
            "lambda": "applyguardrail-test-lambda",
            "stage": "complete",
            "blocked": output_guardrail.get("action") == "GUARDRAIL_INTERVENED",
            "message": final_text,
            "model_text": model_text,
            "input_guardrail": compact_guardrail_result(input_guardrail),
            "output_guardrail": compact_guardrail_result(output_guardrail),
            "model_response": model_result["raw"],
        },
    )
