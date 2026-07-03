import os
from typing import Any, Dict, TypedDict

os.environ.setdefault("TRACELOOP_TELEMETRY", "false")

from opentelemetry.instrumentation.bedrock import BedrockInstrumentor
from opentelemetry.instrumentation.langchain import LangchainInstrumentor

BedrockInstrumentor(enrich_token_usage=False, use_legacy_attributes=True).instrument()
LangchainInstrumentor(use_legacy_attributes=True).instrument()

from langgraph.graph import END, StateGraph

from common.bedrock_chat import (
    DEFAULT_GUARDRAIL_ID,
    DEFAULT_GUARDRAIL_VERSION,
    compact_guardrail_result,
    env,
    invoke_claude,
    parse_event,
    response,
)


class ChatState(TypedDict):
    message: str
    max_tokens: int
    model_result: Dict[str, Any]


def call_bedrock_inline_guardrail(state: ChatState) -> Dict[str, Any]:
    model_result = invoke_claude(
        state["message"],
        state["max_tokens"],
        guardrail_id=env("GUARDRAIL_ID", DEFAULT_GUARDRAIL_ID),
        guardrail_version=env("GUARDRAIL_VERSION", DEFAULT_GUARDRAIL_VERSION),
    )

    return {"model_result": model_result}


def build_graph():
    graph = StateGraph(ChatState)
    graph.add_node("bedrock_inline_guardrail", call_bedrock_inline_guardrail)
    graph.set_entry_point("bedrock_inline_guardrail")
    graph.add_edge("bedrock_inline_guardrail", END)
    return graph.compile()


chat_graph = build_graph()


def lambda_handler(event, context):
    request = parse_event(event)
    graph_result = chat_graph.invoke(
        {
            "message": request["message"],
            "max_tokens": request["max_tokens"],
        }
    )
    model_result = graph_result["model_result"]
    raw = model_result["raw"]
    amazon_bedrock_guardrail = raw.get("amazon-bedrock-guardrailAction")
    trace = raw.get("amazon-bedrock-trace", {})

    return response(
        200,
        {
            "lambda": "inline-guardrail-test-lambda",
            "execution_engine": "langgraph",
            "instrumentation": "traceloop-openllmetry",
            "span_exporter": "dynatrace-oneagent",
            "graph_nodes": ["bedrock_inline_guardrail"],
            "stage": "complete",
            "guardrail_action": amazon_bedrock_guardrail,
            "message": model_result["text"],
            "model_response": raw,
            "guardrail_trace": trace,
            "guardrail_assessment": compact_guardrail_result(trace) if isinstance(trace, dict) else {},
        },
    )
