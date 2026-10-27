"""Build gold pages: every rulebook page (after the contents) containing all key phrases."""
import csv, re
from langchain_community.document_loaders import PyPDFLoader
PDF = "/home/meghashyam/Desktop/drone2/retrieval/corpus/easy_access_rules_uas.pdf"
norm = lambda t: re.sub(r"\s+", " ", t.lower())
pages = [(p.metadata["page"] + 1, norm(p.page_content)) for p in PyPDFLoader(PDF).load()]
pages = [(n, t) for n, t in pages if n > 20]          # skip table of contents

rows, out = list(csv.DictReader(open("eval/questions_draft.tsv"), delimiter="\t")), []
for r in rows:
    phrases = [norm(p) for p in r["phrases"].split("|")]
    hits = [n for n, t in pages if all(p in t for p in phrases)]
    flag = "NONE - rephrase key phrase" if not hits else ("TOO MANY - narrow it" if len(hits) > 12 else "ok")
    print(f"{len(hits):>3} pages  {flag:<28} {r['question']}")
    if hits and len(hits) <= 12:
        out.append([r["question"], ";".join(map(str, hits))])

with open("eval/eval_questions.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["question", "gold_pages"]); w.writerows(out)
print(f"\n{len(out)} usable questions written to eval/eval_questions.csv")
