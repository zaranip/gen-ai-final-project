"""
Persistent memory store.

Grounded in Reflexion (Shinn et al., NeurIPS 2023): after each run the agent's
verbal reflections (lessons, weaknesses) are stored so subsequent runs on
related questions avoid repeating the same dead ends.

Storage: a single JSON file in memory_store/.
Retrieval: TF-IDF cosine similarity — no external embedding API required.
           Upgrade to dense embeddings later if needed.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DEFAULT_DIR = Path("memory_store")


class MemoryStore:
    """
    Stores (question, answer, critique, verdict) triples and retrieves
    the most relevant past attempts for a new question.

    Usage:
        store = MemoryStore()
        store.save(question, answer_dict, critique_dict, verdict="revise")
        context = store.retrieve(new_question, top_k=3)
    """

    def __init__(self, memory_dir: Optional[Path] = None):
        self.path = (memory_dir or DEFAULT_DIR) / "memory.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._records: List[dict] = self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(
        self,
        question: str,
        answer: dict,
        critique: dict,
        verdict: str,
    ) -> None:
        """Persist one (question, attempt, verdict) triple."""
        record = {
            "id": self._uid(question),
            "question": question,
            "claim": answer.get("claim", ""),
            "confidence": answer.get("confidence", ""),
            "verdict": verdict,
            "weaknesses": critique.get("weaknesses", []),
            "lessons": critique.get("lessons", ""),
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._records.append(record)
        self._flush()

    def retrieve(self, question: str, top_k: int = 3, min_score: float = 0.1) -> str:
        """
        Return a formatted string of the top-k most relevant past attempts.
        Returns empty string if no relevant memories exist.

        The formatted string is injected directly into the researcher's
        system prompt as context.
        """
        if not self._records:
            return ""

        docs = [
            r["question"] + " " + r.get("lessons", "") + " " + " ".join(r.get("weaknesses", []))
            for r in self._records
        ]

        try:
            vec = TfidfVectorizer(stop_words="english", min_df=1)
            matrix = vec.fit_transform(docs + [question])
            scores = cosine_similarity(matrix[-1], matrix[:-1])[0]
            top_idx = np.argsort(scores)[::-1][:top_k]
            relevant = [self._records[i] for i in top_idx if scores[i] >= min_score]
        except Exception:
            # Fallback: return the most recent records
            relevant = self._records[-top_k:]

        if not relevant:
            return ""

        lines = ["Past research attempts (most relevant first):"]
        for r in relevant:
            lines.append(f"\n[{r['verdict'].upper()}] {r['question']}")
            lines.append(f"  Claim:    {r['claim']}")
            if r["weaknesses"]:
                lines.append(f"  Flaws:    {'; '.join(r['weaknesses'][:2])}")
            if r["lessons"]:
                lines.append(f"  Lesson:   {r['lessons']}")
        return "\n".join(lines)

    def clear(self) -> None:
        """Wipe all stored memories (useful for test resets)."""
        self._records = []
        self._flush()

    def __len__(self) -> int:
        return len(self._records)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> List[dict]:
        if self.path.exists():
            try:
                with open(self.path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _flush(self) -> None:
        with open(self.path, "w") as f:
            json.dump(self._records, f, indent=2)

    @staticmethod
    def _uid(question: str) -> str:
        return hashlib.md5(
            (question + datetime.utcnow().isoformat()).encode()
        ).hexdigest()[:8]
