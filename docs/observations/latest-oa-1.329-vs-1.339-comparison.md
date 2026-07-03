# Latest Dynatrace Layer: OneAgent 1.329.73 vs 1.339.55

Compared exports:

```text
test-outputs/1.329_latest_applyguardrail.csv
test-outputs/1.329_latest_inlineguardrail.csv
test-outputs/1.339_latest_applyguardrail.csv
test-outputs/1.339_latest_inlineguardrail.csv
```

Common test setup:

```text
Dynatrace layer generation: latest
Traceloop: not installed
Manual span attributes: none
Lambda code changes for observability: none
Model profile: us.anthropic.claude-haiku-4-5-20251001-v1:0
Guardrail ID: e3uve6f999od
```

Prompt paths:

1. Safe prompt
2. Email input block
3. Output email anonymization

## Summary Table

| Scenario | Span pattern | LLM gen_ai attributes | Guardrail gen_ai attributes | Prompt/completion content |
| --- | --- | --- | --- | --- |
| 1.329 latest + explicit ApplyGuardrail | `lambda_handler`, `bedrock-runtime/applyguardrail`, `aws_bedrock.text_completion` | Yes, only on `aws_bedrock.text_completion` | No | No |
| 1.329 latest + inline guardrail | `lambda_handler`, `aws_bedrock.text_completion` | Yes | Yes, on `aws_bedrock.text_completion` | No |
| 1.339 latest + explicit ApplyGuardrail | `lambda_handler`, `bedrock-runtime/applyguardrail`, `aws_bedrock.text_completion` | Yes, only on `aws_bedrock.text_completion` | No populated values | No |
| 1.339 latest + inline guardrail | `lambda_handler`, `aws_bedrock.text_completion` | Yes | Yes, on `aws_bedrock.text_completion` | No |

## Explicit ApplyGuardrail Path

Both OneAgent versions captured explicit guardrail calls as AWS client spans:

```text
bedrock-runtime/applyguardrail
```

Both versions captured the model invocation as:

```text
aws_bedrock.text_completion
```

For both `1.329.73` and `1.339.55`, the explicit `ApplyGuardrail` spans did not receive populated `gen_ai.*` attributes.

The `1.339.55` export included guardrail columns because the DQL query explicitly selected them with `fields`, not because those attributes were present on the spans:

```text
gen_ai.guardrail.id
gen_ai.guardrail.input.latency
gen_ai.guardrail.input.sensitive_information.piis
gen_ai.guardrail.output.latency
gen_ai.guardrail.output.sensitive_information.piis
```

Those guardrail columns had no populated values in the explicit ApplyGuardrail export, and the Distributed Traces app also showed no `gen_ai.*` attributes on `bedrock-runtime/applyguardrail` spans.

Conclusion:

```text
No meaningful improvement from 1.329.73 to 1.339.55 for explicit ApplyGuardrail calls.
```

## Inline Guardrail Path

Both OneAgent versions represented inline guardrail invocation as:

```text
aws_bedrock.text_completion
```

Both versions populated standard LLM attributes:

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

Both versions populated inline guardrail attributes:

```text
gen_ai.guardrail.id
gen_ai.guardrail.input.latency
gen_ai.guardrail.output.latency
gen_ai.guardrail.input.sensitive_information.piis
gen_ai.guardrail.output.sensitive_information.piis
```

Observed guardrail values:

```text
gen_ai.guardrail.id = e3uve6f999od
gen_ai.guardrail.input.sensitive_information.piis = EMAIL
gen_ai.guardrail.output.sensitive_information.piis = EMAIL
```

Small observed difference:

- In the inline blocked-input case, `1.339.55` populated `gen_ai.response.model` for all three GenAI spans.
- In the same path, `1.329.73` populated `gen_ai.response.model` for two out of three GenAI spans.

This is a minor metadata improvement, not a prompt/guardrail breakthrough.

## Prompt And Completion Content

None of the four exports contained prompt or completion content columns such as:

```text
gen_ai.prompt.0.content
gen_ai.completion.0.content
```

Conclusion:

```text
Neither latest-layer OneAgent 1.329.73 nor 1.339.55 captures prompt/completion text by default in this setup.
```

## Overall Conclusion

For latest-generation Dynatrace Lambda layers without Traceloop and without manual instrumentation:

- Inline guardrail invocation gives much richer guardrail metadata than explicit `ApplyGuardrail` calls.
- Explicit `ApplyGuardrail` calls are visible as AWS Bedrock Runtime client spans, but not as GenAI-enriched spans.
- Upgrading from OneAgent `1.329.73` to `1.339.55` does not improve prompt visibility or explicit ApplyGuardrail enrichment in this test.
- Prompt and completion content are absent in both versions.

Next useful test:

```text
Classic Lambda layer 1.329.2 / 1.331.3, still no Traceloop, to compare classic vs latest-generation layer behavior.
```
