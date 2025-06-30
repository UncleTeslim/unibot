# from dotenv import load_dotenv
# from flask import Flask, request, jsonify, render_template
# import os
# import langchain
# import logging
# print("=== STARTING FLASK APP ===")

# from src.helpers import download_embeddings
# from src.prompt import *

# from langchain_pinecone import PineconeVectorStore

# from langchain_google_genai import ChatGoogleGenerativeAI

# # from langchain_openai import ChatOpenAI
# from langchain_core.globals import set_llm_cache
# from langchain_community.cache import InMemoryCache
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains import create_retrieval_chain
# from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.messages import HumanMessage, SystemMessage
# print("=== IMPORTS SUCCESSFUL ===")


# set_llm_cache(InMemoryCache())
# load_dotenv()

# app = Flask(__name__) 

# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash-lite",
#     temperature=1.0,
#     max_retries=2,
#     google_api_key=GEMINI_API_KEY,
#     # openai_api_key=OPENAI_API_KEY,
#     max_tokens=1000,
# )

# embeddings = download_embeddings()
# index_name = "unibot"

# docsearch = PineconeVectorStore.from_existing_index(
#     index_name=index_name,
#     embedding=embeddings,
# )
# print("=== PINECONE CONNECTED ===")

# retriever = docsearch.as_retriever(
#     search_type="similarity",
#     search_kwargs={"k": 10}
# )

# prompt = ChatPromptTemplate.from_messages([
#     ("system", f"{system_prompt}\n\nUse the following context to answer: {{context}}"),
#     ("human", "{input}"),
# ])



# qa_chain = create_stuff_documents_chain(
#     llm=llm,
#     prompt=prompt)

# rag_chain = create_retrieval_chain(retriever,qa_chain)


# @app.route('/')
# def index():
#     print("=== INDEX ROUTE CALLED ===")
#     return render_template('index.html')

# @app.route('/health')
# def health():
#     return "App is running!"

# @app.route('/chat', methods=['POST'])
# def chat():
#     data = request.get_json()
#     user_message = data.get('message', '')
    
#     # Use your existing RAG chain
#     result = rag_chain.invoke({"input": user_message})
    
#     return jsonify({
#         'answer': result['answer'],
#         'question': result['input']
#     })


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))




from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import os
import langchain
import logging

print("=== STARTING FLASK APP ===")

try:
    from src.helpers import download_embeddings
    print("=== src.helpers imported successfully ===")
except Exception as e:
    print(f"=== ERROR importing src.helpers: {e} ===")
    raise

try:
    from src.prompt import *
    print("=== src.prompt imported successfully ===")
except Exception as e:
    print(f"=== ERROR importing src.prompt: {e} ===")
    raise

try:
    from langchain_pinecone import PineconeVectorStore
    print("=== langchain_pinecone imported ===")
except Exception as e:
    print(f"=== ERROR importing langchain_pinecone: {e} ===")
    raise

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("=== langchain_google_genai imported ===")
except Exception as e:
    print(f"=== ERROR importing langchain_google_genai: {e} ===")
    raise

try:
    from langchain_openai import OpenAIEmbeddings
    print("=== langchain_openai imported ===")
except Exception as e:
    print(f"=== ERROR importing langchain_openai: {e} ===")
    raise

try:
    from langchain_core.globals import set_llm_cache
    from langchain_community.cache import InMemoryCache
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_retrieval_chain
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import HumanMessage, SystemMessage
    print("=== All langchain imports successful ===")
except Exception as e:
    print(f"=== ERROR importing langchain components: {e} ===")
    raise

print("=== ALL IMPORTS SUCCESSFUL ===")

print("=== SETTING UP CACHE ===")
set_llm_cache(InMemoryCache())

print("=== LOADING ENV VARIABLES ===")
load_dotenv()

print("=== CREATING FLASK APP ===")
app = Flask(__name__) 

