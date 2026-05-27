"""
FastAPI Backend — Main Application
DV2573: Intelligent DSS for Drone Selection in Small EU Ports
Blekinge Institute of Technology

Run with: uvicorn main:app --reload --port 8001
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import numpy as np

from ahp import load_matrix_from_dict, compute_ahp, CRITERIA
from topsis import run_topsis
from knowledge_base import apply_knowledge_base, get_rules_summary
from rag_service import generate_explanation, answer_followup
from country_regulations import get_all_countries, get_country_regulations, apply_country_filter
from sensitivity_analysis import run_sensitivity_analysis

# ── Load ALL data files on startup ────────────────────────────────────────────
BASE = os.path.dirname(__file__)

with open(os.path.join(BASE, "drone_dataset.json")) as f:
    DRONE_DATA = json.load(f)

with open(os.path.join(BASE, "port_scenarios.json")) as f:
    SCENARIO_DATA = json.load(f)

with open(os.path.join(BASE, "ahp_pairwise_matrix.json")) as f:
    AHP_DATA = json.load(f)

with open(os.path.join(BASE, "knowledge_base_rules.json")) as f:
    KB_RULES_DATA = json.load(f)

DRONES    = DRONE_DATA["drones"]
SCENARIOS = {s["id"]: s for s in SCENARIO_DATA["scenarios"]}

print(f"Loaded {len(DRONES)} drones")
print(f"Loaded {len(SCENARIOS)} scenarios")
print(f"Loaded AHP matrix for {len(AHP_DATA['criteria'])} criteria")
print(f"Loaded {len(KB_RULES_DATA['regulatory_rules'])} regulatory rules")
print(f"Loaded {len(KB_RULES_DATA['operational_rules'])} operational rules")
print(f"Loaded {len(KB_RULES_DATA['soft_rules'])} soft rules")
print(f"Loaded {len(KB_RULES_DATA['expert_recommendations'])} expert recommendations")

# ── Helper to convert numpy types to Python native types ─────────────────────
def convert_numpy(obj):
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_numpy(i) for i in obj]
    if isinstance(obj, tuple):
        return tuple(convert_numpy(i) for i in obj)
    return obj

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Intelligent DSS — Drone Selection for Small EU Ports",
    description="AHP + TOPSIS + Knowledge Base Decision Support System | DV2573 | BTH",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic models ───────────────────────────────────────────────────────────
class ExplainRequest(BaseModel):
    scenario_id: str
    custom_matrix: Optional[Dict[str, List[float]]] = None
    n_sensitivity_simulations: Optional[int] = 100
    perturbation_pct: Optional[float] = 0.20
    question: Optional[str] = None

class ChatRequest(BaseModel):
    question: str
    evaluation_result: Dict[str, Any]
    chat_history: Optional[List[Dict[str, str]]] = []

class EvaluationRequest(BaseModel):
    scenario_id: str
    custom_matrix: Optional[Dict[str, List[float]]] = None
    n_sensitivity_simulations: Optional[int] = 200
    perturbation_pct: Optional[float] = 0.20

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "system": "Intelligent DSS for Drone Selection in Small EU Ports",
        "course": "DV2573",
        "institution": "Blekinge Institute of Technology",
        "data": {
            "drones":    len(DRONES),
            "scenarios": len(SCENARIOS),
            "criteria":  len(CRITERIA),
            "rules":     get_rules_summary()["total_rules"],
        },
        "endpoints": ["/drones", "/scenarios", "/ahp", "/evaluate", "/rules", "/docs"]
    }


@app.get("/drones")
def get_drones():
    """Return full drone database (20 drones)."""
    return {"count": len(DRONES), "drones": DRONES}


@app.get("/drones/{drone_id}")
def get_drone(drone_id: str):
    """Return a single drone by ID."""
    drone = next((d for d in DRONES if d["id"] == drone_id), None)
    if not drone:
        raise HTTPException(status_code=404, detail=f"Drone '{drone_id}' not found")
    return drone


@app.get("/scenarios")
def get_scenarios():
    """Return all 5 available port scenarios."""
    return {"count": len(SCENARIOS), "scenarios": list(SCENARIOS.values())}


@app.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str):
    """Return a single scenario by ID (S01-S05)."""
    if scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    return SCENARIOS[scenario_id]


@app.get("/ahp")
def get_ahp_weights():
    """Compute and return AHP weights from the default pairwise matrix."""
    matrix = load_matrix_from_dict(AHP_DATA["matrix"], CRITERIA)
    result = compute_ahp(matrix, CRITERIA)
    return convert_numpy(result)


@app.get("/rules")
def get_rules():
    """Return all knowledge base rules loaded from knowledge_base_rules.json."""
    return convert_numpy({
        "metadata":   KB_RULES_DATA["metadata"],
        "summary":    get_rules_summary(),
        "regulatory": KB_RULES_DATA["regulatory_rules"],
        "operational": KB_RULES_DATA["operational_rules"],
        "soft":       KB_RULES_DATA["soft_rules"],
        "expert":     KB_RULES_DATA["expert_recommendations"],
    })


@app.get("/criteria")
def get_criteria():
    """Return all 20 decision criteria with AHP weights."""
    matrix = load_matrix_from_dict(AHP_DATA["matrix"], CRITERIA)
    result = compute_ahp(matrix, CRITERIA)
    weights = convert_numpy(result["weights"])
    return {
        "count": len(CRITERIA),
        "criteria": [
            {
                "id":       c,
                "name":     c.replace("_", " ").title(),
                "weight":   weights[c],
                "notes":    DRONE_DATA["metadata"]["criteria_notes"].get(
                    c if c in DRONE_DATA["metadata"]["criteria_notes"]
                    else c + "_min", ""
                ),
            }
            for c in CRITERIA
        ]
    }


@app.post("/evaluate")
def evaluate(request: EvaluationRequest):
    """
    Full DSS pipeline:
    1. Load scenario from port_scenarios.json
    2. Apply Knowledge Base rules from knowledge_base_rules.json
    3. Compute AHP weights from ahp_pairwise_matrix.json
    4. Run TOPSIS on eligible drones from drone_dataset.json
    5. Run Monte Carlo Sensitivity Analysis
    6. Return ranked results with full explanation
    """
    # 1. Validate scenario
    if request.scenario_id not in SCENARIOS:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario '{request.scenario_id}' not found. Available: {list(SCENARIOS.keys())}"
        )
    scenario = SCENARIOS[request.scenario_id]

    # 2. Knowledge Base filter
    eligible, eliminated = apply_knowledge_base(DRONES, scenario)
    if len(eligible) == 0:
        raise HTTPException(
            status_code=422,
            detail="No drones passed the knowledge base filter. Relax constraints."
        )

    # 3. AHP weights
    matrix_dict = request.custom_matrix if request.custom_matrix else AHP_DATA["matrix"]
    matrix      = load_matrix_from_dict(matrix_dict, CRITERIA)
    ahp_result  = compute_ahp(matrix, CRITERIA)
    ahp_result  = convert_numpy(ahp_result)

    ahp_warning = None
    if not ahp_result["is_consistent"]:
        ahp_warning = (
            f"AHP inconsistency warning: CR={ahp_result['consistency_ratio']:.4f} >= 0.10. "
            "Results may be unreliable."
        )

    weights = ahp_result["weights_array"]

    # 4. TOPSIS ranking
    ranked = run_topsis(eligible, weights, CRITERIA)
    ranked = convert_numpy(ranked)

    # 5. Sensitivity analysis
    np.random.seed(42)
    sensitivity = run_sensitivity_analysis(
        eligible, weights, CRITERIA,
        n_simulations=request.n_sensitivity_simulations,
        perturbation_pct=request.perturbation_pct
    )
    sensitivity = convert_numpy(sensitivity)

    # 6. Build response
    return {
        "scenario": {
            "id":          scenario["id"],
            "name":        scenario["name"],
            "description": scenario["description"],
            "mission":     scenario["mission"]["primary"],
            "environment": scenario["environment"]["location_type"],
        },
        "filter_summary": {
            "total_drones":    len(DRONES),
            "eligible":        len(eligible),
            "eliminated":      len(eliminated),
            "rules_applied":   get_rules_summary()["total_rules"],
            "eliminated_drones": eliminated,
        },
        "ahp": {
            "consistency_ratio":        ahp_result["consistency_ratio"],
            "lambda_max":               ahp_result["lambda_max"],
            "is_consistent":            ahp_result["is_consistent"],
            "warning":                  ahp_warning,
            "top5_criteria_by_weight":  sorted(
                ahp_result["weights"].items(), key=lambda x: -x[1]
            )[:5],
        },
        "ranking": ranked,
        "sensitivity": sensitivity,
        "recommendation": {
            "top_drone":            ranked[0]["name"],
            "top_drone_id":         ranked[0]["id"],
            "manufacturer":         ranked[0]["manufacturer"],
            "closeness_coefficient": ranked[0]["closeness_coefficient"],
            "stability": next(
                (r["stability"] for r in sensitivity["results"] if r["id"] == ranked[0]["id"]),
                "UNKNOWN"
            ),
            "eliminated_count": len(eliminated),
            "eligible_count":   len(eligible),
            "explanation": (
                f"{ranked[0]['name']} ranked #1 with closeness coefficient "
                f"{ranked[0]['closeness_coefficient']:.4f} for the "
                f"'{scenario['name']}' scenario. "
                f"{len(eliminated)} of {len(DRONES)} drones were eliminated by "
                f"Knowledge Base rules. "
                f"It outperformed {len(eligible)-1} eligible drones across {len(CRITERIA)} criteria."
            )
        }
    }

@app.post("/explain")
def explain(request: ExplainRequest):
    """Full DSS pipeline + RAG AI explanation."""
    if request.scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario not found")
    scenario = SCENARIOS[request.scenario_id]
    eligible, eliminated = apply_knowledge_base(DRONES, scenario)
    if len(eligible) == 0:
        raise HTTPException(status_code=422, detail="No eligible drones")
    matrix_dict = request.custom_matrix if request.custom_matrix else AHP_DATA["matrix"]
    matrix = load_matrix_from_dict(matrix_dict, CRITERIA)
    ahp_result = convert_numpy(compute_ahp(matrix, CRITERIA))
    weights = ahp_result["weights_array"]
    ranked = convert_numpy(run_topsis(eligible, weights, CRITERIA))
    np.random.seed(42)
    sensitivity = convert_numpy(run_sensitivity_analysis(
        eligible, weights, CRITERIA,
        n_simulations=request.n_sensitivity_simulations,
        perturbation_pct=request.perturbation_pct
    ))
    evaluation_result = {
        "scenario": {"id": scenario["id"], "name": scenario["name"],
                     "description": scenario["description"],
                     "mission": scenario["mission"]["primary"],
                     "environment": scenario["environment"]["location_type"]},
        "filter_summary": {"total_drones": len(DRONES), "eligible": len(eligible),
                           "eliminated": len(eliminated),
                           "rules_applied": get_rules_summary()["total_rules"],
                           "eliminated_drones": eliminated},
        "ahp": {"consistency_ratio": ahp_result["consistency_ratio"],
                "is_consistent": ahp_result["is_consistent"],
                "top5_criteria_by_weight": sorted(ahp_result["weights"].items(), key=lambda x: -x[1])[:5]},
        "ranking": ranked,
        "sensitivity": sensitivity,
        "recommendation": {
            "top_drone": ranked[0]["name"],
            "top_drone_id": ranked[0]["id"],
            "closeness_coefficient": ranked[0]["closeness_coefficient"],
            "stability": next((r["stability"] for r in sensitivity["results"] if r["id"] == ranked[0]["id"]), "UNKNOWN"),
            "explanation": f"{ranked[0]['name']} ranked first with CC={ranked[0]['closeness_coefficient']:.4f}"
        }
    }
    explanation = generate_explanation(evaluation_result, request.question)
    return {**evaluation_result, "ai_explanation": explanation}


@app.post("/chat")
def chat(request: ChatRequest):
    """Follow-up chat about evaluation results."""
    answer = answer_followup(
        question=request.question,
        evaluation_result=request.evaluation_result,
        chat_history=request.chat_history or []
    )
    return {"question": request.question, "answer": answer, "role": "assistant"}


@app.get("/countries")
def get_countries():
    """Return all supported EU countries with their regulations."""
    from country_regulations import get_all_countries, EU_COUNTRY_REGULATIONS
    countries = get_all_countries()
    return {
        "count": len(countries),
        "countries": countries,
        "note": "All countries follow EASA EU 2019/947 base regulations with national additions"
    }


@app.get("/countries/{country_code}")
def get_country(country_code: str):
    """Return regulations for a specific EU country."""
    regs = get_country_regulations(country_code.upper())
    if not regs:
        raise HTTPException(
            status_code=404,
            detail=f"Country '{country_code}' not found. Use /countries to see supported countries."
        )
    return regs


@app.post("/evaluate/country")
def evaluate_with_country(
    scenario_id: str,
    country_code: str,
    n_sensitivity_simulations: int = 100,
):
    """
    Full DSS evaluation with country-specific regulation filtering.
    Applies both Knowledge Base rules AND country-specific EU regulations.
    """
    if scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario not found")

    scenario = SCENARIOS[scenario_id]

    # 1. Apply Knowledge Base filter
    eligible_kb, eliminated_kb = apply_knowledge_base(DRONES, scenario)

    # 2. Apply country regulations on top of KB filter
    country_result = apply_country_filter(eligible_kb, country_code.upper())
    eligible    = country_result["eligible"]
    eliminated_country = country_result["eliminated"]
    country_info = country_result.get("country", {})

    if not eligible:
        raise HTTPException(
            status_code=422,
            detail={
                "message": f"No drones eligible after applying {country_code} regulations",
                "kb_eliminated": len(eliminated_kb),
                "country_eliminated": len(eliminated_country),
            }
        )

    # 3. AHP + TOPSIS
    matrix = load_matrix_from_dict(AHP_DATA["matrix"], CRITERIA)
    ahp_result = convert_numpy(compute_ahp(matrix, CRITERIA))
    weights = ahp_result["weights_array"]
    ranked = convert_numpy(run_topsis(eligible, weights, CRITERIA))

    # 4. Sensitivity
    np.random.seed(42)
    sensitivity = convert_numpy(run_sensitivity_analysis(
        eligible, weights, CRITERIA,
        n_simulations=n_sensitivity_simulations,
        perturbation_pct=0.20
    ))

    # 5. AI explanation with country context
    eval_result = {
        "scenario": {"id": scenario["id"], "name": scenario["name"],
                     "description": scenario["description"],
                     "mission": scenario["mission"]["primary"],
                     "environment": scenario["environment"]["location_type"]},
        "filter_summary": {
            "total_drones": len(DRONES),
            "eligible": len(eligible),
            "eliminated": len(eliminated_kb) + len(eliminated_country),
            "rules_applied": get_rules_summary()["total_rules"],
            "eliminated_drones": eliminated_kb + eliminated_country,
        },
        "ahp": {
            "consistency_ratio": ahp_result["consistency_ratio"],
            "is_consistent": ahp_result["is_consistent"],
            "top5_criteria_by_weight": sorted(ahp_result["weights"].items(), key=lambda x: -x[1])[:5],
        },
        "ranking": ranked,
        "sensitivity": sensitivity,
        "recommendation": {
            "top_drone": ranked[0]["name"],
            "top_drone_id": ranked[0]["id"],
            "closeness_coefficient": ranked[0]["closeness_coefficient"],
            "stability": next(
                (r["stability"] for r in sensitivity["results"] if r["id"] == ranked[0]["id"]),
                "UNKNOWN"
            ),
            "explanation": f"{ranked[0]['name']} ranked first for {scenario['name']} in {country_info.get('name', country_code)}"
        }
    }

    country_question = f"Consider that this evaluation is for {country_info.get('name', country_code)}. {country_info.get('notes', '')}. What country-specific regulations apply?"
    ai_explanation = generate_explanation(eval_result, country_question)

    return {
        **eval_result,
        "country": {
            "code":      country_code.upper(),
            "name":      country_info.get("name", ""),
            "flag":      country_info.get("flag", ""),
            "authority": country_info.get("authority", ""),
            "summary":   country_result.get("summary", {}),
            "kb_eliminated":      len(eliminated_kb),
            "country_eliminated": len(eliminated_country),
            "eliminated_by_country": eliminated_country,
        },
        "ai_explanation": ai_explanation,
    }
