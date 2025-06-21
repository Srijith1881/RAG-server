
# Handles chunking and embedding documents using LangChain + ChromaDB.

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
import os
from rag_module.rag_chain import get_embedding

embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

def index_document(docs):
    try:
        persist_dir = "./chroma_db"
        os.makedirs(persist_dir, exist_ok=True)

        # Split documents into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = splitter.split_documents(docs)

        # Check if DB already exists
        if os.path.exists(os.path.join(persist_dir, "index")):
            vectorstore = Chroma(
                embedding_function=get_embedding(),
                persist_directory=persist_dir
            )
            vectorstore.add_documents(splits)
        else:
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=embedding,
                persist_directory=persist_dir
            )

        vectorstore.persist()

    except Exception as e:
        raise RuntimeError(f"Failed to index document: {e}")
