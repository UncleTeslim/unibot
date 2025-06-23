from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter


def load_data_from_directory(data):
    """
    Load data from directory and return the loaded documents.
    """
    loader= DirectoryLoader(data,
                            glob="**/*.pdf", 
                            loader_cls=PyPDFLoader)
    documents = loader.load()

    return documents

def split_documents(data):
    """
    Splits documents into smaller chunks for processing.
    """
    text_spliter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200, 
        length_function=len
    )
    
    chunks = text_spliter.split_documents(data)
    return chunks

def download_embeddings():
    """
    Downloads embeddings for the documents in the specified directory.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        # model_kwargs={"device": "cuda"}
    )
    return embeddings
    
