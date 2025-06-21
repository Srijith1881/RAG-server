
# Defines the RAG chain

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain import hub
from dotenv import load_dotenv
load_dotenv()

def get_embedding():
    return HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
prompt = hub.pull("rlm/rag-prompt")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")
parser = StrOutputParser()

def get_vectorstore():
    # Loads existing Chroma vector store from disk
    embedding = get_embedding()
    return Chroma(
        embedding_function=embedding,
        persist_directory="./chroma_db"
    )

def create_chain_from_retriever(retriever):
    # Builds the RAG chain from the retriever, prompt, LLM, and parser.
    def format_docs(docs): return "\n".join(doc.page_content for doc in docs)
    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | parser
    )
