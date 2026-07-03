# Latest OneAgent 1.329.73 With OpenLLMetry 0.45.4

Scenario:

```text
Layer generation: latest
OneAgent: 1.329.73.20260123-140641
Layer ARN: arn:aws:lambda:us-east-1:585768157899:layer:Dynatrace_OneAgent_1_329_73_20260123-140641_python_x86:1

Lambdas:
- applyguardrail-test-lambda
- inline-guardrail-test-lambda

LangGraph: enabled
OpenLLMetry/Traceloop instrumentors: 0.45.4
Traceloop exporter: not used
Dynatrace OneAgent OTel bridge: DT_OPEN_TELEMETRY_ENABLE_INTEGRATION=true
Manual span attributes: none
Custom spans/decorators: none
```

Source exports:

```text
test-outputs\1.329_latest_applyguardrail_traceloop.csv
test-outputs\1.329_latest_inlineguardrail_traceloop.csv
```

Compared against:

```text
test-outputs\1.329_classic_applyguardrail_traceloop.csv
test-outputs\1.329_classic_inlineguardrail_traceloop.csv
```

## ApplyGuardrail Lambda

Latest `1.329.73` export:

```text
Rows: 14
Traces: 2
Span names:
- lambda_handler
- LangGraph.workflow
- applyguardrail_input.task
- should_call_model.task
- bedrock_model.task
- aws_bedrock.text_completion
- applyguardrail_output.task
- bedrock-runtime/applyguardrail
```

Classic `1.329.2` export for the same Lambda had:

```text
Rows: 15
Traces: 2
Span names:
- applyguardrail-test-lambda
- LangGraph.workflow
- applyguardrail_input.task
- should_call_model.task
- bedrock_model.task
- bedrock.completion
- applyguardrail_output.task
- POST
```

Latest layer changed native span naming:

- Lambda root span became `lambda_handler`.
- Bedrock model span became `aws_bedrock.text_completion`.
- Explicit guardrail calls became `bedrock-runtime/applyguardrail`.
- Generic `POST` spans were no longer present in the export.

Populated content attributes differed:

```text
Classic 1.329.2 ApplyGuardrail:
- gen_ai.prompt.0.content: 1
- gen_ai.completion.0.content: 1
- gen_ai.response.id: 1
- gen_ai.usage.prompt_tokens: 1
- gen_ai.usage.completion_tokens: 1
- llm.usage.total_tokens: 1

Latest 1.329.73 ApplyGuardrail:
- gen_ai.request.model: 1
- gen_ai.request.max_tokens: 1
- gen_ai.response.model: 1
```

So latest `1.329.73` preserved some native `gen_ai.*` model metadata, but did not expose prompt content, completion content, response id, or token usage in this CSV export.

## Inline Guardrail Lambda

Latest `1.329.73` export:

```text
Rows: 8
Traces: 2
Span names:
- lambda_handler
- LangGraph.workflow
- bedrock_inline_guardrail.task
- aws_bedrock.text_completion
```

Classic `1.329.2` export for the same Lambda had:

```text
Rows: 10
Traces: 2
Span names:
- inline-guardrail-test-lambda
- LangGraph.workflow
- bedrock_inline_guardrail.task
- bedrock.completion
- POST
```

Latest layer again changed native span naming:

- Lambda root span became `lambda_handler`.
- Bedrock model span became `aws_bedrock.text_completion`.
- Generic `POST` spans were no longer present in the export.

Populated content attributes differed:

```text
Classic 1.329.2 Inline:
- gen_ai.prompt.0.content: 2
- gen_ai.completion.0.content: 2
- gen_ai.response.id: 1
- gen_ai.usage.prompt_tokens: 1
- gen_ai.usage.completion_tokens: 1
- llm.usage.total_tokens: 1

Latest 1.329.73 Inline:
- gen_ai.request.model: 2
- gen_ai.request.max_tokens: 2
- gen_ai.response.model: 1
```

So latest `1.329.73` did not expose prompt/completion content for inline guardrail in this CSV export, even though classic `1.329.2` with the same OpenLLMetry code did.

## Traceloop Output Truncation

Both latest exports still had LangGraph/OpenLLMetry attributes:

```text
ApplyGuardrail:
- traceloop.entity.input: 8
- traceloop.entity.output: 8
- traceloop.entity.name: 8
- traceloop.span.kind: 8

Inline:
- traceloop.entity.input: 4
- traceloop.entity.output: 4
- traceloop.entity.name: 4
- traceloop.span.kind: 4
```

However, exported `traceloop.entity.output` fields were truncated in the CSV at `1000` characters and ended with an ellipsis character. This CSV export limit also affects classic-layer exports, so CSV files are not reliable for full long-attribute inspection.

User also observed a separate UI-level difference:

- Classic-layer `traceloop.entity.output` could be copied from the Dynatrace UI as complete JSON.
- A classic sample copied from the UI was saved to `local copied Dynatrace UI sample` and measured `8862` characters locally.
- The latest-layer `traceloop.entity.output` modal appeared truncated around `4096` characters and showed an incomplete string.
- This latest-layer UI truncation matches a similar observation from another monitored environment.

Working conclusion:

- Dynatrace notebook CSV export applies a `1000` character limit to long fields, regardless of layer generation.
- Latest-generation OneAgent appears to additionally cap or stringify long `traceloop.entity.output` values around `4096` characters in the Dynatrace UI.
- Classic OneAgent did not show this `4096` UI truncation in the user's copied sample.
- Full raw `traceloop.entity.output` should not be treated as reliably retrievable from latest-layer spans when the serialized LangGraph output is large.

## Conclusion

Latest-generation OneAgent `1.329.73` with OpenLLMetry `0.45.4` does produce LangGraph/OpenLLMetry spans, but it is not strictly better than classic `1.329.2` for this experiment.

Compared with classic `1.329.2` + OpenLLMetry:

- Latest has cleaner native Bedrock span names such as `aws_bedrock.text_completion` and `bedrock-runtime/applyguardrail`.
- Latest removed generic `POST` spans from these exports.
- Latest did not expose `gen_ai.prompt.0.content` or `gen_ai.completion.0.content` in the CSV exports.
- Latest `traceloop.entity.output` is subject to long-attribute truncation in the Dynatrace UI around `4096` characters, consistent with the other monitored-environment observation.
- Notebook CSV export truncates long fields around `1000` characters, so CSV is useful for attribute presence/counts but not full long JSON values.

For prompt/completion visibility, classic `1.329.2` + OpenLLMetry was better in these exports.

For native Bedrock span naming, latest `1.329.73` was better.
