from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

BASE = os.path.dirname(__file__)
PDF_PATH = os.path.join(BASE, "corpus", "easy_access_rules_uas.pdf")
INDEX_PATH = os.path.join(BASE, "faiss_index")

print(f"Loading PDF from {PDF_PATH}...")
loader = PyPDFLoader(PDF_PATH)
pages = loader.load()
print(f"Loaded {len(pages)} pages.")

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(pages)
print(f"Split into {len(chunks)} chunks.")

print("Loading embedding model (first run downloads ~90MB)...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

print("Building FAISS index (this may take a few minutes for 600 pages)...")
db = FAISS.from_documents(chunks, embeddings)
db.save_local(INDEX_PATH)
print(f"Saved index to {INDEX_PATH}")

print("\n--- Sample chunk ---")
print(chunks[0].page_content[:300])
