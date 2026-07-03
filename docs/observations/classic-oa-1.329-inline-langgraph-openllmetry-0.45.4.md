# Classic OneAgent 1.329.2 + LangGraph + OpenLLMetry 0.45.4 Inline Baseline

Scenario:

```text
Lambda: inline-guardrail-test-lambda
Guardrail mode: inline Bedrock guardrail config on invoke_model
Dynatrace layer generation: classic
OneAgent: 1.329.2.20251114-045249
Layer ARN: arn:aws:lambda:us-east-1:725887861453:layer:Dynatrace_OneAgent_1_329_2_20251114-045249_python:1
OpenTelemetry bridge: DT_OPEN_TELEMETRY_ENABLE_INTEGRATION=true
LangGraph: enabled
OpenLLMetry/Traceloop instrumentors: 0.45.4
Traceloop exporter: not used
Manual span attributes: none
Custom spans/decorators: none
```

Source exports:

```text
test-outputs\sampletest-with-langgraph-inline.csv
test-outputs\sampletest-with-langgraph-inline-updated.csv
```

The updated CSV includes `traceloop.entity.output` and should be treated as the primary export for this observation.

Repo-local raw copies:

```text
test-outputs\sampletest-with-langgraph-inline.csv
test-outputs\sampletest-with-langgraph-inline-updated.csv
```

## Observed Spans

Export summary:

```text
Rows: 5
Traces: 1
Telemetry SDK version: 1.329.2.20251114-045249
Span names:
- inline-guardrail-test-lambda
- LangGraph.workflow
- bedrock_inline_guardrail.task
- bedrock.completion
- POST
```

This is the first successful run where the trace shows both:

- LangGraph workflow/task spans.
- Bedrock GenAI span details.

## Traceloop Attributes

Populated Traceloop attributes:

```text
traceloop.span.kind
traceloop.entity.name
traceloop.entity.input
traceloop.entity.output
```

The earlier export also included these LangGraph association fields:

```text
traceloop.workflow.name
traceloop.association.properties.ls_integration
traceloop.association.properties.langgraph_node
traceloop.association.properties.langgraph_path
traceloop.association.properties.langgraph_triggers
traceloop.association.properties.langgraph_step
traceloop.association.properties.langgraph_checkpoint_ns
```

Observed from Dynatrace UI and CSV:

- `LangGraph.workflow` span has `traceloop.span.kind=workflow`.
- `bedrock_inline_guardrail.task` span has `traceloop.span.kind=task`.
- `traceloop.entity.input` includes the LangGraph state input.
- `traceloop.entity.output` includes the model result, model text, raw Bedrock response, and inline guardrail trace details.

From the updated CSV:

```text
traceloop.entity.output populated on:
- LangGraph.workflow
- bedrock_inline_guardrail.task

traceloop.entity.output was not populated on:
- inline-guardrail-test-lambda
- bedrock.completion
- POST
```

The output attribute was long enough that the CSV export truncates it around 1000 characters, but the included portion confirms it contains:

```text
model_result.text
model_result.raw.model
model_result.raw.id
model_result.raw.content[0].text
model_result.raw.usage
model_result.raw.amazon-bedrock-trace.guardrail
guardrail content policy filter results
guardrail sensitive information policy results
guardrail invocation metrics
applied guardrail details
```

Privacy note:

```text
This setup can capture prompt text, completion text, and raw guardrail details.
That is useful for this experiment, but it is sensitive telemetry and should be reviewed before any production-like use.
```

## GenAI Attributes

Populated GenAI attributes appeared on the `bedrock.completion` span:

```text
gen_ai.prompt.0.role
gen_ai.prompt.0.content
gen_ai.completion.0.content
gen_ai.response.model
gen_ai.response.id
gen_ai.request.model
gen_ai.request.max_tokens
gen_ai.usage.prompt_tokens
gen_ai.usage.completion_tokens
gen_ai.system
llm.request.type
llm.usage.total_tokens
```

This is materially better than the no-OpenLLMetry classic tests, where no `gen_ai.*` attributes were populated.

## Conclusion

This is the current best working setup for the internal baseline scenario:

```text
Classic Dynatrace layer
+ OneAgent 1.329.2
+ DT_OPEN_TELEMETRY_ENABLE_INTEGRATION=true
+ LangGraph wrapper
+ OpenLLMetry/Traceloop instrumentors 0.45.4
+ no Traceloop exporter
+ no separate Dynatrace OTLP ingest token
```

Results:

- LangGraph spans are visible.
- LangGraph workflow/task attributes are visible.
- Bedrock completion is visible as a GenAI span.
- Prompt and completion content are captured.
- Inline guardrail details are present in Traceloop entity output.
- Dynatrace OneAgent remains the trace export path.
