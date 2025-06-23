from src.helpers import load_file, text_splitter, download_embeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

extracted_data= load_file(data = 'data/')
texts_chunks = text_splitter(data=extracted_data)
embeddings = download_embeddings()
index_name = "unibot"

pinecone_client = Pinecone(
            api_key=os.getenv("PINECONE_API_KEY")
        )

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings,
)


docsearch = PineconeVectorStore.from_documents(
    documents=texts_chunks,
    index_name=index_name,
    embedding=embeddings,
)