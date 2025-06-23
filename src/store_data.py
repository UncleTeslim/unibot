# from src.helpers import load_data_from_directory, split_documents, download_embeddings
# from pinecone import Pinecone, ServerlessSpec
# from langchain_pinecone import PineconeVectorStore
# import os
# from dotenv import load_dotenv

# index_name = "unibot"

# load_dotenv()
# def store_data_in_pinecone(directory, file_type="pdf"):
#     """
#     Load data from a directory, split it into chunks, and store it in Pinecone.
#     """
#     documents = load_data_from_directory(directory, file_type)
#     chunks = split_documents(documents)
#     embeddings = download_embeddings()
    
#     pinecone_client = Pinecone(
#         api_key=os.getenv("PINECONE_API_KEY"),
#         # environment=os.getenv("PINECONE_ENVIRONMENT")
#     )
    
#     pinecone_client.create_index(
#         name = index_name,
#         dimension = 384,
#         metric = "cosine",
#         serverless=ServerlessSpec(
#             cloud="aws",
#             region="us-east-1",
#         )
#     )
    
    
#     # Create a vector store in Pinecone
#     vector_store = PineconeVectorStore(
#         index_name=index_name,
#         embedding=embeddings,
#         pinecone_client=pinecone_client
#     )
    
#     vector_store.add_documents(chunks)
    
#     print("Data stored successfully in Pinecone.")
    
# if __name__ == "__main__":
#     store_data_in_pinecone(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))
#     print("\n--- Data Ingestion Process Finished ---")


from src.helpers import load_data_from_directory, split_documents, download_embeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
import os
import time
from dotenv import load_dotenv

index_name = "unibot"

load_dotenv()

def store_data_in_pinecone(directory, file_type="pdf"):
    """
    Load data from a directory, split it into chunks, and store it in Pinecone.
    """
    try:
        print("Loading documents...")
        documents = load_data_from_directory(directory)
        
        if not documents:
            print("No documents found in the specified directory.")
            return
        
        print(f"Loaded {len(documents)} documents. Splitting into chunks...")
        chunks = split_documents(documents)
        
        if not chunks:
            print("No chunks created from documents.")
            return
        
        print(f"Created {len(chunks)} chunks. Loading embeddings...")
        embeddings = download_embeddings()
        
        
        # Initialize Pinecone client
        print("Initializing Pinecone client...")
        pinecone_client = Pinecone(
            api_key=os.getenv("PINECONE_API_KEY")
        )
        
        # Check if index already exists
        existing_indexes = pinecone_client.list_indexes()
        index_names = [index.name for index in existing_indexes]
        
        if index_name in index_names:
            print(f"Index '{index_name}' already exists. Using existing index.")
        else:
            print(f"Creating new index '{index_name}'...")
            pinecone_client.create_index(
                name=index_name,
                dimension=31536, 
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            
        
        # Create vector store
        print("Creating vector store...")
        vector_store = PineconeVectorStore(
            index_name=index_name,
            embedding=embeddings,
            pinecone_api_key=os.getenv("PINECONE_API_KEY")
        )
        
        # Add documents to vector store in batches
        print(f"Adding {len(chunks)} documents to vector store in batches...")
        
        # Process in batches 
        batch_size = 100  
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            try:
                print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} documents)...")
                vector_store.add_documents(batch)
                print(f"✓ Batch {batch_num} completed successfully")
                
                time.sleep(0.5)
                
            except Exception as batch_error:
                print(f"✗ Error in batch {batch_num}: {str(batch_error)}")
                
                # If batch still too large, try smaller batches
                if "message length too large" in str(batch_error):
                    print(f"Batch too large, splitting batch {batch_num} into smaller chunks...")
                    smaller_batch_size = 50
                    for j in range(0, len(batch), smaller_batch_size):
                        small_batch = batch[j:j + smaller_batch_size]
                        try:
                            print(f"  Processing sub-batch {j//smaller_batch_size + 1} ({len(small_batch)} docs)...")
                            vector_store.add_documents(small_batch)
                            time.sleep(0.5)
                        except Exception as small_batch_error:
                            print(f"  ✗ Sub-batch failed: {str(small_batch_error)}")
                            continue
                else:
                    print(f"Continuing with next batch...")
                    continue
        
        print("Data stored successfully in Pinecone.")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise


if __name__ == "__main__":

    data_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    
    store_data_in_pinecone(directory=data_directory)
    print("\n--- Data Ingestion Process Finished ---")