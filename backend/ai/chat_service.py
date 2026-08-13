"""
RAG Q&A orchestration: retrieve relevant chunks, build a citation-enforcing
prompt, call an LLM to generate the answer.

Provider design mirrors embedding_service.py: an `LLMClient` interface
with real `OpenAIChatClient` / `GeminiChatClient` implementations (either
requires an API key — real generation, real cost, real network call), and
a `LocalTemplateClient` fallback that does no generation at all — it
extracts and formats the single most relevant retrieved chunk. This is
clearly labeled as a stub in its docstring and in every answer it
produces, but it lets the *retrieval → prompt → citation* pipeline be
tested end-to-end without an API key, which is what this sandbox has
available and what any CI environment should be able to run too.

The prompt template is shared across all three providers: it always
includes the retrieved chunks as numbered, cited context and explicitly
instructs the model to cite page numbers and refuse to answer from
outside the provided context. This is what "enforces citing chunk page
numbers" in practice — the enforcement happens via the retrieval scope
(only relevant chunks are ever given as context) plus the prompt
instruction; a production system could additionally validate the model's
citations against the source list, if stricter guarantees were needed.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from ai.config import AISettings, get_ai_settings
from ai.retriever import RetrievedChunk, retrieve
from ai.schemas import ChatResponse, ChatSource

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a financial document analysis assistant. Answer the user's "
    "question using ONLY the numbered context excerpts below. Every claim "
    "you make must cite its source like this: (Source: page N). If the "
    "context does not contain enough information to answer, say so "
    "explicitly instead of guessing."
)


class LLMClient(ABC):
    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Return the model's answer text."""


class OpenAIChatClient(LLMClient):
    def __init__(self, api_key: str, model: str):
        from openai import OpenAI  # imported lazily: optional dep

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""


class GeminiChatClient(LLMClient):
    def __init__(self, api_key: str, model: str):
        import google.generativeai as genai  # imported lazily: optional dep

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self._model.generate_content(f"{system_prompt}\n\n{user_prompt}")
        return response.text or ""


class LocalTemplateClient(LLMClient):
    """
    Offline stub - no generation. Extracts the top retrieved excerpt(s)
    already embedded in `user_prompt` and returns them verbatim with their
    citation, clearly labeled as a non-generative fallback. Used when no
    OpenAI/Gemini key is configured, so the surrounding retrieval + prompt
    + citation machinery is still exercisable without network access.
    """

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return (
            "[local fallback - no LLM configured, showing raw retrieved context]\n\n"
            + user_prompt.split("Context:\n", 1)[-1]
        )


def get_llm_client(settings: AISettings | None = None) -> LLMClient:
    settings = settings or get_ai_settings()

    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            logger.warning("llm_provider=openai but OPENAI_API_KEY not set; using LocalTemplateClient")
            return LocalTemplateClient()
        return OpenAIChatClient(settings.openai_api_key, settings.openai_chat_model)

    if settings.llm_provider == "gemini":
        if not settings.gemini_api_key:
            logger.warning("llm_provider=gemini but GEMINI_API_KEY not set; using LocalTemplateClient")
            return LocalTemplateClient()
        return GeminiChatClient(settings.gemini_api_key, settings.gemini_model)

    return LocalTemplateClient()


def _build_context_block(chunks: list[RetrievedChunk]) -> str:
    lines = []
    for i, c in enumerate(chunks, start=1):
        lines.append(f"[{i}] (page {c.page_number}) {c.text}")
    return "\n\n".join(lines)


def answer_question(
    document_id: str,
    question: str,
    top_k: int | None = None,
    llm_client: LLMClient | None = None,
) -> ChatResponse:
    """
    Full RAG pipeline: retrieve -> build cited context -> generate answer.
    Returns an empty-source, explicit "no information" answer if nothing
    relevant was retrieved, rather than letting the LLM hallucinate.
    """
    chunks = retrieve(question, document_id=document_id, k=top_k)

    if not chunks:
        return ChatResponse(
            answer=(
                "I don't have any embedded content for this document yet, "
                "or nothing relevant was found for that question."
            ),
            sources=[],
        )

    context_block = _build_context_block(chunks)
    user_prompt = (
        f"Question: {question}\n\n"
        f"Context:\n{context_block}\n\n"
        "Answer the question, citing the page number for every claim."
    )

    client = llm_client or get_llm_client()
    answer = client.complete(SYSTEM_PROMPT, user_prompt)

    sources = [
        ChatSource(
            document_id=c.document_id,
            chunk_id=c.chunk_id,
            page_number=c.page_number,
            text_snippet=c.text[:200],
        )
        for c in chunks
    ]

    logger.info("answer_question(document_id=%s): %d sources cited", document_id, len(sources))
    return ChatResponse(answer=answer, sources=sources)
