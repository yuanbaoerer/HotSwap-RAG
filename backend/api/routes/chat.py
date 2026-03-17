"""Chat and RAG query API routes."""

import json
import logging
from typing import List, Optional, AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.factories import create_store, create_llm
from backend.utils.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class SourceReference(BaseModel):
    """Source reference model for RAG response."""

    document_id: Optional[str] = None
    filename: Optional[str] = None
    content_snippet: str
    score: Optional[float] = None


class ChatRequest(BaseModel):
    """Request model for chat."""

    question: str
    kb_id: Optional[str] = None
    stream: bool = False
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_k: int = 4


class ChatResponse(BaseModel):
    """Response model for chat."""

    answer: str
    sources: List[SourceReference]
    kb_id: Optional[str] = None
    model: Optional[str] = None


def get_vector_store(kb_id: Optional[str] = None):
    """Get vector store instance.

    Args:
        kb_id: Knowledge base ID for collection naming.

    Returns:
        Vector store instance.
    """
    collection_name = kb_id or "default"
    return create_store(
        store_type="chromadb",
        collection_name=collection_name,
        persist_directory=str(settings.vector_stores_dir),
    )


def get_llm_instance():
    """Get LLM instance based on settings.

    Returns:
        LLM instance.
    """
    # Default to OpenAI, can be configured via settings
    llm_type = settings.default_llm

    if llm_type == "openai":
        return create_llm("openai", model=settings.default_embedding_model.replace("embedding", "gpt-4o-mini"))
    elif llm_type == "anthropic":
        return create_llm("anthropic")
    elif llm_type == "ollama":
        return create_llm("ollama")
    else:
        return create_llm("openai")


def format_sources(results: List[dict]) -> List[SourceReference]:
    """Format search results as source references.

    Args:
        results: Search results from vector store.

    Returns:
        List of SourceReference objects.
    """
    sources = []
    for result in results:
        metadata = result.get("metadata", {})
        sources.append(
            SourceReference(
                document_id=metadata.get("document_id"),
                filename=metadata.get("filename"),
                content_snippet=result.get("content", "")[:200] + "...",
                score=result.get("score"),
            )
        )
    return sources


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a RAG query and return the answer.

    This endpoint:
    1. Searches the vector store for relevant documents
    2. Uses the LLM to generate an answer based on the context
    3. Returns the answer with source references
    """
    logger.info(f"Processing RAG query: {request.question[:50]}...")

    try:
        # Get vector store and search
        store = get_vector_store(request.kb_id)
        results = store.similarity_search(request.question, k=request.top_k)

        if not results:
            logger.warning("No relevant documents found")
            return ChatResponse(
                answer="I couldn't find any relevant information in the knowledge base. "
                       "Please make sure documents have been uploaded and processed.",
                sources=[],
                kb_id=request.kb_id,
                model=settings.default_llm,
            )

        # Extract context from results
        contexts = [result.get("content", "") for result in results]
        sources = format_sources(results)

        # Get LLM and generate response
        llm = get_llm_instance()

        answer = llm.generate_with_context(
            prompt=request.question,
            contexts=contexts,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        logger.info(f"Generated answer for question")

        return ChatResponse(
            answer=answer,
            sources=sources,
            kb_id=request.kb_id,
            model=llm.model_name,
        )

    except ValueError as e:
        # Handle configuration errors (missing API keys, etc.)
        error_msg = str(e)
        logger.error(f"Configuration error: {error_msg}")
        if "API_KEY" in error_msg.upper() or "KEY" in error_msg.lower():
            return ChatResponse(
                answer="API key is not configured. Please set up your API keys in the .env file. "
                       "For OpenAI, set OPENAI_API_KEY. For Anthropic, set ANTHROPIC_API_KEY.",
                sources=[],
                kb_id=request.kb_id,
                model=None,
            )
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Process a RAG query with streaming response (SSE).

    This endpoint returns the response as a stream of server-sent events.
    Event format: data: {"content": "chunk of text"}\n\n
    """
    logger.info(f"Processing streaming RAG query: {request.question[:50]}...")

    async def generate() -> AsyncGenerator[str, None]:
        try:
            # Get vector store and search
            store = get_vector_store(request.kb_id)
            results = store.similarity_search(request.question, k=request.top_k)

            if not results:
                # Send message about no results
                yield f"data: {json.dumps({'content': 'No relevant documents found. '})}\n\n"
                yield f"data: {json.dumps({'content': 'Please upload and process documents first.'})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
                return

            # Extract context from results
            contexts = [result.get("content", "") for result in results]

            # Get LLM instance
            llm = get_llm_instance()

            # Stream the response
            full_response = ""
            for chunk in llm.stream_generate(
                prompt=request.question,
                contexts=contexts,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            # Send sources at the end
            sources = format_sources(results)
            yield f"data: {json.dumps({'sources': [s.model_dump() for s in sources]})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

            logger.info("Streaming completed")

        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )