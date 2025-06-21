#Extracts text content from PDF files using LangChain's PyMuPDFLoader

from langchain_community.document_loaders import PyMuPDFLoader
def extract_text(file_path: str):
    try:
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
        return docs
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")
