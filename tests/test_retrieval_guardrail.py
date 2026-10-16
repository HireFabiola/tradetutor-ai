"""Exercise the real answer guardrail without model loading, ChromaDB, or Ollama IO."""

import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def guardrail():
    # retriever.py opens ChromaDB and loads SentenceTransformer at import time.
    # Substitute only that dependency, then execute the unchanged llm_client.py.
    retriever = ModuleType("app.rag.retriever")
    retriever.retrieve_chunks = Mock()
    path = Path(__file__).resolve().parents[1] / "app/rag/llm_client.py"
    spec = importlib.util.spec_from_file_location("guardrail_under_test", path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"app.rag.retriever": retriever}):
        spec.loader.exec_module(module)
    with patch.object(module.ollama, "chat", return_value={
        "message": {"content": "Grounded educational answer."}
    }) as chat, patch.object(module, "ask_model", wraps=module.ask_model) as ask:
        yield module, chat, ask


def retrieval_result(distances: list[float]) -> dict:
    """Use ChromaDB's nested result structure for one query."""
    return {
        "ids": [[f"chunk_{i}" for i in range(len(distances))]],
        "documents": [[f"Educational context {i}" for i in range(len(distances))]],
        "metadatas": [[{"source": "risk_reward_lesson.md"} for _ in distances]],
        "distances": [distances],
    }


def test_relevant_retrieval_invokes_llm(guardrail) -> None:
    module, chat, ask = guardrail
    module.retrieve_chunks.return_value = retrieval_result([0.56])

    assert module.DISTANCE_THRESHOLD == 1.0
    assert module.is_context_relevant([0.56]) is True
    assert module.answer_question("Explain risk/reward.") == "Grounded educational answer."
    module.retrieve_chunks.assert_called_once_with("Explain risk/reward.", n_results=3)
    ask.assert_called_once_with("Explain risk/reward.", retrieved_chunks="Educational context 0")
    chat.assert_called_once_with(
        model="llama3.2:1b",
        messages=[{"role": "user", "content": module.SYSTEM_PROMPT.format(
            retrieved_chunks="Educational context 0", user_question="Explain risk/reward."
        )}],
    )


def test_irrelevant_retrieval_returns_fallback_without_llm(guardrail) -> None:
    module, chat, ask = guardrail
    module.retrieve_chunks.return_value = retrieval_result([1.18])

    assert module.is_context_relevant([1.18]) is False
    assert module.answer_question("Unsupported question") == module.NO_ANSWER_MESSAGE
    ask.assert_not_called()
    chat.assert_not_called()


def test_distance_equal_to_threshold_is_rejected(guardrail) -> None:
    module, chat, ask = guardrail
    module.retrieve_chunks.return_value = retrieval_result([module.DISTANCE_THRESHOLD])

    assert module.is_context_relevant([module.DISTANCE_THRESHOLD]) is False
    assert module.answer_question("Boundary question") == module.NO_ANSWER_MESSAGE
    ask.assert_not_called()
    chat.assert_not_called()


def test_empty_retrieval_currently_raises_without_invoking_llm(guardrail) -> None:
    module, chat, ask = guardrail
    module.retrieve_chunks.return_value = retrieval_result([])

    with pytest.raises(ValueError):
        module.answer_question("No matching chunks")
    ask.assert_not_called()
    chat.assert_not_called()


@pytest.mark.xfail(
    strict=True,
    raises=ValueError,
    reason="Existing gap: empty distances reach min([]) instead of the fallback response.",
)
def test_empty_retrieval_should_return_fallback(guardrail) -> None:
    module, chat, ask = guardrail
    module.retrieve_chunks.return_value = retrieval_result([])

    try:
        assert module.answer_question("No matching chunks") == module.NO_ANSWER_MESSAGE
    finally:
        ask.assert_not_called()
        chat.assert_not_called()


@pytest.mark.parametrize(
    "distances",
    [[0.56, 1.18, 1.42], [1.18, 0.56, 1.42], [1.18, 1.42, 0.56]],
)
def test_minimum_distance_controls_acceptance_regardless_of_order(guardrail, distances) -> None:
    module, chat, ask = guardrail
    result = retrieval_result(distances)
    module.retrieve_chunks.return_value = result

    assert module.is_context_relevant(distances) is True
    assert module.answer_question("Mixed matches") == "Grounded educational answer."
    # The application gates on the minimum but forwards ALL documents in returned order.
    ask.assert_called_once_with(
        "Mixed matches", retrieved_chunks="\n\n".join(result["documents"][0])
    )
    chat.assert_called_once()
