# Intelligent DSS for Drone Selection in Small EU Ports
**Course:** DV2573 — Decision Support Systems  
**Institution:** Blekinge Institute of Technology  
**Team:** Sriya Chittaneni, Sri Sumedh Pisapati, Meghashyam Sai Dontha, Daiki Saito, Venkata Naga Sai Yaswanth Deevi

---

## Project Overview

An Intelligent Decision Support System (DSS) that helps port administrators select the most suitable drone for their specific port scenario using:

- **AHP** (Analytic Hierarchy Process) — criteria weighting
- **TOPSIS** (Technique for Order Preference by Similarity to Ideal Solution) — drone ranking
- **Knowledge Base** — EU regulatory rules + operational constraints
- **Monte Carlo Sensitivity Analysis** — ranking stability testing
- **Groq AI (RAG)** — natural language explanation of decisions
- **Country Regulations** — EU member state specific drone laws

---

## Project Structure

```
dss_project/
├── backend/
│   ├── main.py                    ← FastAPI app — all endpoints
│   ├── ahp.py                     ← AHP criteria weighting
│   ├── topsis.py                  ← TOPSIS drone ranking
│   ├── knowledge_base.py          ← Rule-based drone filtering
│   ├── sensitivity_analysis.py    ← Monte Carlo simulation
│   ├── rag_service.py             ← Groq AI explanation
│   ├── country_regulations.py     ← EU country drone laws
│   ├── drone_dataset.json         ← 20 commercial drones
│   ├── port_scenarios.json        ← 5 port scenarios
│   ├── ahp_pairwise_matrix.json   ← AHP comparison matrix
│   └── knowledge_base_rules.json  ← 22 KB rules
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── SetupPage.tsx       ← Port scenario setup
    │   │   ├── CriteriaPage.tsx    ← AHP matrix input
    │   │   ├── ResultsPage.tsx     ← TOPSIS rankings + AI
    │   │   ├── SensitivityPage.tsx ← Monte Carlo results
    │   │   └── ComparePage.tsx     ← Side-by-side comparison
    │   ├── components/
    │   │   └── AIExplanation.tsx   ← Groq AI chat widget
    │   └── services/
    │       └── api.ts              ← Backend API calls
    └── package.json
```

---

## How to Run

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key (free at https://console.groq.com)

### Step 1 — Backend
```bash
cd backend
pip install fastapi uvicorn numpy groq
uvicorn main:app --reload --port 8001
```

Backend runs at: **http://localhost:8001**  
API docs at: **http://localhost:8001/docs**

### Step 2 — Frontend
```bash
cd frontend
npm install
npx vite
```

Frontend runs at: **http://localhost:5173**

### Step 3 — Set Groq API Key
Open `backend/rag_service.py` and set your key on line 12:
```python
GROQ_API_KEY = "your_groq_api_key_here"
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | System info |
| GET | `/drones` | All 20 drones |
| GET | `/scenarios` | All 5 port scenarios |
| GET | `/ahp` | AHP weights + consistency ratio |
| GET | `/rules` | All 22 knowledge base rules |
| GET | `/criteria` | 20 criteria with weights |
| GET | `/countries` | 14 EU countries |
| GET | `/countries/{code}` | Country regulations |
| POST | `/evaluate` | Full AHP + TOPSIS evaluation |
| POST | `/explain` | Evaluation + AI explanation |
| POST | `/chat` | Follow-up AI questions |
| POST | `/evaluate/country` | Country-specific evaluation |

---

## Dataset

**20 commercial drones** including:
- DJI Matrice 350 RTK
- Nordic Drones ND-800
- Percepto Sparrow
- Wingtra WingtraOne GEN II
- Quantum Systems Trinity F90+
- senseFly eBee X
- And 14 more...

**Evaluated across 20 criteria:**
Flight time, flight range, night vision, payload capacity, camera quality, autonomy level, weather resistance, real-time transmission, obstacle avoidance, GPS accuracy, battery swappable, maintenance requirements, initial cost, operational cost, regulatory compliance, integration capability, sensor compatibility, data storage, launch/recovery method, redundancy/failsafe.

---

## Port Scenarios

| ID | Name | Mission |
|---|---|---|
| S01 | Coastal Surveillance — Small Fishing Port | Surveillance |
| S02 | 24/7 Security — Medium Container Port | Security |
| S03 | Infrastructure Inspection — Ferry Terminal | Inspection |
| S04 | Environmental Monitoring — Eco Port | Environmental |
| S05 | Emergency Response — Multi-Purpose Port | Emergency |

---

## EU Countries Supported

🇸🇪 Sweden · 🇩🇪 Germany · 🇫🇷 France · 🇳🇱 Netherlands · 🇪🇸 Spain · 🇮🇹 Italy · 🇵🇱 Poland · 🇩🇰 Denmark · 🇫🇮 Finland · 🇳🇴 Norway · 🇧🇪 Belgium · 🇵🇹 Portugal · 🇬🇷 Greece · 🇭🇷 Croatia

---

## Methodology

### AHP (Analytic Hierarchy Process)
- 20x20 pairwise comparison matrix using Saaty scale (1-9)
- Consistency Ratio must be < 0.10
- Produces criteria weights for TOPSIS

### TOPSIS
- Vector normalisation of decision matrix
- Weighted normalised matrix using AHP weights
- Positive Ideal Solution (PIS) and Negative Ideal Solution (NIS)
- Closeness Coefficient CCi = D⁻ / (D⁺ + D⁻)
- Higher CCi = better drone

### Knowledge Base
- 5 regulatory rules (EU 2019/947, EASA)
- 10 operational rules (flight time, range, weather, budget)
- 4 soft constraints (maintenance, training, obstacle avoidance)
- 3 expert recommendations (tethered, fixed-wing, automated dock)

### Sensitivity Analysis
- Monte Carlo simulation (100 runs)
- ±20% weight perturbation
- Stability: HIGH (≥70%), MEDIUM (40-70%), LOW (<40%)

---

## References

- Saaty & Vargas (2012) — AHP methodology
- Hwang & Yoon — TOPSIS methodology
- EU 2019/947 — Drone regulations
- EU 2019/945 — Drone categories
- EASA — European Aviation Safety Agency

---

## License

Academic project — Blekinge Institute of Technology, 2026
