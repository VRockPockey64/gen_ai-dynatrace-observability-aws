import os
from typing import Any, Dict, TypedDict

os.environ.setdefault("TRACELOOP_TELEMETRY", "false")

from opentelemetry.instrumentation.bedrock import BedrockInstrumentor
from opentelemetry.instrumentation.langchain import LangchainInstrumentor

BedrockInstrumentor(enrich_token_usage=False, use_legacy_attributes=True).instrument()
LangchainInstrumentor(use_legacy_attributes=True).instrument()

from langgraph.graph import END, StateGraph

from common.bedrock_chat import (
    apply_guardrail,
    compact_guardrail_result,
    guardrail_output_text,
    invoke_claude,
    parse_event,
    response,
)


class ChatState(TypedDict, total=False):
    message: str
    max_tokens: int
    input_guardrail: Dict[str, Any]
    model_result: Dict[str, Any]
    output_guardrail: Dict[str, Any]
    final_text: str


def run_input_guardrail(state: ChatState) -> Dict[str, Any]:
    return {"input_guardrail": apply_guardrail("INPUT", state["message"])}


def should_call_model(state: ChatState) -> str:
    if state["input_guardrail"].get("action") == "GUARDRAIL_INTERVENED":
        return "blocked"
    return "model"


def call_bedrock_model(state: ChatState) -> Dict[str, Any]:
    return {"model_result": invoke_claude(state["message"], state["max_tokens"])}


def run_output_guardrail(state: ChatState) -> Dict[str, Any]:
    model_text = state["model_result"]["text"]
    output_guardrail = apply_guardrail("OUTPUT", model_text)
    return {
        "output_guardrail": output_guardrail,
        "final_text": guardrail_output_text(output_guardrail, model_text),
    }


def build_graph():
    graph = StateGraph(ChatState)
    graph.add_node("applyguardrail_input", run_input_guardrail)
    graph.add_node("bedrock_model", call_bedrock_model)
    graph.add_node("applyguardrail_output", run_output_guardrail)
    graph.set_entry_point("applyguardrail_input")
    graph.add_conditional_edges(
        "applyguardrail_input",
        should_call_model,
        {
            "blocked": END,
            "model": "bedrock_model",
        },
    )
    graph.add_edge("bedrock_model", "applyguardrail_output")
    graph.add_edge("applyguardrail_output", END)
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

    input_guardrail = graph_result["input_guardrail"]
    if input_guardrail.get("action") == "GUARDRAIL_INTERVENED":
        return response(
            200,
            {
                "lambda": "applyguardrail-test-lambda",
                "execution_engine": "langgraph",
                "instrumentation": "traceloop-openllmetry",
                "span_exporter": "dynatrace-oneagent",
                "graph_nodes": ["applyguardrail_input", "bedrock_model", "applyguardrail_output"],
                "stage": "input_guardrail",
                "blocked": True,
                "message": guardrail_output_text(input_guardrail, "Input blocked by guardrail."),
                "input_guardrail": compact_guardrail_result(input_guardrail),
            },
        )

    model_result = graph_result["model_result"]
    model_text = model_result["text"]
    output_guardrail = graph_result["output_guardrail"]
    final_text = graph_result["final_text"]

    return response(
        200,
        {
            "lambda": "applyguardrail-test-lambda",
            "execution_engine": "langgraph",
            "instrumentation": "traceloop-openllmetry",
            "span_exporter": "dynatrace-oneagent",
            "graph_nodes": ["applyguardrail_input", "bedrock_model", "applyguardrail_output"],
            "stage": "complete",
            "blocked": output_guardrail.get("action") == "GUARDRAIL_INTERVENED",
            "message": final_text,
            "model_text": model_text,
            "input_guardrail": compact_guardrail_result(input_guardrail),
            "output_guardrail": compact_guardrail_result(output_guardrail),
            "model_response": model_result["raw"],
        },
    )
