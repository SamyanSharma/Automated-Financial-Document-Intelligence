import pytest

from ai.chat_service import LLMClient, LocalTemplateClient, answer_question, get_llm_client
from ai.config import AISettings
from ai.embedding_service import LocalDeterministicEmbedder
from ai.retriever import retrieve
from ai.vector_store import VectorStore


class FakeLLMClient(LLMClient):
    """Records the exact prompt it received, for asserting citation
    instructions and context actually reach the LLM call."""

    def __init__(self):
        self.last_system_prompt = None
        self.last_user_prompt = None

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return "The revenue was $115 million (Source: page 1)."


@pytest.fixture
def seeded_store(tmp_path):
    store = VectorStore(AISettings(
        chroma_persist_dir=str(tmp_path / "chroma"),
        chroma_collection_name="chat_test",
    ))
    embedder = LocalDeterministicEmbedder(dimensions=256)
    texts = [
        "Total revenue for the quarter was $115 million, a 15 percent increase year over year.",
        "The company also announced a new product line launching next year.",
    ]
    embeddings = embedder.embed_texts(texts)
    store.add_chunks(
        chunk_ids=["r1", "r2"], texts=texts, embeddings=embeddings,
        document_id="doc-chat", page_numbers=[1, 4], sequences=[0, 1],
    )
    return store, embedder


def test_answer_question_returns_sources_with_page_numbers(seeded_store, monkeypatch):
    store, embedder = seeded_store
    monkeypatch.setattr("ai.chat_service.retrieve", lambda *a, **k: retrieve(
        k.get("question", a[0] if a else ""), document_id="doc-chat", k=2, embedder=embedder, store=store
    ))

    fake_llm = FakeLLMClient()
    response = answer_question("doc-chat", "What was the revenue?", llm_client=fake_llm)

    assert "115 million" in response.answer
    assert len(response.sources) >= 1
    assert all(s.document_id == "doc-chat" for s in response.sources)
    assert any(s.page_number == 1 for s in response.sources)


def test_answer_question_prompt_includes_citation_instruction(seeded_store, monkeypatch):
    store, embedder = seeded_store
    monkeypatch.setattr("ai.chat_service.retrieve", lambda *a, **k: retrieve(
        "revenue", document_id="doc-chat", k=2, embedder=embedder, store=store
    ))

    fake_llm = FakeLLMClient()
    answer_question("doc-chat", "revenue?", llm_client=fake_llm)

    assert "cite" in fake_llm.last_system_prompt.lower()
    assert "page" in fake_llm.last_user_prompt.lower()


def test_answer_question_no_hallucination_when_nothing_retrieved(monkeypatch):
    monkeypatch.setattr("ai.chat_service.retrieve", lambda *a, **k: [])
    fake_llm = FakeLLMClient()

    response = answer_question("doc-empty", "irrelevant question", llm_client=fake_llm)

    assert response.sources == []
    assert "don't have" in response.answer.lower() or "nothing relevant" in response.answer.lower()
    # LLM should never even be called when there's no context to ground it.
    assert fake_llm.last_user_prompt is None


def test_local_template_client_returns_context_without_calling_external_api():
    client = LocalTemplateClient()
    result = client.complete("system", "Question: x\n\nContext:\n[1] (page 1) some fact")
    assert "some fact" in result
    assert "local fallback" in result.lower()


def test_get_llm_client_falls_back_to_local_without_key():
    settings = AISettings(llm_provider="openai", openai_api_key=None)
    client = get_llm_client(settings)
    assert isinstance(client, LocalTemplateClient)

    settings2 = AISettings(llm_provider="gemini", gemini_api_key=None)
    client2 = get_llm_client(settings2)
    assert isinstance(client2, LocalTemplateClient)
