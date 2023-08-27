import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage


class AddingDataToGPT:

    def __init__(self, llama_context:str):
        self.index = None
        self.persist_dir = str(Path(os.getcwd()).joinpath('assistants').joinpath('storage') \
                               .joinpath(llama_context))
        self.data_dir = str(Path(os.getcwd()).joinpath('assistants').joinpath('data') \
                            .joinpath(llama_context))
        self.build_storage()

    def build_storage(self):

        documents = SimpleDirectoryReader(self.data_dir).load_data()
        self.index = GPTVectorStoreIndex.from_documents(documents)
        self.index.storage_context.persist(self.persist_dir)


adding_data = AddingDataToGPT("infra_ui")
