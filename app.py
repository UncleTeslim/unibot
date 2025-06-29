from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import os
import langchain


# from src.store_data import store_data_in_pinecone
# from src.retrieve_data import docsearch
from src.helpers import download_embeddings
from src.prompt import *

from langchain_pinecone import PineconeVectorStore

# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage



set_llm_cache(InMemoryCache())
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-4.1-nano",
    temperature=1.0,
    max_retries=2,
    openai_api_key=OPENAI_API_KEY,
    max_tokens=1000,
)

embeddings = download_embeddings()
index_name = "unibot"

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings,
)

retriever = docsearch.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

prompt = ChatPromptTemplate.from_messages([
    ("system", f"{system_prompt}\n\nUse the following context to answer: {{context}}"),
    ("human", "{input}"),
])



qa_chain = create_stuff_documents_chain(
    llm=llm,
    prompt=prompt)

rag_chain = create_retrieval_chain(retriever,qa_chain)


result = rag_chain.invoke({"input": "tell me about the Msc digital marketing programme?? Whata is the tuition?"})
print("Question:", result['input'])
print("Answer:", result['answer'])
print(f"Retrieved {len(result['context'])} documents")