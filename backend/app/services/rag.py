from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime
from typing import Any

import httpx
from groq import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from groq import AsyncGroq

from app.core.config import settings
from app.models.entities import Analysis, ScanHistory


CHAT_SYSTEM_PROMPT = (
    "You are PotionCheck RAG Chatbot. Answer only from the retrieved product snapshot context. "
    "Answer only what the user asked, in the shortest useful form. "
    "Do not add extra explanation, disclaimers, suggestions, summaries, or follow-up topics unless the user asks for them. "
    "If a one-word or one-sentence answer is enough, use that. "
    "If the context does not contain the answer, say so clearly. "
    "Do not invent ingredients, nutrition values, or warnings."
)


def _compact(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def product_snapshot(scan: ScanHistory, analysis: Analysis) -> str:
    raw = scan.raw_product_data or {}
    sections = [
        ("Product", {
            "scan_id": scan.id,
            "analysis_id": analysis.id,
            "product_name": scan.product_name,
            "barcode": scan.barcode,
            "verdict": scan.verdict,
            "safety_score": scan.safety_score,
            "flagged_count": scan.flagged_count,
            "created_at": scan.created_at,
            "image": scan.product_image_url,
            "brand": raw.get("brands") or raw.get("brand"),
            "categories": raw.get("categories"),
        }),
        ("Ingredients Text", raw.get("ingredients_text") or raw.get("ingredients_text_en")),
        ("All Ingredients Analysis", analysis.all_ingredients),
        ("Flagged Ingredients", analysis.flagged_ingredients),
        ("Nutrition", analysis.nutriments or raw.get("nutriments") or raw.get("nutrition")),
        ("AI Summary", analysis.ai_summary),
        ("AI Recommendation", analysis.ai_recommendation),
        ("Personalized Warnings", analysis.personalized_warnings),
        ("Raw Product Data", raw),
    ]
    return "\n\n".join(f"## {title}\n{_compact(content)}" for title, content in sections if _compact(content))


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    size = max(400, chunk_size or settings.rag_chunk_size)
    step_back = max(0, min(overlap or settings.rag_chunk_overlap, size // 2))
    paragraphs = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > size:
            if current:
                chunks.append(current.strip())
                current = ""
            start = 0
            while start < len(paragraph):
                chunks.append(paragraph[start:start + size].strip())
                start += size - step_back
            continue
        candidate = f"{current}\n\n{paragraph}".strip()
        if len(candidate) <= size:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())
            current = paragraph
    if current:
        chunks.append(current.strip())
    return chunks


def _hash_embedding(text: str, dimensions: int = 384) -> list[float]:
    vector = [0.0] * dimensions
    tokens = re.findall(r"[a-zA-Z0-9_%-]+", text.lower())
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = -1.0 if digest[4] % 2 else 1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


async def embed_texts(texts: list[str], preferred_source: str | None = None) -> tuple[list[list[float]], str]:
    if not texts:
        return [], "none"
    if preferred_source == "local_hash_384":
        return [_hash_embedding(text) for text in texts], "local_hash_384"
    embeddings: list[list[float]] = []
    timeout = httpx.Timeout(settings.ollama_timeout_seconds, connect=10)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            for text in texts:
                response = await client.post(
                    f"{settings.ollama_base_url.rstrip('/')}/api/embeddings",
                    json={"model": settings.ollama_embedding_model, "prompt": text},
                )
                response.raise_for_status()
                embedding = response.json().get("embedding")
                if not embedding:
                    raise RuntimeError("Ollama embedding response was empty")
                embeddings.append([float(value) for value in embedding])
        return embeddings, f"ollama_{len(embeddings[0])}"
    except Exception:
        return [_hash_embedding(text) for text in texts], "local_hash_384"


def _collection_name(source: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", source).strip("_").lower() or "default"
    return f"product_rag_{cleaned}"[:60]


def _chroma_collection(source: str):
    try:
        import chromadb
    except ImportError as exc:
        raise RuntimeError("chromadb is not installed. Run pip install -r backend/requirements.txt") from exc
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return client.get_or_create_collection(name=_collection_name(source), metadata={"hnsw:space": "cosine"})


async def index_product(scan: ScanHistory, analysis: Analysis) -> dict:
    chunks = chunk_text(product_snapshot(scan, analysis))
    embeddings, source = await embed_texts(chunks)
    collection = _chroma_collection(source)
    where = {"scan_id": scan.id}
    try:
        collection.delete(where=where)
    except Exception:
        pass
    metadatas = [
        {
            "scan_id": scan.id,
            "analysis_id": analysis.id,
            "user_id": scan.user_id or "anonymous",
            "product_name": scan.product_name or "Unknown product",
            "chunk_index": index,
            "created_at": scan.created_at.isoformat() if isinstance(scan.created_at, datetime) else str(scan.created_at),
        }
        for index, _ in enumerate(chunks)
    ]
    collection.add(
        ids=[f"{analysis.id}:{index}" for index in range(len(chunks))],
        documents=chunks,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    return {"chunks": len(chunks), "embedding_source": source}


async def retrieve_context(scan: ScanHistory, analysis: Analysis, question: str, top_k: int | None = None) -> tuple[list[dict], dict]:
    index_meta = await index_product(scan, analysis)
    question_chunks = chunk_text(question, chunk_size=500, overlap=80)
    query_embedding, source = await embed_texts(question_chunks or [question], preferred_source=index_meta["embedding_source"])
    if source != index_meta["embedding_source"]:
        index_meta = await index_product(scan, analysis)
        query_embedding, source = await embed_texts(question_chunks or [question], preferred_source=index_meta["embedding_source"])
    collection = _chroma_collection(source)
    result = collection.query(
        query_embeddings=query_embedding,
        n_results=max(1, top_k or settings.rag_top_k),
        where={"scan_id": scan.id},
        include=["documents", "metadatas", "distances"],
    )
    contexts_by_id = {}
    for documents, metadatas, distances in zip(result.get("documents", []), result.get("metadatas", []), result.get("distances", [])):
        for document, metadata, distance in zip(documents, metadatas, distances):
            key = f"{metadata.get('analysis_id')}:{metadata.get('chunk_index')}"
            existing = contexts_by_id.get(key)
            if not existing or distance < existing["distance"]:
                contexts_by_id[key] = {"text": document, "metadata": metadata, "distance": distance}
    contexts = sorted(contexts_by_id.values(), key=lambda item: item["distance"])[:max(1, top_k or settings.rag_top_k)]
    index_meta["question_chunks"] = len(question_chunks or [question])
    return contexts, index_meta


def build_chat_prompt(product_name: str, question: str, contexts: list[dict]) -> str:
    context_text = "\n\n---\n\n".join(
        f"Source chunk {index + 1}:\n{item['text']}" for index, item in enumerate(contexts)
    )
    return f"""
Selected product: {product_name}

Retrieved product snapshot chunks:
{context_text or "No relevant chunks were retrieved."}

User question:
{question}

Answer rules:
- Answer only the exact question asked.
- Keep the answer short: usually 1 to 3 sentences, or bullets only if the user asks for a list.
- Use only the retrieved context.
- Mention product-specific ingredient or nutrition values when they are present.
- If the data is missing, say only what is missing.
- Do not add extra tips, long explanations, or unrelated safety advice.
"""


async def _chat_with_groq(prompt: str) -> str:
    if not settings.groq_api_key:
        raise RuntimeError("Groq API key is not configured")
    client = AsyncGroq(api_key=settings.groq_api_key)
    response = await client.chat.completions.create(
        model=settings.groq_model,
        max_tokens=180,
        temperature=0.15,
        messages=[
            {"role": "system", "content": CHAT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""


async def _chat_with_ollama(prompt: str) -> str:
    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "messages": [
            {"role": "system", "content": CHAT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "options": {"temperature": 0.15, "num_predict": 180},
        "keep_alive": "10m",
    }
    timeout = httpx.Timeout(settings.ollama_timeout_seconds, connect=10)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(f"{settings.ollama_base_url.rstrip('/')}/api/chat", json=payload)
        response.raise_for_status()
    return response.json().get("message", {}).get("content") or ""


async def answer_product_question(scan: ScanHistory, analysis: Analysis, question: str) -> dict:
    contexts, index_meta = await retrieve_context(scan, analysis, question)
    prompt = build_chat_prompt(scan.product_name or "Selected product", question, contexts)
    provider = "groq"
    try:
        answer = await _chat_with_groq(prompt)
    except (RateLimitError, APIStatusError, APIConnectionError, APITimeoutError, RuntimeError):
        provider = "ollama"
        try:
            answer = await _chat_with_ollama(prompt)
        except Exception:
            provider = "retrieval_only"
            answer = (
                "I retrieved the matching product data, but both Groq and Ollama were unavailable. "
                "From the saved report, review these matching chunks: "
                + " ".join(item["text"][:240] for item in contexts[:2])
            )
    return {
        "answer": answer.strip(),
        "provider": provider,
        "retrieved_chunks": contexts,
        **index_meta,
    }
