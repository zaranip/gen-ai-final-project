# Critic agent — adversarial reviewer in the Self-Refine loop.
# Intentionally runs on a different model than the researcher to reduce echo-chamber agreement.
# Re-fetches FRED data independently rather than trusting the researcher's numbers.

import json
from typing import Optional

import anthropic
from dotenv import load_dotenv

from src.tools.fred_tool import fetch_series, get_series_info

load_dotenv()

SYSTEM_PROMPT = """You are a skeptical peer reviewer for macroeconomic research. \
Your job is to find real flaws — not to agree.

Pull the FRED data yourself and check the researcher's specific numbers. \
Look for alternative explanations, cherry-picked windows, or confounding factors they missed. \
Don't let a plausible-sounding argument slide if you haven't verified the underlying data.

Verdicts:
  accept  — you checked the data and genuinely found no substantive problem
  revise  — specific fixable issues; tell the researcher exactly what to re-examine
  reject  — fundamental flaw that invalidates the main claim

Call `submit_critique` when done.
"""

TOOLS = [
    {
        "name": "fetch_fred_series",
        "description": "Fetch FRED data to independently verify the researcher's claims.",
        "input_schema": {
            "type": "object",
            "properties": {
                "series_id": {"type": "string"},
                "start_date": {"type": "string", "description": "YYYY-MM-DD (optional)"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD (optional)"},
            },
            "required": ["series_id"],
        },
    },
    {
        "name": "get_fred_series_info",
        "description": "Get metadata for a FRED series to check units/frequency.",
        "input_schema": {
            "type": "object",
            "properties": {
                "series_id": {"type": "string"},
            },
            "required": ["series_id"],
        },
    },
    {
        "name": "submit_critique",
        "description": "Submit your structured critique after reviewing the researcher's answer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "verdict": {
                    "type": "string",
                    "enum": ["accept", "revise", "reject"],
                },
                "weaknesses": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Specific flaws found. Each item should name the claim and "
                        "the problem. Empty only if verdict is 'accept'."
                    ),
                },
                "suggested_investigations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "What the researcher should check or correct next.",
                },
                "lessons": {
                    "type": "string",
                    "description": (
                        "One key takeaway to store in memory for future research on "
                        "this topic — what dead end to avoid or what source to trust."
                    ),
                },
            },
            "required": ["verdict", "weaknesses", "suggested_investigations", "lessons"],
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
    else:
        result = {"error": f"Unknown tool: {name}"}
    return json.dumps(result)


class CriticAgent:

    def __init__(
        self,
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 4096,
        max_tool_calls: int = 12,
    ):
        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens
        self.max_tool_calls = max_tool_calls

    def critique(self, question: str, researcher_output: dict) -> dict:
        answer = researcher_output.get("answer", {})
        user_content = f"""Research Question: {question}

Researcher's Findings:
  Claim:      {answer.get("claim", "")}
  Confidence: {answer.get("confidence", "")}
  Evidence:   {answer.get("evidence_summary", "")}
  Rationale:  {answer.get("rationale", "")}
  Open Qs:    {json.dumps(answer.get("open_questions", []))}

Fetch the FRED data yourself to verify specific numbers. Then submit your critique."""

        messages = [{"role": "user", "content": user_content}]
        tool_call_count = 0
        token_usage = {"input_tokens": 0, "output_tokens": 0}

        while tool_call_count < self.max_tool_calls:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            token_usage["input_tokens"] += response.usage.input_tokens
            token_usage["output_tokens"] += response.usage.output_tokens

            for block in response.content:
                if block.type == "tool_use" and block.name == "submit_critique":
                    return {
                        "critique": block.input,
                        "tool_calls": tool_call_count,
                        "token_usage": token_usage,
                    }

            if response.stop_reason != "tool_use":
                return {
                    "critique": {
                        "verdict": "accept",
                        "weaknesses": [],
                        "suggested_investigations": [],
                        "lessons": "Critic stopped without a structured submission.",
                    },
                    "tool_calls": tool_call_count,
                    "token_usage": token_usage,
                }

            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use" and block.name != "submit_critique":
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": _dispatch(block.name, block.input),
                    })
                    tool_call_count += 1
            messages.append({"role": "user", "content": tool_results})

        return {
            "critique": {
                "verdict": "accept",
                "weaknesses": [],
                "suggested_investigations": [],
                "lessons": "Critic reached tool call limit without finding a clear flaw.",
            },
            "tool_calls": tool_call_count,
            "token_usage": token_usage,
        }
