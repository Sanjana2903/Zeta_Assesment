from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings 
from langchain_community.vectorstores import Chroma


# Initialize LLM (chat model)
llm = ChatOllama(model="llama3")

# Embedding model used during ingestion
embedding = OllamaEmbeddings(model="mxbai-embed-large")

# Load persisted Chroma vector DB
vectorstore = Chroma(
    persist_directory="db",
    embedding_function=embedding
)

# Satya-style prompt
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a digital twin of Satya Nadella, trained on his blogs and public writing.

Respond as Satya would: grounded in empathy, innovation, and purpose-driven leadership.
Paraphrase from his writings and add contextual reasoning.

Context:
{context}

Q: What would Satya Nadella advise about: {question}?
A:"""
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt}
)

def ask_nadella(question: str):
    return qa_chain.run(question)

if __name__ == "__main__":
    print("Ask 'Satya Nadella' anything based on his blogs.")
    while True:
        q = input("\nAsk Satya Twin >> ")
        if q.lower().strip() in {"exit", "quit"}:
            print("Exiting...")
            break
        print("\nResponse:\n")
        print(ask_nadella(q))
