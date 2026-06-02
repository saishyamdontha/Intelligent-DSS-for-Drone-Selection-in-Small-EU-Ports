"""
FastAPI Backend — Main Application
DV2573: Intelligent DSS for Drone Selection in Small EU Ports
Blekinge Institute of Technology

Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import numpy as np
import httpx

from ahp import load_matrix_from_dict, compute_ahp, CRITERIA
from topsis import run_topsis
from knowledge_base import apply_knowledge_base
from sensitivity_analysis import run_sensitivity_analysis
from dotenv import load_dotenv
load_dotenv()
# ── Load data on startup ─────────────────────────────────────────────────────
BASE = os.path.dirname(__file__)

with open(os.path.join(BASE, "drone_dataset.json")) as f:
    DRONE_DATA = json.load(f)

with open(os.path.join(BASE, "port_scenarios.json")) as f:
    SCENARIO_DATA = json.load(f)

with open(os.path.join(BASE, "ahp_pairwise_matrix.json")) as f:
    AHP_DATA = json.load(f)

DRONES = DRONE_DATA["drones"]
SCENARIOS = {s["id"]: s for s in SCENARIO_DATA["scenarios"]}

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Intelligent DSS — Drone Selection for Small EU Ports",
    description="AHP + TOPSIS Decision Support System | DV2573 | BTH",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic models ───────────────────────────────────────────────────────────
class EvaluationRequest(BaseModel):
    scenario_id: str
    custom_matrix: Optional[Dict[str, List[float]]] = None  # override AHP matrix
    n_sensitivity_simulations: Optional[int] = 200
    perturbation_pct: Optional[float] = 0.20

class CustomScenario(BaseModel):
    name: str
    budget: Dict[str, Any]
    hard_constraints: Dict[str, Any]
    mission: Dict[str, Any]
    environment: Dict[str, Any]

class CustomScenarioRequest(BaseModel):
    scenario: CustomScenario
    matrix: Optional[Dict[str, List[float]]] = None

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "system": "Intelligent DSS for Drone Selection in Small EU Ports",
        "course": "DV2573",
        "institution": "Blekinge Institute of Technology",
        "endpoints": ["/drones", "/scenarios", "/evaluate", "/ahp", "/docs"]
    }


@app.get("/drones")
def get_drones():
    """Return full drone database."""
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
    """Return all available port scenarios."""
    return {"count": len(SCENARIOS), "scenarios": list(SCENARIOS.values())}


@app.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str):
    """Return a single scenario by ID."""
    if scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    return SCENARIOS[scenario_id]


@app.get("/ahp")
def get_ahp_weights():
    """Compute and return AHP weights from the default pairwise matrix."""
    matrix = load_matrix_from_dict(AHP_DATA["matrix"], CRITERIA)
    result = compute_ahp(matrix, CRITERIA)
    return result


@app.post("/evaluate")
def evaluate(request: EvaluationRequest):
    """
    Full DSS pipeline:
    1. Validate scenario
    2. Apply Knowledge Base filter (hard constraints)
    3. Compute AHP weights
    4. Run TOPSIS on eligible drones
    5. Run Sensitivity Analysis
    6. Return ranked results with explanation
    """
    # 1. Validate scenario
    if request.scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{request.scenario_id}' not found")
    scenario = SCENARIOS[request.scenario_id]

    # 2. Knowledge Base filter
    eligible, eliminated = apply_knowledge_base(DRONES, scenario)
    if len(eligible) == 0:
        raise HTTPException(
            status_code=422,
            detail="No drones passed the knowledge base filter for this scenario. Relax constraints."
        )

    # 3. AHP weights
    matrix_dict = request.custom_matrix if request.custom_matrix else AHP_DATA["matrix"]
    matrix = load_matrix_from_dict(matrix_dict, CRITERIA)
    ahp_result = compute_ahp(matrix, CRITERIA)

    ahp_warning = None
    if not ahp_result["is_consistent"]:
        ahp_warning = f"AHP inconsistency warning: CR={ahp_result['consistency_ratio']:.4f} >= 0.10. Results may be unreliable."

    weights = ahp_result["weights_array"]

    # 4. TOPSIS ranking
    ranked = run_topsis(eligible, weights, CRITERIA)

    # 5. Sensitivity analysis
    np.random.seed(42)
    sensitivity = run_sensitivity_analysis(
        eligible, weights, CRITERIA,
        n_simulations=request.n_sensitivity_simulations,
        perturbation_pct=request.perturbation_pct
    )

    # 6. Compose response
    return {
        "scenario": {
            "id": scenario["id"],
            "name": scenario["name"],
            "description": scenario["description"]
        },
        "filter_summary": {
            "total_drones": len(DRONES),
            "eligible": len(eligible),
            "eliminated": len(eliminated),
            "eliminated_drones": eliminated
        },
        "ahp": {
            "consistency_ratio": ahp_result["consistency_ratio"],
            "is_consistent": ahp_result["is_consistent"],
            "warning": ahp_warning,
            "top5_criteria_by_weight": sorted(
                ahp_result["weights"].items(), key=lambda x: -x[1]
            )[:5]
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
            "explanation": (
                f"{ranked[0]['name']} ranked first with a closeness coefficient of "
                f"{ranked[0]['closeness_coefficient']:.4f}, indicating it is closest to the "
                f"ideal solution for the '{scenario['name']}' scenario. "
                f"It outperformed {len(eligible)-1} other eligible drones across {len(CRITERIA)} criteria."
            )
        }
    }


@app.post("/evaluate/custom-scenario")
def evaluate_custom(request: CustomScenarioRequest):
    """Evaluate drones against a user-defined custom scenario (not from presets)."""
    scenario_dict = request.scenario.dict()
    scenario_dict["id"] = "CUSTOM"
    eligible, eliminated = apply_knowledge_base(DRONES, scenario_dict)

    if len(eligible) == 0:
        raise HTTPException(status_code=422, detail="No eligible drones for this custom scenario.")

    matrix_dict = request.matrix if request.matrix else AHP_DATA["matrix"]
    ahp_matrix = load_matrix_from_dict(matrix_dict, CRITERIA)
    ahp_result = compute_ahp(ahp_matrix, CRITERIA)
    ranked = run_topsis(eligible, ahp_result["weights_array"], CRITERIA)

    return {
        "scenario": scenario_dict,
        "eligible_count": len(eligible),
        "eliminated_count": len(eliminated),
        "ranking": ranked,
        "ahp": ahp_result
    }

# ── Anthropic proxy ──────────────────────────────────────────────────────────
class AIPromptRequest(BaseModel):
    prompt: str

@app.post("/ai/overview")
async def ai_overview(request: AIPromptRequest):
    """Proxy Anthropic API call to avoid browser CORS restrictions."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set.")

    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": request.prompt}]
            }
        )
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    data = r.json()
    text = data["content"][0]["text"]
    return {"content": [{"type": "text", "text": text}]}