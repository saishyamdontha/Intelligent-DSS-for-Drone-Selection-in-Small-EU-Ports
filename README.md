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
uvicorn index:app --reload --port 8003
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
Uses **Groq API** with **Llama 3.3 70B** model for:
- Explaining why top drone was selected
- Describing strengths of each ranked drone
- Explaining why drones were eliminated
- Get free API key at: https://console.groq.com

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
