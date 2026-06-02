"""
Sensitivity Analysis
DV2573: Intelligent DSS for Drone Selection in Small EU Ports
Blekinge Institute of Technology

Tests how stable the TOPSIS ranking is when AHP weights are perturbed.
Runs N simulations varying weights by ±perturbation_pct and tracks rank changes.
"""

import numpy as np
import json
import os
from typing import List, Dict
from collections import defaultdict
from topsis import run_topsis
from ahp import load_matrix_from_dict, compute_ahp, CRITERIA


def run_sensitivity_analysis(
    drones: List[dict],
    base_weights: List[float],
    criteria: List[str],
    n_simulations: int = 500,
    perturbation_pct: float = 0.20
) -> dict:
    """
    Monte Carlo sensitivity analysis on TOPSIS rankings.

    For each simulation:
    - Randomly perturb base weights by ±perturbation_pct
    - Renormalize so weights sum to 1
    - Run TOPSIS
    - Record ranks

    Returns stability metrics per drone.
    """
    base_weights = np.array(base_weights)
    n = len(drones)
    rank_counts = defaultdict(lambda: defaultdict(int))  # drone_id -> rank -> count
    cc_values = defaultdict(list)

    for sim in range(n_simulations):
        # Perturb weights
        noise = np.random.uniform(1 - perturbation_pct, 1 + perturbation_pct, len(base_weights))
        perturbed = base_weights * noise
        perturbed = np.clip(perturbed, 0, None)
        perturbed /= perturbed.sum()  # renormalize

        results = run_topsis(drones, perturbed.tolist(), criteria)
        for r in results:
            rank_counts[r["id"]][r["rank"]] += 1
            cc_values[r["id"]].append(r["closeness_coefficient"])

    # Aggregate
    base_results = run_topsis(drones, base_weights.tolist(), criteria)
    drone_lookup = {d["id"]: d["name"] for d in drones}

    analysis = []
    for r in base_results:
        did = r["id"]
        counts = rank_counts[did]
        ccs = cc_values[did]
        most_common_rank = max(counts, key=counts.get)
        rank_1_pct = round(counts.get(1, 0) / n_simulations * 100, 1)
        top3_pct = round(sum(counts.get(rk, 0) for rk in [1, 2, 3]) / n_simulations * 100, 1)

        analysis.append({
            "id": did,
            "name": drone_lookup[did],
            "base_rank": r["rank"],
            "base_cc": round(r["closeness_coefficient"], 6),
            "most_common_rank": most_common_rank,
            "rank_1_frequency_pct": rank_1_pct,
            "top3_frequency_pct": top3_pct,
            "cc_mean": round(float(np.mean(ccs)), 6),
            "cc_std": round(float(np.std(ccs)), 6),
            "cc_min": round(float(np.min(ccs)), 6),
            "cc_max": round(float(np.max(ccs)), 6),
            "rank_distribution": {str(k): v for k, v in sorted(counts.items())},
            "stability": "HIGH" if top3_pct >= 70 else ("MEDIUM" if top3_pct >= 40 else "LOW")
        })

    analysis.sort(key=lambda x: x["base_rank"])

    return {
        "settings": {
            "n_simulations": n_simulations,
            "perturbation_pct": perturbation_pct,
            "n_criteria": len(criteria),
            "n_drones": len(drones)
        },
        "results": analysis
    }


def print_sensitivity_report(sa: dict):
    print("\n" + "=" * 75)
    print(f"SENSITIVITY ANALYSIS  ({sa['settings']['n_simulations']} simulations, "
          f"±{int(sa['settings']['perturbation_pct']*100)}% weight perturbation)")
    print("=" * 75)
    print(f"  {'Rank':<5} {'Drone':<35} {'Base CC':>8}  {'Top-3%':>7}  {'Stability'}")
    print("-" * 75)
    for r in sa["results"]:
        stability_icon = {"HIGH": "✓✓", "MEDIUM": "~", "LOW": "✗"}.get(r["stability"], "")
        print(f"  {r['base_rank']:<5} {r['name']:<35} {r['base_cc']:>8.4f}  "
              f"{r['top3_frequency_pct']:>6.1f}%  {stability_icon} {r['stability']}")
    print("=" * 75)


if __name__ == "__main__":
    base = os.path.dirname(__file__)

    with open(os.path.join(base, "drone_dataset.json")) as f:
        drone_data = json.load(f)
    with open(os.path.join(base, "ahp_pairwise_matrix.json")) as f:
        ahp_data = json.load(f)

    matrix = load_matrix_from_dict(ahp_data["matrix"], CRITERIA)
    ahp_result = compute_ahp(matrix, CRITERIA)
    weights = ahp_result["weights_array"]
    drones = drone_data["drones"]

    np.random.seed(42)
    sa = run_sensitivity_analysis(drones, weights, CRITERIA, n_simulations=500, perturbation_pct=0.20)
    print_sensitivity_report(sa)

    out_path = os.path.join(base, "sensitivity_results.json")
    with open(out_path, "w") as f:
        json.dump(sa, f, indent=2)
    print(f"\nSaved to: {out_path}")
