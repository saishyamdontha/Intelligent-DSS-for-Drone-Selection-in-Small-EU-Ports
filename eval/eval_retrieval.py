"""Page-level retrieval evaluation for the EASA RAG index, with a BM25 baseline and fix options."""
import argparse, csv, re
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings
from rank_bm25 import BM25Okapi

ap = argparse.ArgumentParser()
ap.add_argument("--index", default="retrieval/faiss_index")
ap.add_argument("--questions", default="eval/eval_questions.csv")
ap.add_argument("--k", type=int, default=4)
ap.add_argument("--offset", type=int, default=1)
ap.add_argument("--dedupe", action="store_true", help="keep only the first chunk per page")
ap.add_argument("--skip-front", type=int, default=0, help="drop pages <= N (front matter)")
args = ap.parse_args()

vs = FAISS.load_local(args.index, CohereEmbeddings(model="embed-english-v3.0"),
                      allow_dangerous_deserialization=True)
docs = list(vs.docstore._dict.values())
tok = lambda t: re.findall(r"[a-z0-9]+", t.lower())
bm25 = BM25Okapi([tok(d.page_content) for d in docs])
page = lambda d: int(d.metadata["page"]) + args.offset

def postprocess(pages, k):
    out = []
    for p in pages:
        if p <= args.skip_front or (args.dedupe and p in out): continue
        out.append(p)
        if len(out) == k: break
    return out

def dense(q, k): return postprocess([page(d) for d in vs.similarity_search(q, k=k * 5)], k)
def keyword(q, k):
    s = bm25.get_scores(tok(q))
    top = sorted(range(len(docs)), key=lambda i: s[i], reverse=True)[:k * 5]
    return postprocess([page(docs[i]) for i in top], k)

rows = list(csv.DictReader(open(args.questions)))
methods = [("dense (Cohere + FAISS)", dense), ("keyword (BM25)", keyword)]
res = {m: {"rank": [], "near": []} for m, _ in methods}
misses = []
for r in rows:
    gold = {int(p) for p in r["gold_pages"].split(";")}
    for name, fn in methods:
        pages = fn(r["question"], args.k)
        rank = next((i + 1 for i, p in enumerate(pages) if p in gold), None)
        res[name]["rank"].append(rank)
        res[name]["near"].append(any(abs(p - g) <= 1 for p in pages for g in gold))
        if name.startswith("dense") and rank is None:
            misses.append((r["question"], sorted(gold), pages))

n = len(rows)
print(f"{n} questions, top-{args.k}, dedupe={args.dedupe}, skip_front={args.skip_front}\n")
print(f"{'method':<24}{'hit@1':>8}{'hit@'+str(args.k):>8}{'MRR':>8}{'  ±1 page':>10}")
for name, d in res.items():
    rk = d["rank"]
    print(f"{name:<24}{sum(x == 1 for x in rk)/n:>8.0%}{sum(x is not None for x in rk)/n:>8.0%}"
          f"{sum(1/x for x in rk if x)/n:>8.2f}{sum(d['near'])/n:>10.0%}")
print("\nDense misses (question | gold | retrieved):")
for q, g, p in misses: print(f"- {q} | {g} | {p}")
