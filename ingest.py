from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

with open("satya_data/blogs.txt", "r") as f:
    raw_text = f.read()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = splitter.create_documents([raw_text])

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=OllamaEmbeddings(model="mxbai-embed-large"),
    persist_directory="db"
)
vectorstore.persist()
print("Blog ingestion complete.")
