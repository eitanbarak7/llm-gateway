from http import HTTPStatus
import os
from pathlib import Path

from llama_index import StorageContext, ServiceContext, load_index_from_storage
from llama_index.chat_engine.condense_question import CondenseQuestionChatEngine
from llama_index.llms import OpenAI, MessageRole

from app.routers.chat.models.indexed_query_model import IndexedQuery
from app.internal.exceptions import LLMChatStorageNotFound, LLMChatUnknownError, LLMChatUnsupportedEngine
from app.internal import infra_logger
from app.routers.chat.models.query_model import LlmEngine


def get_completion_from_message_with_indexing(query: IndexedQuery):
    adding_data = AddingDataToLlmEngine(query)
    infra_logger.log_debug(
        debug_text=f"llama response: {adding_data.response}")
    infra_logger.log_info("Received response from llama index")
    return adding_data.response.response


class AddingDataToLlmEngine:
    '''Simple class used for adding data to query'''

    def __init__(self, query: IndexedQuery):
        self.index = None
        self.persist_dir = str(Path(os.getcwd()).joinpath('assistants').joinpath('storage') \
                               .joinpath(query.llama_context))
        self.data_dir = str(Path(os.getcwd()).joinpath('assistants').joinpath('data') \
                            .joinpath(query.llama_context))
        if not os.path.exists(self.persist_dir):
            infra_logger.log_error(error_code_recevied=-1,
                                   error_text="Missing storage file")
            raise LLMChatStorageNotFound(
                http_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Llama context for {query.llama_context} was not found"
            )
        self.read_from_storage(query)
        query_engine = self.index.as_query_engine()
        chat_engine = CondenseQuestionChatEngine.from_defaults(
            query_engine=query_engine,
            chat_history=query.chat_messages[:-1],
            verbose=True)
        if query.chat_messages[-1].role != MessageRole.USER:
            infra_logger.log_error(
                error_code_recevied=-1,
                error_text="Indexed query does not end with USER propmpt")
            raise LLMChatUnknownError(
                "Indexed query does not end with USER propmpt",
                http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        self.response = chat_engine.chat(query.chat_messages[-1].content)

    def read_from_storage(self, query: IndexedQuery):
        if query.llm_engine == LlmEngine.OPEN_AI:
            service_context = ServiceContext.from_defaults(
                llm=OpenAI(temperature=query.temperature, model=query.model))
            storage_context = StorageContext.from_defaults(
                persist_dir=self.persist_dir)
            self.index = load_index_from_storage(
                storage_context=storage_context,
                service_context=service_context)
        else:
            infra_logger.log_error(
                error_code_recevied=-1,
                error_text=f"Assitant doesn't support llm engine: {query.llm_engine}")
            raise LLMChatUnsupportedEngine(
                f"Assistant doesn't support llm engine: {query.llm_engine}",
                http_code=HTTPStatus.METHOD_NOT_ALLOWED)