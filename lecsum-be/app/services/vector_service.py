# vector_service.py
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from typing import List


chroma = Chroma(
    persist_directory="./data/chroma",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_name="documents"
)

def get_retriever(file_id: str):
    return chroma.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 3,
            "filter": {"file_id": file_id}
        }
    )

async def get_relevant_documents(retriever, query: str) -> str:    
    documents = await retriever.ainvoke(query)
    content_of_documents = "\n\n".join([doc.page_content for doc in documents])  
    return content_of_documents