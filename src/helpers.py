# from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter


# def load_data_from_directory(directory, file_type="pdf"):
#     """
#     Load data from directory and return the loaded documents.
#     """
#     loader= DirectoryLoader(directory,
#                             show_progress=True,
#                             glob="**/*.pdf", 
#                             loader_cls=PyPDFLoader)
#     documents = loader.load()

#     return documents

# def split_documents(data):
#     """
#     Splits documents into smaller chunks for processing.
#     """
#     text_spliter = RecursiveCharacterTextSplitter(
#         chunk_size=1000, 
#         chunk_overlap=200, 
#         length_function=len
#     )
    
#     chunks = text_spliter.split_documents(data)
#     return chunks

# def download_embeddings():
#     """
#     Downloads embeddings for the documents in the specified directory.
#     """
#     embeddings = HuggingFaceEmbeddings(
#         model_name="sentence-transformers/all-MiniLM-L6-v2",
#         # model_kwargs={"device": "cuda"}
#     )
#     return embeddings
    

#IMPLEMENTED BETTER CHINKING STRATEGY TO INCREASE RETRIEVAL ACCURACY
import re
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter


def clean_document_content(text):
    """Remove reference patterns that don't contain actual information"""
    patterns_to_remove = [
        r'See page \d+.*?(?=\n|$)',
        r'Refer to .*?page \d+.*?(?=\n|$)', 
        r'For more information, see.*?(?=\n|$)',
        r'Details on page \d+.*?(?=\n|$)',
        r'Please visit.*?(?=\n|$)',
        r'Contact.*?for.*?details.*?(?=\n|$)',
        r'Visit www\.[^\s]+.*?(?=\n|$)',
        r'More details.*?page \d+.*?(?=\n|$)',
        r'Further information.*?page \d+.*?(?=\n|$)',
    ]

    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Clean up formatting issues
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  
    text = re.sub(r' +', ' ', text)                
    text = re.sub(r'\n ', '\n', text) 
    
    return text.strip()


def load_data_from_directory(directory, file_type="pdf"):
    """
    Load data from directory, clean content, and return the loaded documents.
    """
    loader = DirectoryLoader(directory,
                            show_progress=True,
                            glob="**/*.pdf", 
                            loader_cls=PyPDFLoader)
    documents = loader.load()
    
    print(f"Cleaning {len(documents)} documents...")
    cleaned_documents = []
    for doc in documents:
        cleaned_doc = doc.copy()
        cleaned_doc.page_content = clean_document_content(doc.page_content)
        cleaned_documents.append(cleaned_doc)
    
    print("Document cleaning completed.")
    return cleaned_documents


def split_documents(documents):
    """
    Split cleaned documents into optimized chunks for better retrieval.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,   
        chunk_overlap=300,   
        length_function=len,
        separators=[
            "\n\n\n",         
            "\n\n",         
            "\n",         
            ". ",         
            " "           
        ]
    )
    
    print(f"Splitting {len(documents)} documents into chunks...")
    chunks = text_splitter.split_documents(documents)
    
 
    processed_chunks = []
    skipped_count = 0
    
    for chunk in chunks:
        content = chunk.page_content.strip()
        
        if (content.startswith(("See page", "Refer to", "For more", "Visit www", "Contact")) or
            len(content) < 50):
            skipped_count += 1
            continue
            
        processed_chunks.append(chunk)
    
    print(f"Created {len(processed_chunks)} chunks (skipped {skipped_count} reference-only chunks)")
    return processed_chunks


def download_embeddings():
    """
    Downloads embeddings for the documents in the specified directory.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        # model_kwargs={"device": "cuda"}
    )
    return embeddings



# def download_embeddings():
#     """
#     Downloads embeddings for the documents in the specified directory.
#     """
#     embeddings = OpenAIEmbeddings(
#         model="text-embedding-3-small",
#         # model_kwargs={"device": "cuda"}
#     )
#     return embeddings