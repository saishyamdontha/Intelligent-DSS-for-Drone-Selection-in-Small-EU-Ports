# Intelligent DSS for Drone Selection in Small EU Ports

**Course:** DV2573 — Decision Support Systems  
**Institution:** Blekinge Institute of Technology  
**Supervisor:** Lawrence Henesey  

---

## Live Demo
**Frontend:** https://intelligent-dss-for-drone-selection-sandy.vercel.app  
**Backend API:** https://intelligent-dss-for-drone-selection-in.onrender.com  
**API Docs:** https://intelligent-dss-for-drone-selection-in.onrender.com/docs  

---

## Overview
An Intelligent Decision Support System that helps EU port administrators select the most suitable drone using:
- **AHP** — Analytic Hierarchy Process (criteria weighting)
- **TOPSIS** — Technique for Order Preference by Similarity to Ideal Solution (ranking)
- **Knowledge Base** — 22 rules from EU regulations + operational constraints
- **Monte Carlo** — Sensitivity analysis (300 simulations)
- **Groq AI** — Natural language explanation of decisions

---

##  System Architecture
	PORT SCENARIOS + DRONE DATASET + PAIRWISE MATRIX
		↓
		KNOWLEDGE BASE FILTER (22 rules)
			↓
			AHP (criteria weights, CR=0.0159)
				↓
				TOPSIS (drone ranking)
					↓
					SENSITIVITY ANALYSIS (300 simulations)
						↓
						AI EXPLANATION (Groq Llama 3.3)
							↓
							DASHBOARD (results)
##  Project Structure
├── api/
│   ├── index.py                  ← FastAPI backend
│   ├── drone_dataset.json        ← 20 commercial drones
│   ├── port_scenarios.json       ← 5 port scenarios
│   ├── ahp_pairwise_matrix.json  ← 20x20 AHP matrix
│   ├── knowledge_base_rules.json ← 22 KB rules
│   └── requirements.txt
└── public/
└── index.html                ← Frontend UI

---

## How to Run Locally

### Backend
```bash
cd api
pip install -r requirements.txt
export GROQ_API_KEY=your_groq_api_key_here
export COHERE_API_KEY=your_cohere_api_key_here
export LLM_PROVIDER=ollama
uvicorn index:app --reload --port 8003
```

To build the RAG index locally (one-time):
```bash
export COHERE_API_KEY=your_cohere_api_key_here
python3 retrieval/ingest.py
```

### Frontend
```bash
cd public
python3 -m http.server 8081
```
Open: http://localhost:8081

---

## Dataset
- **20 commercial drones** — DJI, Parrot, Autel, Wingtra, Skydio, Nordic Drones etc.
- **20 decision criteria** — flight time, range, camera, payload, weather resistance etc.
- **5 port scenarios** — surveillance, security, inspection, environmental, emergency

---

## Port Scenarios
| ID  | Scenario | Mission | Budget |
|-----|--------------------------------------------------|---------------|---------|
| S01 | Coastal Surveillance — Small Fishing Port        | Surveillance  | €8,000  |
| S02 | 24/7 Security — Medium Container Port            | Security      | €30,000 |
| S03 | Infrastructure Inspection — Ferry Terminal       | Inspection    | €20,000 |
| S04 | Environmental Monitoring — Eco Port              | Environmental | €25,000 |
| S05 | Emergency Response — Multi-Purpose Port          | Emergency     | €35,000 |

---

## API Endpoints
| Method | Endpoint | Description |
|------|---------------------------------|-------------------|
| GET  | `/api/drones`                   | All 20 drones     |
| GET  | `/api/scenarios`                | All 5 scenarios   |
| GET  | `/api/ahp`                      | AHP weights + CR  |
| POST | `/api/evaluate`                 | Full evaluation   |
| POST | `/api/evaluate/custom-scenario` | Custom evaluation |
| POST | `/api/ai/overview`              | AI explanation    |

---

## AI Integration
Provider-agnostic explanation layer — defaults to a **local Ollama model** (`llama3.1:8b`) for development, falls back to **Groq API** (`openai/gpt-oss-120b`) for production, selected via the `LLM_PROVIDER` environment variable. Used for:
- Explaining why top drone was selected
- Describing strengths of each ranked drone
- Explaining why drones were eliminated
- Answering free-form regulatory questions, grounded in retrieved EASA regulation text (see RAG section below)

Get a free Groq API key at: https://console.groq.com | Install Ollama locally at: https://ollama.com

---

## Methodology
### AHP
- 20x20 pairwise comparison matrix (Saaty scale 1-9)
- Consistency Ratio = 0.0159 < 0.10 

### TOPSIS
- Vector normalization
- Weighted decision matrix
- Closeness Coefficient: CCi = D⁻ / (D⁺ + D⁻)

### Knowledge Base
- 5 regulatory rules (EASA EU 2019/947)
- 10 operational rules
- 4 soft constraints
- 3 expert recommendations

### Sensitivity Analysis
- 300 Monte Carlo simulations
- ±20% weight perturbation
- HIGH/MEDIUM/LOW stability classification

---

## Retrieval-Augmented Generation (RAG) Layer

Extends the AI explanation layer with grounded, citable answers sourced directly from EU drone regulation text, rather than relying on the LLM's parametric knowledge alone.

### Pipeline
```
EASA Easy Access Rules PDF (617 pages, Reg. 2019/947 + 2019/945)
    ↓
CHUNKING (LangChain RecursiveCharacterTextSplitter, ~500 chars, 50 overlap)
    ↓
EMBEDDING (Cohere embed-english-v3.0, batched for trial rate limits)
    ↓
FAISS VECTOR INDEX (3,600+ chunks, persisted to disk)
    ↓
QUERY-TIME RETRIEVAL (top-k semantic search, k=4)
    ↓
GROUNDED GENERATION (Ollama / Groq, cites source page numbers)
````

### Design notes
- **Static pipeline, not an agent** — retrieval is a fixed, deterministic lookup (embed query → nearest-neighbor search), with no autonomous decision-making. Contrast with AgentDSS, a separate multi-agent project where agents make context-dependent decisions.
- **Provider-agnostic embeddings and generation** — swapping Cohere for another embedding provider, or Ollama for Groq, requires no changes outside `retrieval/retriever.py` and the `LLM_PROVIDER` env var.
- **Grounded, citable output** — every AI-generated answer references the source page number(s) it was drawn from, reducing hallucination risk versus an ungrounded LLM call.

### Files
| Path | Purpose |
|------|---------|
| `retrieval/ingest.py` | One-time: chunks the regulation PDF, embeds via Cohere, builds and saves the FAISS index |
| `retrieval/retriever.py` | Runtime: loads the FAISS index (lazily, on first request) and serves top-k semantic search |
| `retrieval/corpus/` | Source regulation PDF (gitignored — not committed) |
| `retrieval/faiss_index/` | Persisted vector index (committed, since it's lightweight with Cohere embeddings) |

---

## Team
| Name | Student ID |
|---------------------------------|---------------|
| Sriya Chittaneni                | 20030608-5580 |
| Sri Sumedh Pisapati             | 20041015-1518 |
| Meghashyam Sai Dontha           | 20040429-2914 |
| Daiki Saito                     | 20031230-T294 |
| Venkata Naga Sai Yaswanth Deevi | 20040920-4674 |

---

## References
- Saaty & Vargas (2012) — AHP methodology
- Hwang & Yoon — TOPSIS methodology
- EU 2019/947 — Drone regulations
- EASA — European Aviation Safety Agency
