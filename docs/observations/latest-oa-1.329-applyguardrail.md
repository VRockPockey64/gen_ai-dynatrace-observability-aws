# Latest Dynatrace Layer + OneAgent 1.329.73 + ApplyGuardrail Lambda

Scenario:

```text
Lambda: applyguardrail-test-lambda
Dynatrace layer generation: latest
OneAgent: 1.329.73.20260123-140641
Layer ARN: arn:aws:lambda:us-east-1:585768157899:layer:Dynatrace_OneAgent_1_329_73_20260123-140641_python_x86:1
Traceloop: not installed
Manual span attributes: none
Lambda code changes for observability: none
```

Source export:

```text
test-outputs\1.329_latest_applyguardrail.csv
```

## Observed Spans

Three prompt paths were captured:

1. Safe prompt
2. Output email anonymization
3. Email input block

Observed span pattern:

```text
lambda_handler
bedrock-runtime/applyguardrail
aws_bedrock.text_completion
bedrock-runtime/applyguardrail
```

For the blocked-input case, the Lambda returned after the first `ApplyGuardrail` call:

```text
lambda_handler
bedrock-runtime/applyguardrail
```

## gen_ai Attribute Findings

`aws_bedrock.text_completion` spans contained:

```text
gen_ai.operation.name
gen_ai.provider.name
gen_ai.request.max_tokens
gen_ai.request.model
gen_ai.response.finish_reasons
gen_ai.response.model
gen_ai.usage.input_tokens
gen_ai.usage.output_tokens
```

Observed values included:

```text
gen_ai.operation.name = text_completion
gen_ai.provider.name = aws_bedrock
gen_ai.request.model = us.anthropic.claude-haiku-4-5-20251001-v1:0
gen_ai.response.model = claude-haiku-4-5-20251001
```

`bedrock-runtime/applyguardrail` spans did not contain `gen_ai.*` attributes.

Prompt/completion content attributes were not present:

```text
gen_ai.prompt.0.content
gen_ai.completion.0.content
```

## Baseline Conclusion

With latest-generation Dynatrace Lambda layer and OneAgent `1.329.73`, without Traceloop and without manual instrumentation:

- Bedrock `InvokeModel` is recognized as a GenAI operation.
- Bedrock `ApplyGuardrail` is captured as an AWS Bedrock Runtime client span, but not as a GenAI span.
- Token counts are captured for the LLM call.
- Model request/response identifiers are captured for the LLM call.
- Prompt and completion text are not captured.
- Guardrail intervention/masking details are not visible as `gen_ai.*` attributes.
