# Agentic Chat Assistant with Digital Twin (Satya Nadella)

A multi-agent conversational assistant built with LangChain and Streamlit, featuring a **Generic AI agent** and a **Digital Twin of Satya Nadella** that responds using Satya’s real public content with paraphrased answers and contextual reasoning.

---

## Problem Approach

Traditional assistants provide generic answers that often lack tone, source grounding, or context. This project tackles that by combining:

- **Agent-specific reasoning**: Each agent (e.g., Satya Nadella Twin) brings a unique knowledge and communication style.
- **Retrieval-Augmented Generation (RAG)**: Satya’s responses are grounded in his real blog posts using a vector store and retrieval chain.
- **User-directed control**: Users can choose which agent(s) to respond per question.


### Key Components:
- **Streamlit UI**: For chat interactions and agent selection.
- **Generic Agent**: Uses ChatOllama LLM and conversation memory.
- **Satya Twin Agent**: Uses LangChain’s RetrievalQA over ChromaDB to quote Satya’s blog posts.
- **Chroma Vector Store**: Stores chunked embeddings of Satya’s writing.
- **LangChain Tools**: Google Search, YouTube search, GitHub issues (for future extensibility).

---

## Tool Choices

| Component         | Tool/Library                  | Why? |
|------------------|-------------------------------|------|
| UI               | Streamlit                     | Easy chat-based UI with session state |
| LLM              | Ollama (LLaMA 3) via LangChain | Fast local inference |
| Vector Store     | Chroma                        | Fast, lightweight local retrieval |
| Embeddings       | `mxbai-embed-large` via Ollama| Works well for long-form semantic search |
| Agent Orchestration | LangChain Agents + Chains     | Handles LLM logic, memory, and RAG |
| Docs Ingestion   | LangChain TextSplitter        | Creates clean, overlapping semantic chunks |
| Deployment       | Local or cloud (e.g., Hugging Face Spaces) | Plug-and-play ready |

---

## Setup Instructions

### 1. Clone the Repo

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```
### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the root directory and add your Youtube API key, Google API key and GitHub token for issue search:

```bash
touch .env
```
### 5. Download and Run Ollama Llama3

Make sure you have Ollama installed: https://ollama.com
```bash
ollama serve
ollama pull llama3
ollama run mxbai-embed-large
```
### 6. Run the streamlit app
```bash
streamlit run ui.py
```

---


### Project Highlights
- Dynamic agent selection per question
- Contextual memory for generic agent
- Satya twin only responds using real sources
- Expandable to support more public figures as digital twins


