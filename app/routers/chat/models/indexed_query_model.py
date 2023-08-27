from typing import List
from enum import Enum

from pydantic import BaseModel, Field
from llama_index.llms.base import ChatMessage

from app.routers.chat.models.query_model import LlmEngine


class LlamaContext(str, Enum):
    '''Enum class to represent different llama contexts'''
    INFRA_UI = "infra_ui"


class IndexedQuery(BaseModel):
    '''An object representing an indexed query with its essential parameters'''
    temperature: float = Field(ge=0, le=1, default=0)
    llm_engine: LlmEngine = LlmEngine.OPEN_AI
    model: str = "gpt-3.5-turbo"
    chat_messages: List[ChatMessage]
    llama_context: LlamaContext

    class Config:
        use_enum_values = True