print("=== GETTING ENVIRONMENT VARIABLES ===")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Debug environment variables
print(f"=== PINECONE_API_KEY: {'SET' if PINECONE_API_KEY else 'NOT SET'} ===")
print(f"=== GEMINI_API_KEY: {'SET' if GEMINI_API_KEY else 'NOT SET'} ===")

if PINECONE_API_KEY:
    print(f"=== PINECONE_API_KEY starts with: {PINECONE_API_KEY[:8]}... ===")
if GEMINI_API_KEY:
    print(f"=== GEMINI_API_KEY starts with: {GEMINI_API_KEY[:8]}... ===")

print("=== CREATING GEMINI LLM ===")
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        temperature=1.0,
        max_retries=2,
        google_api_key=GEMINI_API_KEY,
        max_tokens=1000,
    )
    print("=== GEMINI LLM CREATED SUCCESSFULLY ===")
except Exception as e:
    print(f"=== ERROR creating Gemini LLM: {e} ===")
    raise

print("=== DOWNLOADING EMBEDDINGS ===")
try:
    embeddings = download_embeddings()
    print("=== EMBEDDINGS DOWNLOADED SUCCESSFULLY ===")
except Exception as e:
    print(f"=== ERROR downloading embeddings: {e} ===")
    raise

print("=== SETTING UP PINECONE ===")
index_name = "unibot"
print(f"=== Using index name: {index_name} ===")

try:
    docsearch = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embeddings,
    )
    print("=== PINECONE VECTOR STORE CREATED SUCCESSFULLY ===")
except Exception as e:
    print(f"=== ERROR creating Pinecone vector store: {e} ===")
    raise

print("=== PINECONE CONNECTED ===")

print("=== CREATING RETRIEVER ===")
try:
    retriever = docsearch.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10}
    )
    print("=== RETRIEVER CREATED SUCCESSFULLY ===")
except Exception as e:
    print(f"=== ERROR creating retriever: {e} ===")
    raise

print("=== CREATING PROMPT TEMPLATE ===")
try:
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"{system_prompt}\n\nUse the following context to answer: {{context}}"),
        ("human", "{input}"),
    ])
    print("=== PROMPT TEMPLATE CREATED SUCCESSFULLY ===")
except Exception as e:
    print(f"=== ERROR creating prompt template: {e} ===")
    raise

print("=== CREATING QA CHAIN ===")
try:
    qa_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=prompt)
    print("=== QA CHAIN CREATED SUCCESSFULLY ===")
except Exception as e:
    print(f"=== ERROR creating QA chain: {e} ===")
    raise

print("=== CREATING RAG CHAIN ===")
try:
    rag_chain = create_retrieval_chain(retriever, qa_chain)
    print("=== RAG CHAIN CREATED SUCCESSFULLY ===")
except Exception as e:
    print(f"=== ERROR creating RAG chain: {e} ===")
    raise

print("=== ALL INITIALIZATION COMPLETE ===")

@app.route('/')
def index():
    print("=== INDEX ROUTE CALLED ===")
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"=== ERROR in index route: {e} ===")
        return f"Error loading page: {e}"

@app.route('/health')
def health():
    print("=== HEALTH ROUTE CALLED ===")
    return {"status": "ok", "message": "App is running!"}

@app.route('/chat', methods=['POST'])
def chat():
    print("=== CHAT ROUTE CALLED ===")
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        print(f"=== User message: {user_message} ===")
        
        result = rag_chain.invoke({"input": user_message})
        print("=== RAG CHAIN INVOKED SUCCESSFULLY ===")
        
        return jsonify({
            'answer': result['answer'],
            'question': result['input']
        })
    except Exception as e:
        print(f"=== ERROR in chat route: {e} ===")
        return jsonify({"error": str(e)}), 500

print("=== FLASK ROUTES DEFINED ===")

if __name__ == '__main__':
    print("=== STARTING FLASK SERVER ===")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
else:
    print("=== FLASK APP READY FOR GUNICORN ===")