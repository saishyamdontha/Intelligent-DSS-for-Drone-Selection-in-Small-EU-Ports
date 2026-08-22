from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS
import os

BASE = os.path.dirname(__file__)
INDEX_PATH = os.path.join(BASE, "faiss_index")

embeddings = CohereEmbeddings(model="embed-english-v3.0")
db = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

def retrieve(query: str, k: int = 4):
    docs = db.similarity_search(query, k=k)
    return [{"content": d.page_content, "page": d.metadata.get("page")} for d in docs]

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "What is the open category weight limit?"
    results = retrieve(query)
    print(f"Query: {query}\n")
    for i, r in enumerate(results, 1):
        print(f"--- Result {i} (page {r['page']}) ---")
        print(r['content'][:300])
        print()
