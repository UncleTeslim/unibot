from src.helpers import load_data_from_directory, split_documents, download_embeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
import os
from dotenv import load_dotenv

index_name = "unibot"

load_dotenv()
def store_data_in_pinecone(directory, file_type="pdf"):
    """
    Load data from a directory, split it into chunks, and store it in Pinecone.
    """
    documents = load_data_from_directory(directory, file_type=file_type)
    chunks = split_documents(documents)
    embeddings = download_embeddings()
    index_name = "unibot"
    pinecone_client = Pinecone(
        api_key=os.getenv("PINECONE_API_KEY"),
        environment=os.getenv("PINECONE_ENVIRONMENT")
    )
    
    
    existing_indexes = pinecone_client.list_indexes()
    index_names_list = [index.name for index in existing_indexes]
        
    if index_name in index_names_list:
        print(f"Index '{index_name}' already exists. Using existing index.")
    else:
        print(f"Creating new index '{index_name}'...")
        pinecone_client.create_index(
            name=index_name,
            dimension=384, 
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    
    
    # Create a vector store in Pinecone
    vector_store = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings,
    )
    
    vector_store.add_documents(chunks)
    
    print("Data stored successfully in Pinecone.")
    
if __name__ == "__main__":
    store_data_in_pinecone(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))
    print("\n--- Data Ingestion Process Finished ---")

