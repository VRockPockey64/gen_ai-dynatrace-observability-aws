# Latest OneAgent 1.329.73 vs 1.339.55 With OpenLLMetry 0.45.4

Scenario:

```text
Layer generation: latest
Compared OneAgent versions:
- 1.329.73.20260123-140641
- 1.339.55.20260615-110349

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
test-outputs\1.339_latest_applyguardrail_traceloop.csv
test-outputs\1.339_latest_inlineguardrail_traceloop.csv
```

## ApplyGuardrail Lambda

Both latest `1.329.73` and latest `1.339.55` produced the same span shape:

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

The major difference was attribute preservation.

Latest `1.329.73` had:

```text
traceloop.entity.input: 8
traceloop.entity.output: 8
traceloop.entity.name: 8
traceloop.span.kind: 8
gen_ai.request.model: 1
gen_ai.request.max_tokens: 1
gen_ai.response.model: 1
```

Latest `1.339.55` had:

```text
traceloop.entity.input: 0
traceloop.entity.output: 0
traceloop.entity.name: 0
traceloop.span.kind: 0
gen_ai.request.model: 1
gen_ai.request.max_tokens: 1
gen_ai.response.model: 1
```

## Inline Guardrail Lambda

Both latest `1.329.73` and latest `1.339.55` produced the same span shape:

```text
Rows: 8
Traces: 2
Span names:
- lambda_handler
- LangGraph.workflow
- bedrock_inline_guardrail.task
- aws_bedrock.text_completion
```

Again, the major difference was attribute preservation.

Latest `1.329.73` had:

```text
traceloop.entity.input: 4
traceloop.entity.output: 4
traceloop.entity.name: 4
traceloop.span.kind: 4
gen_ai.request.model: 2
gen_ai.request.max_tokens: 2
gen_ai.response.model: 1
```

Latest `1.339.55` had:

```text
traceloop.entity.input: 0
traceloop.entity.output: 0
traceloop.entity.name: 0
traceloop.span.kind: 0
gen_ai.request.model: 2
gen_ai.request.max_tokens: 2
gen_ai.response.model: 2
```

## Conclusion

Latest-generation OneAgent `1.339.55` appears to preserve the OpenLLMetry/LangGraph span structure but drops the Traceloop entity attributes that were present in latest-generation OneAgent `1.329.73`.

This does not look like a Lambda code or configuration mistake:

- The same Lambda packages were used.
- `DT_OPEN_TELEMETRY_ENABLE_INTEGRATION=true` remained present.
- Both Lambdas used the latest-generation env style with `DT_CLUSTER`.
- The `1.339.55` layer ARN was valid and applied to both Lambdas.
- LangGraph spans still appeared, which means the OpenLLMetry/LangGraph instrumentation was still producing recognizable spans.

Working conclusion:

- Latest `1.329.73` + OpenLLMetry: LangGraph spans plus truncated `traceloop.entity.*` values.
- Latest `1.339.55` + OpenLLMetry: LangGraph spans but no exported `traceloop.entity.*` values.

For this experiment, latest `1.339.55` regressed Traceloop entity attribute visibility compared with latest `1.329.73`.
