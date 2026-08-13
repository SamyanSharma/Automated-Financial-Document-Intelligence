import pytest

from ai.config import AISettings
from ai.embedding_service import LocalDeterministicEmbedder, get_embedder
from ai.retriever import retrieve
from ai.vector_store import VectorStore


@pytest.fixture
def vector_store(tmp_path):
    # Unique directory + collection name per test: chromadb caches clients
    # in-process by path, so reusing a shared path across tests can leak
    # collection state (e.g. embedding dimension) between otherwise
    # independent tests.
    store = VectorStore(AISettings(
        chroma_persist_dir=str(tmp_path / "chroma"),
        chroma_collection_name="test_collection",
    ))
    return store


def test_local_embedder_is_deterministic():
    embedder = LocalDeterministicEmbedder(dimensions=64)
    v1 = embedder.embed_query("revenue increased significantly")
    v2 = embedder.embed_query("revenue increased significantly")
    assert v1 == v2


def test_local_embedder_produces_correct_dimensionality():
    embedder = LocalDeterministicEmbedder(dimensions=128)
    vec = embedder.embed_query("some text")
    assert len(vec) == 128


def test_local_embedder_similar_text_more_similar_than_dissimilar():
    """Sanity check the vector space actually behaves like a vector space:
    shared-vocabulary texts should be closer than unrelated ones."""
    embedder = LocalDeterministicEmbedder(dimensions=256)

    def cosine(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        return dot  # already L2-normalized, so dot product == cosine similarity

    revenue_a = embedder.embed_query("Company revenue grew significantly this quarter")
    revenue_b = embedder.embed_query("Quarterly revenue growth was strong for the company")
    unrelated = embedder.embed_query("The cafeteria menu changed to include more vegetarian options")

    sim_related = cosine(revenue_a, revenue_b)
    sim_unrelated = cosine(revenue_a, unrelated)
    assert sim_related > sim_unrelated


def test_get_embedder_falls_back_to_local_without_api_key():
    settings = AISettings(embedding_provider="openai", openai_api_key=None)
    embedder = get_embedder(settings)
    assert isinstance(embedder, LocalDeterministicEmbedder)


def test_vector_store_add_and_search(vector_store):
    embedder = LocalDeterministicEmbedder(dimensions=128)
    texts = [
        "Total revenue for the quarter was $115 million, up 15 percent.",
        "The office relocated to a larger space downtown.",
    ]
    embeddings = embedder.embed_texts(texts)

    vector_store.add_chunks(
        chunk_ids=["a", "b"],
        texts=texts,
        embeddings=embeddings,
        document_id="doc-1",
        page_numbers=[1, 2],
        sequences=[0, 1],
    )

    query_vec = embedder.embed_query("What was the quarterly revenue?")
    hits = vector_store.similarity_search(query_vec, k=1, document_id="doc-1")

    assert len(hits) == 1
    assert hits[0]["id"] == "a"
    assert hits[0]["metadata"]["page_number"] == 1


def test_vector_store_scopes_search_to_document_id(vector_store):
    embedder = LocalDeterministicEmbedder(dimensions=64)
    text = "Revenue discussion for this document."
    emb = embedder.embed_texts([text])

    vector_store.add_chunks(
        chunk_ids=["x"], texts=[text], embeddings=emb,
        document_id="doc-A", page_numbers=[1], sequences=[0],
    )

    query_vec = embedder.embed_query("revenue")
    hits_wrong_doc = vector_store.similarity_search(query_vec, k=5, document_id="doc-B")
    hits_right_doc = vector_store.similarity_search(query_vec, k=5, document_id="doc-A")

    assert hits_wrong_doc == []
    assert len(hits_right_doc) == 1


def test_vector_store_upsert_is_idempotent(vector_store):
    embedder = LocalDeterministicEmbedder(dimensions=32)
    text = "Some chunk text."
    emb = embedder.embed_texts([text])

    vector_store.add_chunks(
        chunk_ids=["dup"], texts=[text], embeddings=emb,
        document_id="doc-1", page_numbers=[1], sequences=[0],
    )
    vector_store.add_chunks(
        chunk_ids=["dup"], texts=[text], embeddings=emb,
        document_id="doc-1", page_numbers=[1], sequences=[0],
    )

    assert vector_store._collection.count() == 1


def test_retrieve_returns_correct_chunk_for_revenue_query(vector_store, monkeypatch):
    embedder = LocalDeterministicEmbedder(dimensions=256)
    texts = [
        "Total revenue for the quarter was $115 million, a 15 percent increase.",
        "Net income for the quarter was $9 million, driven by margin expansion.",
        "The board approved a new share buyback program during the quarter.",
    ]
    embeddings = embedder.embed_texts(texts)
    vector_store.add_chunks(
        chunk_ids=["r", "n", "b"], texts=texts, embeddings=embeddings,
        document_id="doc-fin", page_numbers=[1, 2, 3], sequences=[0, 1, 2],
    )

    results = retrieve(
        "What was the company's revenue?",
        document_id="doc-fin",
        k=1,
        embedder=embedder,
        store=vector_store,
    )

    assert len(results) == 1
    assert results[0].chunk_id == "r"
    assert results[0].page_number == 1
