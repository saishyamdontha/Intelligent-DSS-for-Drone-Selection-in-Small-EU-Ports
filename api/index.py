"""
FastAPI Backend — Vercel Deployment
DV2573: Intelligent DSS for Drone Selection in Small EU Ports
Blekinge Institute of Technology
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# ── Load data ─────────────────────────────────────────────────────────────────
BASE = os.path.dirname(__file__)

with open(os.path.join(BASE, "drone_dataset.json")) as f:
    DRONE_DATA = json.load(f)

with open(os.path.join(BASE, "port_scenarios.json")) as f:
    SCENARIO_DATA = json.load(f)

with open(os.path.join(BASE, "ahp_pairwise_matrix.json")) as f:
    AHP_DATA = json.load(f)

DRONES = DRONE_DATA["drones"]
SCENARIOS = {s["id"]: s for s in SCENARIO_DATA["scenarios"]}

# ── Inline AHP (no local import needed on Vercel) ─────────────────────────────
import numpy as _np

RI_TABLE = {1:0.00,2:0.00,3:0.58,4:0.90,5:1.12,6:1.24,7:1.32,8:1.41,9:1.45,10:1.49,
            11:1.51,12:1.48,13:1.56,14:1.57,15:1.59,16:1.60,17:1.61,18:1.62,19:1.63,20:1.64}

CRITERIA = [
    "flight_time","flight_range","night_vision","payload_capacity","camera_quality",
    "autonomy_level","weather_resistance","real_time_transmission","obstacle_avoidance",
    "gps_accuracy","battery_swappable","maintenance_requirements","initial_cost",
    "operational_cost","regulatory_compliance","integration_capability",
    "sensor_compatibility","data_storage","launch_recovery_method","redundancy_failsafe"
]

CRITERIA_DIRECTION = {
    "flight_time":"benefit","flight_range":"benefit","night_vision":"benefit",
    "payload_capacity":"benefit","camera_quality":"benefit","autonomy_level":"benefit",
    "weather_resistance":"benefit","real_time_transmission":"benefit","obstacle_avoidance":"benefit",
    "gps_accuracy":"cost","battery_swappable":"benefit","maintenance_requirements":"cost",
    "initial_cost":"cost","operational_cost":"cost","regulatory_compliance":"benefit",
    "integration_capability":"benefit","sensor_compatibility":"benefit","data_storage":"benefit",
    "launch_recovery_method":"benefit","redundancy_failsafe":"benefit",
}

ENCODINGS = {
    "night_vision":{"none":0,"basic":1,"advanced":2},
    "autonomy_level":{"manual":0,"semi-autonomous":1,"fully-autonomous":2},
    "weather_resistance_ip":{"IP43":1,"IP53":2,"IP55":3,"IP67":4},
    "obstacle_avoidance":{"none":0,"basic":1,"omnidirectional":2},
    "regulatory_compliance":{"Open-A1":1,"Open-A2":2,"Open-A3":2,"Specific":3,"Certified":4},
    "integration_capability":{"low":1,"medium":2,"high":3},
    "launch_recovery_method":{"hand-launch":1,"runway":1,"VTOL":2,"automated-pad":3},
    "redundancy_failsafe":{"none":0,"basic":1,"advanced":2,"full-redundancy":3},
    "real_time_transmission":{True:1,False:0},
    "battery_swappable":{True:1,False:0},
}

CRITERIA_FIELDS = {
    "flight_time":"flight_time_min","flight_range":"flight_range_km","night_vision":"night_vision",
    "payload_capacity":"payload_capacity_kg","camera_quality":"camera_quality_mp",
    "autonomy_level":"autonomy_level","weather_resistance":"weather_resistance_ip",
    "real_time_transmission":"real_time_transmission","obstacle_avoidance":"obstacle_avoidance",
    "gps_accuracy":"gps_accuracy_m","battery_swappable":"battery_swappable",
    "maintenance_requirements":"maintenance_score","initial_cost":"initial_cost_eur",
    "operational_cost":"operational_cost_eur_hr","regulatory_compliance":"regulatory_compliance",
    "integration_capability":"integration_capability","sensor_compatibility":"sensor_compatibility",
    "data_storage":"data_storage_gb","launch_recovery_method":"launch_recovery_method",
    "redundancy_failsafe":"redundancy_failsafe",
}

IP_RANK = {"IP43":1,"IP53":2,"IP55":3,"IP67":4}
AUTONOMY_RANK = {"manual":0,"semi-autonomous":1,"fully-autonomous":2}
REDUNDANCY_RANK = {"none":0,"basic":1,"advanced":2,"full-redundancy":3}


def load_matrix_from_dict(matrix_dict, criteria):
    n = len(criteria)
    matrix = _np.zeros((n, n))
    for i, ci in enumerate(criteria):
        for j, cj in enumerate(criteria):
            matrix[i][j] = matrix_dict[ci][j]
    return matrix


def compute_ahp(matrix, criteria):
    n = len(criteria)
    col_sums = matrix.sum(axis=0)
    normalized = matrix / col_sums
    weights = normalized.mean(axis=1)
    weighted_sum = matrix @ weights
    lambda_vector = weighted_sum / weights
    lambda_max = lambda_vector.mean()
    CI = (lambda_max - n) / (n - 1)
    ri = RI_TABLE.get(n, 1.64)
    CR = CI / ri if ri > 0 else 0.0
    consistent = bool(CR < 0.10)
    return {
        "criteria": criteria,
        "weights": dict(zip(criteria, weights.tolist())),
        "weights_array": weights.tolist(),
        "lambda_max": round(float(lambda_max), 6),
        "consistency_index": round(float(CI), 6),
        "consistency_ratio": round(float(CR), 6),
        "random_index": ri,
        "is_consistent": consistent,
        "status": "ACCEPTED" if consistent else "REJECTED — CR >= 0.10"
    }


def encode_drone(drone, criteria):
    row = []
    for criterion in criteria:
        field = CRITERIA_FIELDS[criterion]
        val = drone.get(field, 0)
        if field in ENCODINGS:
            val = ENCODINGS[field].get(val, 0)
        row.append(float(val))
    return row


def run_topsis(drones, weights, criteria):
    n_criteria = len(criteria)
    weights_array = _np.array(weights)
    matrix = _np.array([encode_drone(d, criteria) for d in drones], dtype=float)
    norms = _np.sqrt((matrix ** 2).sum(axis=0))
    norms[norms == 0] = 1e-10
    normalized = matrix / norms
    weighted = normalized * weights_array
    pis = _np.zeros(n_criteria)
    nis = _np.zeros(n_criteria)
    for j, criterion in enumerate(criteria):
        col = weighted[:, j]
        if CRITERIA_DIRECTION[criterion] == "benefit":
            pis[j] = col.max(); nis[j] = col.min()
        else:
            pis[j] = col.min(); nis[j] = col.max()
    d_pos = _np.sqrt(((weighted - pis) ** 2).sum(axis=1))
    d_neg = _np.sqrt(((weighted - nis) ** 2).sum(axis=1))
    cc = d_neg / (d_pos + d_neg + 1e-10)
    results = []
    for i, drone in enumerate(drones):
        results.append({
            "rank": None, "id": drone["id"], "name": drone["name"],
            "manufacturer": drone["manufacturer"], "type": drone["type"],
            "closeness_coefficient": round(float(cc[i]), 6),
            "distance_to_pis": round(float(d_pos[i]), 6),
            "distance_to_nis": round(float(d_neg[i]), 6),
            "criteria_scores": {c: round(float(weighted[i][j]), 6) for j, c in enumerate(criteria)}
        })
    results.sort(key=lambda x: -x["closeness_coefficient"])
    for rank, r in enumerate(results, 1):
        r["rank"] = rank
    return results


def run_sensitivity_analysis(drones, base_weights, criteria, n_simulations=50, perturbation_pct=0.20):
    """Reduced simulations for Vercel timeout compliance."""
    from collections import defaultdict
    base_weights = _np.array(base_weights)
    rank_counts = defaultdict(lambda: defaultdict(int))
    cc_values = defaultdict(list)
    for _ in range(n_simulations):
        noise = _np.random.uniform(1 - perturbation_pct, 1 + perturbation_pct, len(base_weights))
        perturbed = _np.clip(base_weights * noise, 0, None)
        perturbed /= perturbed.sum()
        for r in run_topsis(drones, perturbed.tolist(), criteria):
            rank_counts[r["id"]][r["rank"]] += 1
            cc_values[r["id"]].append(r["closeness_coefficient"])
    base_results = run_topsis(drones, base_weights.tolist(), criteria)
    drone_lookup = {d["id"]: d["name"] for d in drones}
    analysis = []
    for r in base_results:
        did = r["id"]
        counts = rank_counts[did]
        ccs = cc_values[did]
        top3_pct = round(sum(counts.get(rk, 0) for rk in [1, 2, 3]) / n_simulations * 100, 1)
        analysis.append({
            "id": did, "name": drone_lookup[did], "base_rank": r["rank"],
            "base_cc": round(r["closeness_coefficient"], 6),
            "most_common_rank": max(counts, key=counts.get) if counts else r["rank"],
            "rank_1_frequency_pct": round(counts.get(1, 0) / n_simulations * 100, 1),
            "top3_frequency_pct": top3_pct,
            "cc_mean": round(float(_np.mean(ccs)), 6) if ccs else 0,
            "cc_std": round(float(_np.std(ccs)), 6) if ccs else 0,
            "cc_min": round(float(_np.min(ccs)), 6) if ccs else 0,
            "cc_max": round(float(_np.max(ccs)), 6) if ccs else 0,
            "rank_distribution": {str(k): v for k, v in sorted(counts.items())},
            "stability": "HIGH" if top3_pct >= 70 else ("MEDIUM" if top3_pct >= 40 else "LOW")
        })
    analysis.sort(key=lambda x: x["base_rank"])
    return {"settings": {"n_simulations": n_simulations, "perturbation_pct": perturbation_pct,
                         "n_criteria": len(criteria), "n_drones": len(drones)}, "results": analysis}


def apply_knowledge_base(drones, scenario):
    eligible = []
    eliminated = []
    constraints = scenario.get("hard_constraints", {})
    budget = scenario.get("budget", {})
    allowed_compliance = constraints.get("regulatory_compliance_allowed",
        ["Open-A1","Open-A2","Open-A3","Specific","Certified"])
    for drone in drones:
        reasons = []
        if drone["regulatory_compliance"] not in allowed_compliance:
            reasons.append(f"REG-01: Category '{drone['regulatory_compliance']}' not allowed")
        min_ft = constraints.get("min_flight_time_min")
        if min_ft and drone["flight_time_min"] < min_ft:
            reasons.append(f"OPS-01: Flight time {drone['flight_time_min']}min < {min_ft}min")
        min_fr = constraints.get("min_flight_range_km")
        if min_fr and drone["flight_range_km"] < min_fr:
            reasons.append(f"OPS-02: Range {drone['flight_range_km']}km < {min_fr}km")
        min_ip = constraints.get("min_weather_resistance_ip")
        if min_ip and IP_RANK.get(drone["weather_resistance_ip"], 0) < IP_RANK.get(min_ip, 0):
            reasons.append(f"OPS-03: IP {drone['weather_resistance_ip']} < {min_ip}")
        if constraints.get("real_time_transmission_required") and not drone["real_time_transmission"]:
            reasons.append("OPS-04: Real-time transmission required")
        if constraints.get("night_vision_required") and drone["night_vision"] == "none":
            reasons.append("OPS-05: Night vision required")
        max_cost = budget.get("max_initial_cost_eur")
        if max_cost and drone["initial_cost_eur"] > max_cost:
            reasons.append(f"OPS-06: Cost €{drone['initial_cost_eur']:,} > budget €{max_cost:,}")
        max_op = budget.get("max_operational_cost_eur_hr")
        if max_op and drone["operational_cost_eur_hr"] > max_op:
            reasons.append(f"OPS-07: Op cost €{drone['operational_cost_eur_hr']}/hr > €{max_op}/hr")
        min_cam = constraints.get("min_camera_quality_mp")
        if min_cam and drone["camera_quality_mp"] < min_cam:
            reasons.append(f"OPS-08: Camera {drone['camera_quality_mp']}MP < {min_cam}MP")
        min_pay = constraints.get("min_payload_capacity_kg")
        if min_pay and drone["payload_capacity_kg"] < min_pay:
            reasons.append(f"OPS-09: Payload {drone['payload_capacity_kg']}kg < {min_pay}kg")
        min_sen = constraints.get("min_sensor_compatibility")
        if min_sen and drone["sensor_compatibility"] < min_sen:
            reasons.append(f"OPS-10: Sensor compat {drone['sensor_compatibility']} < {min_sen}")
        min_auto = constraints.get("min_autonomy_level")
        if min_auto and AUTONOMY_RANK.get(drone["autonomy_level"], 0) < AUTONOMY_RANK.get(min_auto, 0):
            reasons.append(f"Autonomy '{drone['autonomy_level']}' < '{min_auto}'")
        min_red = constraints.get("min_redundancy")
        if min_red and REDUNDANCY_RANK.get(drone["redundancy_failsafe"], 0) < REDUNDANCY_RANK.get(min_red, 0):
            reasons.append(f"Redundancy '{drone['redundancy_failsafe']}' < '{min_red}'")
        if reasons:
            eliminated.append({"id": drone["id"], "name": drone["name"], "elimination_reasons": reasons})
        else:
            eligible.append(drone)
    return eligible, eliminated


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Intelligent DSS - Drone Selection for Small EU Ports",
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
    custom_matrix: Optional[Dict[str, List[float]]] = None
    n_sensitivity_simulations: Optional[int] = 50  # reduced for Vercel
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

class AIPromptRequest(BaseModel):
    prompt: str

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"system": "DSS Drone Selection", "course": "DV2573", "institution": "BTH"}

@app.get("/api/drones")
def get_drones():
    return {"count": len(DRONES), "drones": DRONES}

@app.get("/api/scenarios")
def get_scenarios():
    return {"count": len(SCENARIOS), "scenarios": list(SCENARIOS.values())}

@app.get("/api/scenarios/{scenario_id}")
def get_scenario(scenario_id: str):
    if scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")
    return SCENARIOS[scenario_id]

@app.get("/api/ahp")
def get_ahp_weights():
    matrix = load_matrix_from_dict(AHP_DATA["matrix"], CRITERIA)
    return compute_ahp(matrix, CRITERIA)

@app.post("/api/evaluate")
def evaluate(request: EvaluationRequest):
    if request.scenario_id not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"Scenario '{request.scenario_id}' not found")
    scenario = SCENARIOS[request.scenario_id]
    eligible, eliminated = apply_knowledge_base(DRONES, scenario)
    if not eligible:
        raise HTTPException(status_code=422, detail="No drones passed filters. Relax constraints.")
    matrix_dict = request.custom_matrix if request.custom_matrix else AHP_DATA["matrix"]
    matrix = load_matrix_from_dict(matrix_dict, CRITERIA)
    ahp_result = compute_ahp(matrix, CRITERIA)
    weights = ahp_result["weights_array"]
    ranked = run_topsis(eligible, weights, CRITERIA)
    np.random.seed(42)
    sensitivity = run_sensitivity_analysis(eligible, weights, CRITERIA,
        n_simulations=request.n_sensitivity_simulations, perturbation_pct=request.perturbation_pct)
    ahp_warning = None if ahp_result["is_consistent"] else f"CR={ahp_result['consistency_ratio']:.4f} >= 0.10"
    return {
        "scenario": {"id": scenario["id"], "name": scenario["name"], "description": scenario["description"]},
        "filter_summary": {"total_drones": len(DRONES), "eligible": len(eligible),
                           "eliminated": len(eliminated), "eliminated_drones": eliminated},
        "ahp": {"consistency_ratio": ahp_result["consistency_ratio"], "is_consistent": ahp_result["is_consistent"],
                "warning": ahp_warning,
                "top5_criteria_by_weight": sorted(ahp_result["weights"].items(), key=lambda x: -x[1])[:5]},
        "ranking": ranked,
        "sensitivity": sensitivity,
        "recommendation": {
            "top_drone": ranked[0]["name"], "top_drone_id": ranked[0]["id"],
            "closeness_coefficient": ranked[0]["closeness_coefficient"],
            "stability": next((r["stability"] for r in sensitivity["results"] if r["id"] == ranked[0]["id"]), "UNKNOWN"),
            "explanation": (f"{ranked[0]['name']} ranked first with CC={ranked[0]['closeness_coefficient']:.4f}, "
                           f"outperforming {len(eligible)-1} drones across {len(CRITERIA)} criteria.")
        }
    }

@app.post("/api/evaluate/custom-scenario")
def evaluate_custom(request: CustomScenarioRequest):
    scenario_dict = request.scenario.dict()
    scenario_dict["id"] = "CUSTOM"
    eligible, eliminated = apply_knowledge_base(DRONES, scenario_dict)
    if not eligible:
        raise HTTPException(status_code=422, detail="No eligible drones for this custom scenario.")
    matrix_dict = request.matrix if request.matrix else AHP_DATA["matrix"]
    ahp_matrix = load_matrix_from_dict(matrix_dict, CRITERIA)
    ahp_result = compute_ahp(ahp_matrix, CRITERIA)
    ranked = run_topsis(eligible, ahp_result["weights_array"], CRITERIA)
    return {"scenario": scenario_dict, "eligible_count": len(eligible),
            "eliminated_count": len(eliminated), "ranking": ranked, "ahp": ahp_result}

@app.post("/api/ai/overview")
def ai_overview(request: AIPromptRequest):
    import requests
    from retrieval.retriever import retrieve

    context_chunks = retrieve(request.prompt, k=4)
    context_text = "\n\n".join(
        [f"[p.{c['page']}] {c['content']}" for c in context_chunks]
    )

    full_prompt = (
        f"Context from EU drone regulation (EASA 2019/947, 2019/945):\n{context_text}\n\n"
        f"Question: {request.prompt}\n\n"
        f"Answer using only the context above. Cite the page number for any claim."
    )

    ollama_response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3.1:8b", "prompt": full_prompt, "stream": False},
    )
    if ollama_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Ollama request failed.")
    text = ollama_response.json()["response"]
    return {"content": [{"type": "text", "text": text}], "sources": context_chunks}
