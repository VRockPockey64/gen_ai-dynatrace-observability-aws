# Classic OneAgent 1.329.2 + OpenLLMetry 0.45.4: ApplyGuardrail vs Inline Two-Prompt Run

Scenario:

```text
Lambdas:
- applyguardrail-test-lambda
- inline-guardrail-test-lambda

Dynatrace layer generation: classic
OneAgent: 1.329.2.20251114-045249
OpenTelemetry bridge: DT_OPEN_TELEMETRY_ENABLE_INTEGRATION=true
LangGraph: enabled on both Lambdas
OpenLLMetry/Traceloop instrumentors: 0.45.4
Traceloop exporter: not used
Manual span attributes: none
Custom spans/decorators: none
```

Source exports:

```text
test-outputs\1.329_classic_applyguardrail_traceloop.csv
test-outputs\1.329_classic_inlineguardrail_traceloop.csv
```

Repo-local raw copies:

```text
test-outputs\1.329_classic_applyguardrail_traceloop.csv
test-outputs\1.329_classic_inlineguardrail_traceloop.csv
```

Prompts:

```text
Safe:
Explain AWS Lambda in one short sentence.

Combined email + hate:
My email is test@example.com. I hate Canadians; they are disgusting and should be excluded from society.
```

## ApplyGuardrail Lambda

Export summary:

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

Trace shape:

```text
Blocked input trace:
- applyguardrail-test-lambda
- LangGraph.workflow
- applyguardrail_input.task
- POST
- should_call_model.task

Safe trace:
- applyguardrail-test-lambda
- LangGraph.workflow
- applyguardrail_input.task
- POST
- should_call_model.task
- bedrock_model.task
- bedrock.completion
- POST
- applyguardrail_output.task
- POST
```

Attribute findings:

```text
traceloop.entity.input populated on 8 rows
traceloop.entity.output populated on 8 rows
traceloop.entity.name populated on 8 rows
traceloop.span.kind populated on 8 rows
```

GenAI attributes appeared only for the safe trace model call:

```text
gen_ai.prompt.0.role
gen_ai.prompt.0.content
gen_ai.completion.0.content
gen_ai.request.model
gen_ai.request.max_tokens
gen_ai.response.model
gen_ai.response.id
gen_ai.usage.prompt_tokens
gen_ai.usage.completion_tokens
llm.usage.total_tokens
```

Blocked combined-policy trace:

- The graph stops after input guardrail evaluation.
- No model call occurs.
- No `bedrock.completion` GenAI span appears for the blocked input.
- `applyguardrail_input.task` output contains the explicit `ApplyGuardrail` result.
- The CSV confirms HATE content policy details in `applyguardrail_input.task` output:
  - `type=HATE`
  - `confidence=HIGH`
  - `action=BLOCKED`
  - `detected=true`
- The input text includes `test@example.com`, but the CSV export truncates long `traceloop.entity.output` fields, so the visible snippet is less convenient for confirming EMAIL from the exported CSV alone.

## Inline Guardrail Lambda

Export summary:

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

Each inline trace has the same 5-span shape.

Attribute findings:

```text
traceloop.entity.input populated on 4 rows
traceloop.entity.output populated on 4 rows
traceloop.entity.name populated on 4 rows
traceloop.span.kind populated on 4 rows
```

GenAI attributes appeared on both inline `bedrock.completion` spans:

```text
gen_ai.prompt.0.role
gen_ai.prompt.0.content
gen_ai.request.model
gen_ai.request.max_tokens
gen_ai.completion.0.content
```

Additional GenAI usage/response attributes appeared on the safe trace:

```text
gen_ai.response.model
gen_ai.response.id
gen_ai.usage.prompt_tokens
gen_ai.usage.completion_tokens
llm.usage.total_tokens
```

Blocked combined-policy trace:

- Inline guardrail still appears through the `bedrock.completion` span.
- `bedrock.completion` includes the blocked prompt in `gen_ai.prompt.0.content`.
- `bedrock.completion` includes the blocked response in `gen_ai.completion.0.content`.
- `bedrock_inline_guardrail.task` output contains guardrail details.
- The CSV confirms both policy families in the inline blocked trace:
  - HATE content policy with `confidence=HIGH`, `action=BLOCKED`, `detected=true`.
  - EMAIL sensitive information policy details are present in `bedrock_inline_guardrail.task` output.

## Comparison

ApplyGuardrail explicit mode:

- Gives clear LangGraph task boundaries for input guardrail, decision, model call, and output guardrail.
- On blocked input, it short-circuits before the model call.
- The blocked input trace has no `bedrock.completion` GenAI span because no model invoke happens.
- Guardrail details live in LangGraph task output for the explicit `ApplyGuardrail` call.

Inline guardrail mode:

- Keeps a consistent trace shape for safe and blocked prompts.
- Produces a `bedrock.completion` span even when the guardrail blocks the request.
- Exposes prompt/completion content on the blocked `bedrock.completion` span.
- Places guardrail details inside the LangGraph task output from the Bedrock model call response.

## Conclusion

Both Lambdas now show useful LangGraph/OpenLLMetry spans under classic OneAgent `1.329.2`.

Inline guardrail is easier to inspect for blocked GenAI prompt/response attributes because the blocked prompt still produces a `bedrock.completion` span.

Explicit ApplyGuardrail is better for separating the guardrail workflow stages, but blocked inputs stop before any model span, so blocked-prompt GenAI details are represented through LangGraph task attributes rather than a `bedrock.completion` span.
