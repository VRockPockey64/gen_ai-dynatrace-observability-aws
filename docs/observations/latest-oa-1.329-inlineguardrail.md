# Latest Dynatrace Layer + OneAgent 1.329.73 + Inline Guardrail Lambda

Scenario:

```text
Lambda: inline-guardrail-test-lambda
Dynatrace layer generation: latest
OneAgent: 1.329.73.20260123-140641
Layer ARN: arn:aws:lambda:us-east-1:585768157899:layer:Dynatrace_OneAgent_1_329_73_20260123-140641_python_x86:1
Traceloop: not installed
Manual span attributes: none
Lambda code changes for observability: none
```

Source export:

```text
test-outputs\1.329_latest_inlineguardrail.csv
```

## Observed Spans

Three prompt paths were captured:

1. Safe prompt
2. Email input block
3. Output email anonymization

Observed span pattern for all three:

```text
lambda_handler
aws_bedrock.text_completion
```

Unlike the explicit `ApplyGuardrail` Lambda, inline guardrail invocation did not create separate `bedrock-runtime/applyguardrail` spans. Guardrail metadata appeared on the `aws_bedrock.text_completion` span.

## gen_ai Attribute Findings

`aws_bedrock.text_completion` spans contained standard LLM attributes:

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

For the input-blocked case, the span did not include token usage or finish reason because the guardrail intervened before normal model completion.

Inline guardrail-specific attributes were present:

```text
gen_ai.guardrail.id
gen_ai.guardrail.input.latency
gen_ai.guardrail.output.latency
gen_ai.guardrail.input.sensitive_information.piis
gen_ai.guardrail.output.sensitive_information.piis
```

Observed examples:

```text
gen_ai.guardrail.id = e3uve6f999od
gen_ai.guardrail.input.sensitive_information.piis = EMAIL
gen_ai.guardrail.output.sensitive_information.piis = EMAIL
```

Prompt/completion content attributes were not present:

```text
gen_ai.prompt.0.content
gen_ai.completion.0.content
```

## Baseline Conclusion

With latest-generation Dynatrace Lambda layer and OneAgent `1.329.73`, without Traceloop and without manual instrumentation:

- Inline Bedrock guardrail invocation is recognized as part of the GenAI `aws_bedrock.text_completion` span.
- Dynatrace captures guardrail ID.
- Dynatrace captures guardrail input/output latency.
- Dynatrace captures PII category for input and output sensitive-information interventions.
- Prompt and completion text are not captured.
- Inline guardrail provides richer guardrail metadata than explicit `ApplyGuardrail` calls in this OneAgent version.
