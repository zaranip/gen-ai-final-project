import unittest
from pathlib import Path
from unittest.mock import patch

import src.orchestrator as orchestrator


def _agent_result(claim, tokens=None):
    return {
        "answer": {
            "claim": claim,
            "confidence": "medium",
            "evidence_summary": f"Evidence for {claim}",
            "rationale": f"Rationale for {claim}",
            "open_questions": [],
        },
        "tool_calls": 0,
        "token_usage": tokens or {"input_tokens": 10, "output_tokens": 5},
    }


def _critic_result(verdict, weaknesses=None):
    return {
        "critique": {
            "verdict": verdict,
            "weaknesses": weaknesses or [],
            "suggested_investigations": weaknesses or [],
            "lessons": "Check the actual time window.",
        },
        "tool_calls": 0,
        "token_usage": {"input_tokens": 4, "output_tokens": 2},
    }


class SequencedResearchAgent:
    answers = []
    instances = []

    def __init__(self, model):
        self.model = model
        self.calls = []
        self.__class__.instances.append(self)

    def investigate(self, question, memory_context=None, critic_feedback=None):
        self.calls.append(
            {
                "question": question,
                "memory_context": memory_context,
                "critic_feedback": critic_feedback,
            }
        )
        return self.__class__.answers.pop(0)


class FixedCriticAgent:
    result = _critic_result("accept")
    instances = []

    def __init__(self, model):
        self.model = model
        self.calls = []
        self.__class__.instances.append(self)

    def critique(self, question, researcher_output):
        self.calls.append({"question": question, "researcher_output": researcher_output})
        return self.__class__.result


class CapturingMemoryStore:
    instances = []

    def __init__(self, memory_dir=None):
        self.memory_dir = memory_dir
        self.saved = []
        self.__class__.instances.append(self)

    def retrieve(self, question):
        return ""

    def save(self, question, answer, critique, verdict):
        self.saved.append(
            {
                "question": question,
                "answer": answer,
                "critique": critique,
                "verdict": verdict,
            }
        )


class OrchestratorModeTests(unittest.TestCase):
    def setUp(self):
        SequencedResearchAgent.answers = []
        SequencedResearchAgent.instances = []
        FixedCriticAgent.result = _critic_result("accept")
        FixedCriticAgent.instances = []
        CapturingMemoryStore.instances = []

    def run_with_fakes(self, *args, **kwargs):
        with (
            patch.object(orchestrator, "ResearchAgent", SequencedResearchAgent),
            patch.object(orchestrator, "CriticAgent", FixedCriticAgent),
            patch.object(orchestrator, "MemoryStore", CapturingMemoryStore),
            patch.object(orchestrator, "_save_log", lambda run_log: None),
        ):
            return orchestrator.run(*args, **kwargs)

    def test_loop_1_returns_revised_answer_when_critic_requests_revision(self):
        SequencedResearchAgent.answers = [
            _agent_result("initial answer"),
            _agent_result("revised answer"),
        ]
        FixedCriticAgent.result = _critic_result(
            "revise",
            weaknesses=["Re-check the GDP trough date."],
        )

        result = self.run_with_fakes("Did GDP recover?", mode="loop_1")

        self.assertEqual(result["final_answer"]["claim"], "revised answer")
        self.assertEqual(result["iterations"], 2)
        researcher = SequencedResearchAgent.instances[0]
        self.assertIsNone(researcher.calls[0]["critic_feedback"])
        self.assertEqual(
            researcher.calls[1]["critic_feedback"],
            "Re-check the GDP trough date.",
        )
        self.assertEqual(CapturingMemoryStore.instances, [])

    def test_loop_1_does_not_revise_after_accept_verdict(self):
        SequencedResearchAgent.answers = [_agent_result("accepted answer")]
        FixedCriticAgent.result = _critic_result("accept")

        result = self.run_with_fakes("Did inflation cool?", mode="loop_1")

        self.assertEqual(result["final_answer"]["claim"], "accepted answer")
        self.assertEqual(result["iterations"], 1)
        researcher = SequencedResearchAgent.instances[0]
        self.assertEqual(len(researcher.calls), 1)

    def test_loop_n_passes_configured_memory_directory_to_store(self):
        SequencedResearchAgent.answers = [_agent_result("memory-backed answer")]
        FixedCriticAgent.result = _critic_result("accept")
        memory_dir = Path("outputs/test-memory")

        result = self.run_with_fakes(
            "What did prior runs learn?",
            mode="loop_n",
            memory_dir=memory_dir,
        )

        self.assertEqual(result["final_answer"]["claim"], "memory-backed answer")
        self.assertEqual(CapturingMemoryStore.instances[0].memory_dir, memory_dir)
        self.assertEqual(len(CapturingMemoryStore.instances[0].saved), 1)


if __name__ == "__main__":
    unittest.main()
