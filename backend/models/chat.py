"""Chat-related Pydantic models."""

from typing import List, Optional

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """Model for source reference in RAG response."""

    document_id: str
    filename: str
    chunk_index: int
    content_snippet: str = Field(..., description="Snippet of relevant content")
    score: float = Field(..., description="Relevance score")


class ChatRequest(BaseModel):
    """Model for chat request."""

    question: str = Field(..., description="User's question", min_length=1)
    kb_id: Optional[str] = Field(None, description="Knowledge base to query")
    stream: bool = Field(False, description="Whether to stream the response")
    temperature: float = Field(0.7, ge=0, le=2, description="LLM temperature")
    max_tokens: Optional[int] = Field(None, description="Max tokens in response")
    top_k: int = Field(4, description="Number of context chunks to retrieve")


class ChatResponse(BaseModel):
    """Model for chat response."""

    answer: str = Field(..., description="Generated answer")
    sources: List[SourceReference] = Field(
        default_factory=list,
        description="Source documents used",
    )
    kb_id: Optional[str] = Field(None, description="Knowledge base used")
    model: Optional[str] = Field(None, description="LLM model used")


class ChatMessage(BaseModel):
    """Model for a chat message in history."""

    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp")