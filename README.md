# Document Q&A Assistant

A Streamlit-based application for querying PDF documents using natural language. Built with RAG (Retrieval-Augmented Generation) technology and Mistral LLM.

## Technologies

- **Frontend**: Streamlit
- **LLM**: Mistral via Ollama
- **Vector Store**: ChromaDB
- **Document Processing**: LangChain, PyPDF
- **Embeddings**: nomic-embed-text

## Requirements

```bash
python >= 3.10
streamlit==1.30.0
langchain==0.1.0
langchain-community==0.0.10
chromadb==0.4.18
pypdf==3.17.1
```

## Getting Started

1. **Clone the Repository**
```bash
git clone <your-repo-url>
cd monopoly_RAG
```

2. **Set Up Python Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
.\venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Ollama and Models**
- Download [Ollama](https://ollama.ai/)
- Install Mistral model:
```bash
ollama pull mistral
ollama pull nomic-embed-text
```

5. **Run the Application**
```bash
streamlit run app.py
```

6. **Using the Application**
- Open `http://localhost:8501`
- Upload PDF documents using the sidebar
- Click "Process Documents"
- Start asking questions about your documents
