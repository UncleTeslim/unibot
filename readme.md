# UniBot - University RAG System

A production-ready Retrieval-Augmented Generation (RAG) system that provides intelligent answers to university-related questions using official university documents. Built with Flask, LangChain, Pinecone, and Google Gemini.

## 🎯 Overview

UniBot is an AI-powered assistant that helps students and prospective students get accurate information about university courses, requirements, fees, and policies. Instead of searching through lengthy PDF documents, users can ask natural language questions and get precise, contextual answers backed by official documentation.

## ✨ Features

- **Intelligent Q&A**: Natural language queries about courses, entry requirements, fees, deadlines
- **Document-Grounded Responses**: All answers sourced from official university documents
- **Smart Content Processing**: Removes unhelpful references like "see page X" from responses
- **Optimized Chunking**: Advanced document processing for better context retrieval
- **Batch Processing**: Handles large document collections efficiently
- **Multiple LLM Support**: Compatible with OpenAI, Google Gemini, and other providers
- **Flexible Embeddings**: Support for HuggingFace, OpenAI, and Gemini embeddings
- **RESTful API**: Easy integration with web applications and mobile apps
- **Docker Ready**: Optimized containerization for production deployment

## 🛠️ Tech Stack

- **Framework**: Flask (Python web framework)
- **LLM**: Google Gemini (gemini-1.5-flash) or OpenAI GPT-4
- **Vector Database**: Pinecone
- **Embeddings**: HuggingFace (sentence-transformers) or Google Gemini
- **Document Processing**: LangChain + PyPDF
- **Environment Management**: python-dotenv
- **Containerization**: Docker with multi-stage builds

## 📁 Project Structure

```
unibot/
├── app.py                    # Main Flask application

├── requirements.txt         # Python dependencies
├── .env                    # Environment variables (not in repo)
├── README.md              # This file
├── data/                  # University PDF documents
│   ├── prospectus_2025.pdf
│   ├── course_guide.pdf
│   └── admissions_info.pdf
├── static
│   ├── script.js           #JavaScript froentend
│   └── style.css          #CSS frontend
├── templates
│   └── index.html         #HTML frontend
│
└── src/
    ├── helpers.py         # Document processing utilities
    ├── prompt.py          # System prompt
    └── store_data.py    # Data ingestion with batch processing
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Pinecone account and API key
- Google AI Studio API key (for Gemini) or OpenAI API key

### Local Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/UncleTeslim/unibot.git
   cd unibot
   ```

2. **Create virtual environment**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:

   ```env
   PINECONE_API_KEY=your_pinecone_api_key
   GEMINI_API_KEY=your_gemini_api_key
   # Optional: for OpenAI
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Add your documents**
   Place PDF files in the `data/` directory

6. **Ingest documents into Pinecone**

   ```bash
   python store_data.py
   ```

7. **Run the application**
   ```bash
   python app.py
   ```
