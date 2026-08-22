from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings
import os
import time

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

print("Setting up Cohere embeddings...")
embeddings = CohereEmbeddings(model="embed-english-v3.0")

BATCH_SIZE = 90  # stay under 100 calls/min trial limit
db = None

print(f"Building FAISS index in batches of {BATCH_SIZE} (trial rate limit: 100/min)...")
for i in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[i:i + BATCH_SIZE]
    print(f"  Embedding batch {i // BATCH_SIZE + 1} ({i}-{i+len(batch)} of {len(chunks)})...")
    if db is None:
        db = FAISS.from_documents(batch, embeddings)
    else:
        db.add_documents(batch)
    if i + BATCH_SIZE < len(chunks):
        time.sleep(65)  # wait out the per-minute limit before next batch

db.save_local(INDEX_PATH)
print(f"Saved index to {INDEX_PATH}")

print("\n--- Sample chunk ---")
print(chunks[0].page_content[:300])
