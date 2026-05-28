# Researcher agent — generation step of the Self-Refine loop.
# Runs tool calls until it submits a structured answer via `submit_research_answer`.

import json
from typing import Optional

import anthropic
from dotenv import load_dotenv

from src.tools.fred_tool import fetch_series, get_series_info
from src.tools.search_tool import web_search

load_dotenv()

SYSTEM_PROMPT = """You are a macroeconomic research analyst investigating a question using \
real FRED data and web sources.

Pull the relevant series, look at actual numbers, and build an argument from evidence — \
not from priors. Cite specific values and dates. If you're uncertain, say so rather than \
papering over it. When you have enough to make a defensible claim, call `submit_research_answer`.

Scope discipline is mandatory. If the research question names a time period, event window, \
or comparison window, make that window the basis of the main claim. You may mention later \
data only as a clearly labeled outside-scope caveat, and later data must not change the \
verdict about the period the user asked you to evaluate.

If you receive critic feedback at the start of this task, you are in revision mode. \
Don't restart the full investigation — focus specifically on the weaknesses flagged. \
Pull only the data needed to address them, then resubmit with the corrections. If critic \
feedback asks you to broaden beyond the original question's time window, treat that as \
out of scope and re-anchor the answer to the original question instead.
"""

TOOLS = [
    {
        "name": "fetch_fred_series",
        "description": (
            "Fetch a FRED time series by ID. Returns chronological date/value pairs. "
            "Common IDs: CPIAUCSL (CPI), PCEPILFE (core PCE), UNRATE (unemployment), "
            "FEDFUNDS (fed funds rate), GDPC1 (real GDP), T10Y2Y (yield curve spread), "
            "M2SL (M2 money supply), AHETPI (avg hourly earnings), USREC (NBER recession), "
            "PAYEMS (nonfarm payroll), CEU7000000001 (leisure & hospitality employment), "
            "CEU6000000001 (professional & business services employment)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "series_id": {"type": "string", "description": "FRED series ID"},
                "start_date": {"type": "string", "description": "YYYY-MM-DD (optional)"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD (optional)"},
            },
            "required": ["series_id"],
        },
    },
    {
        "name": "get_fred_series_info",
        "description": "Get metadata for a FRED series: title, frequency, units.",
        "input_schema": {
            "type": "object",
            "properties": {
                "series_id": {"type": "string"},
            },
            "required": ["series_id"],
        },
    },
    {
        "name": "web_search",
        "description": "Search the web for context, recent analysis, or research papers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "submit_research_answer",
        "description": (
            "Submit your structured final answer once you have gathered and analyzed "
            "sufficient evidence. This ends the research phase."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "description": "Your main finding in 1–2 sentences.",
                },
                "confidence": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                },
                "evidence_summary": {
                    "type": "string",
                    "description": "Specific data points and sources supporting your claim.",
                },
                "rationale": {
                    "type": "string",
                    "description": "Full reasoning chain connecting evidence to claim.",
                },
                "open_questions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "What remains uncertain or unresolved.",
                },
            },
            "required": ["claim", "confidence", "evidence_summary", "rationale", "open_questions"],
        },
    },
]


def _dispatch(name: str, inputs: dict) -> str:
    if name == "fetch_fred_series":
        result = fetch_series(
            inputs["series_id"],
            inputs.get("start_date"),
            inputs.get("end_date"),
        )
    elif name == "get_fred_series_info":
        result = get_series_info(inputs["series_id"])
    elif name == "web_search":
        result = web_search(inputs["query"])
    else:
        result = {"error": f"Unknown tool: {name}"}
    return json.dumps(result)


class ResearchAgent:

    def __init__(
        self,
        model: str = "claude-opus-4-7",
        max_tokens: int = 4096,
        max_tool_calls: int = 20,
    ):
        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens
        self.max_tool_calls = max_tool_calls

    def investigate(
        self,
        question: str,
        memory_context: Optional[str] = None,
        critic_feedback: Optional[str] = None,
    ) -> dict:
        system = SYSTEM_PROMPT
        if memory_context:
            system += (
                "\n\nRelevant prior research attempts — learn from these, "
                "do not repeat dead ends. These memories are subordinate to "
                "the current question's exact scope and time window:\n" + memory_context
            )

        user_content = f"Research question: {question}"
        if critic_feedback:
            user_content += (
                f"\n\nPrevious critic feedback to address in this revision:\n{critic_feedback}"
            )

        messages = [{"role": "user", "content": user_content}]
        tool_call_count = 0
        token_usage = {"input_tokens": 0, "output_tokens": 0}

        while tool_call_count < self.max_tool_calls:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                tools=TOOLS,
                messages=messages,
            )

            token_usage["input_tokens"] += response.usage.input_tokens
            token_usage["output_tokens"] += response.usage.output_tokens

            for block in response.content:
                if block.type == "tool_use" and block.name == "submit_research_answer":
                    return {
                        "answer": block.input,
                        "tool_calls": tool_call_count,
                        "token_usage": token_usage,
                    }

            if response.stop_reason != "tool_use":
                # Model stopped without a structured submission — wrap raw text
                text = " ".join(
                    b.text for b in response.content if hasattr(b, "text")
                )
                return {
                    "answer": {
                        "claim": text[:500],
                        "confidence": "low",
                        "evidence_summary": "Agent stopped without a structured submission.",
                        "rationale": text,
                        "open_questions": [],
                    },
                    "tool_calls": tool_call_count,
                    "token_usage": token_usage,
                }

            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use" and block.name != "submit_research_answer":
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": _dispatch(block.name, block.input),
                    })
                    tool_call_count += 1
            messages.append({"role": "user", "content": tool_results})

        return {
            "answer": {
                "claim": "Max tool calls reached without convergence.",
                "confidence": "low",
                "evidence_summary": "Exceeded tool call limit.",
                "rationale": "Agent did not converge within the allowed number of tool calls.",
                "open_questions": ["Increase max_tool_calls or narrow the question scope."],
            },
            "tool_calls": tool_call_count,
            "token_usage": token_usage,
        }
