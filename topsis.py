"""
TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)
DV2573: Intelligent DSS for Drone Selection in Small EU Ports
Blekinge Institute of Technology
"""

import json
import numpy as np
from typing import List, Dict

# Criteria direction: "benefit" = higher is better, "cost" = lower is better
CRITERIA_DIRECTION = {
    "flight_time":              "benefit",
    "flight_range":             "benefit",
    "night_vision":             "benefit",
    "payload_capacity":         "benefit",
    "camera_quality":           "benefit",
    "autonomy_level":           "benefit",
    "weather_resistance":       "benefit",
    "real_time_transmission":   "benefit",
    "obstacle_avoidance":       "benefit",
    "gps_accuracy":             "cost",      # lower meters = better
    "battery_swappable":        "benefit",
    "maintenance_requirements": "cost",      # lower score = better
    "initial_cost":             "cost",      # lower EUR = better
    "operational_cost":         "cost",      # lower EUR/hr = better
    "regulatory_compliance":    "benefit",
    "integration_capability":   "benefit",
    "sensor_compatibility":     "benefit",
    "data_storage":             "benefit",
    "launch_recovery_method":   "benefit",
    "redundancy_failsafe":      "benefit",
}

# Encode categorical/ordinal fields to numeric scores
ENCODINGS = {
    "night_vision":           {"none": 0, "basic": 1, "advanced": 2},
    "autonomy_level":         {"manual": 0, "semi-autonomous": 1, "fully-autonomous": 2},
    "weather_resistance_ip":  {"IP43": 1, "IP53": 2, "IP55": 3, "IP67": 4},
    "obstacle_avoidance":     {"none": 0, "basic": 1, "omnidirectional": 2},
    "regulatory_compliance":  {"Open-A1": 1, "Open-A2": 2, "Open-A3": 2, "Specific": 3, "Certified": 4},
    "integration_capability": {"low": 1, "medium": 2, "high": 3},
    "launch_recovery_method": {"hand-launch": 1, "runway": 1, "VTOL": 2, "automated-pad": 3},
    "redundancy_failsafe":    {"none": 0, "basic": 1, "advanced": 2, "full-redundancy": 3},
    "real_time_transmission": {True: 1, False: 0},
    "battery_swappable":      {True: 1, False: 0},
}

CRITERIA_FIELDS = {
    "flight_time":              "flight_time_min",
    "flight_range":             "flight_range_km",
    "night_vision":             "night_vision",
    "payload_capacity":         "payload_capacity_kg",
    "camera_quality":           "camera_quality_mp",
    "autonomy_level":           "autonomy_level",
    "weather_resistance":       "weather_resistance_ip",
    "real_time_transmission":   "real_time_transmission",
    "obstacle_avoidance":       "obstacle_avoidance",
    "gps_accuracy":             "gps_accuracy_m",
    "battery_swappable":        "battery_swappable",
    "maintenance_requirements": "maintenance_score",
    "initial_cost":             "initial_cost_eur",
    "operational_cost":         "operational_cost_eur_hr",
    "regulatory_compliance":    "regulatory_compliance",
    "integration_capability":   "integration_capability",
    "sensor_compatibility":     "sensor_compatibility",
    "data_storage":             "data_storage_gb",
    "launch_recovery_method":   "launch_recovery_method",
    "redundancy_failsafe":      "redundancy_failsafe",
}


def encode_drone(drone: dict, criteria: List[str]) -> List[float]:
    """Convert a drone dict to a numeric vector for TOPSIS."""
    row = []
    for criterion in criteria:
        field = CRITERIA_FIELDS[criterion]
        val = drone.get(field, 0)
        if field in ENCODINGS:
            val = ENCODINGS[field].get(val, 0)
        row.append(float(val))
    return row


def run_topsis(drones: List[dict], weights: List[float], criteria: List[str]) -> List[dict]:
    """
    Run TOPSIS on a list of drones.

    Steps:
    1. Build decision matrix
    2. Normalize (vector normalization)
    3. Apply AHP weights
    4. Determine Positive Ideal Solution (PIS) and Negative Ideal Solution (NIS)
    5. Compute Euclidean distances to PIS and NIS
    6. Compute Closeness Coefficient (CC)
    7. Rank by CC descending

    Returns list of drones with TOPSIS scores, sorted by rank.
    """
    n_drones = len(drones)
    n_criteria = len(criteria)
    weights_array = np.array(weights)

    # Step 1: Decision matrix
    matrix = np.array([encode_drone(d, criteria) for d in drones], dtype=float)

    # Step 2: Vector normalization
    norms = np.sqrt((matrix ** 2).sum(axis=0))
    norms[norms == 0] = 1e-10  # avoid division by zero
    normalized = matrix / norms

    # Step 3: Weighted normalized matrix
    weighted = normalized * weights_array

    # Step 4: PIS and NIS per criterion direction
    pis = np.zeros(n_criteria)
    nis = np.zeros(n_criteria)
    for j, criterion in enumerate(criteria):
        col = weighted[:, j]
        if CRITERIA_DIRECTION[criterion] == "benefit":
            pis[j] = col.max()
            nis[j] = col.min()
        else:  # cost
            pis[j] = col.min()
            nis[j] = col.max()

    # Step 5: Euclidean distances
    d_pos = np.sqrt(((weighted - pis) ** 2).sum(axis=1))
    d_neg = np.sqrt(((weighted - nis) ** 2).sum(axis=1))

    # Step 6: Closeness coefficient
    cc = d_neg / (d_pos + d_neg + 1e-10)

    # Step 7: Build results
    results = []
    for i, drone in enumerate(drones):
        results.append({
            "rank": None,
            "id": drone["id"],
            "name": drone["name"],
            "manufacturer": drone["manufacturer"],
            "type": drone["type"],
            "closeness_coefficient": round(float(cc[i]), 6),
            "distance_to_pis": round(float(d_pos[i]), 6),
            "distance_to_nis": round(float(d_neg[i]), 6),
            "criteria_scores": {
                criterion: round(float(weighted[i][j]), 6)
                for j, criterion in enumerate(criteria)
            }
        })

    results.sort(key=lambda x: -x["closeness_coefficient"])
    for rank, r in enumerate(results, 1):
        r["rank"] = rank

    return results


def print_topsis_report(results: List[dict]):
    print("\n" + "=" * 70)
    print("TOPSIS RANKING RESULTS")
    print("=" * 70)
    print(f"  {'Rank':<5} {'Drone':<35} {'CC':>8}  {'D+':<10} {'D-':<10}")
    print("-" * 70)
    for r in results:
        bar = "█" * int(r["closeness_coefficient"] * 30)
        print(f"  {r['rank']:<5} {r['name']:<35} {r['closeness_coefficient']:>8.4f}  "
              f"{r['distance_to_pis']:<10.4f} {r['distance_to_nis']:<10.4f}  {bar}")
    print("=" * 70)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return super().default(obj)


if __name__ == "__main__":
    import os
    from ahp import load_matrix_from_dict, compute_ahp, CRITERIA

    base = os.path.dirname(__file__)

    with open(os.path.join(base, "drone_dataset.json")) as f:
        drone_data = json.load(f)
    with open(os.path.join(base, "ahp_pairwise_matrix.json")) as f:
        ahp_data = json.load(f)

    matrix = load_matrix_from_dict(ahp_data["matrix"], CRITERIA)
    ahp_result = compute_ahp(matrix, CRITERIA)

    if not ahp_result["is_consistent"]:
        print(f"WARNING: {ahp_result['status']}")

    weights = ahp_result["weights_array"]
    drones = drone_data["drones"]

    results = run_topsis(drones, weights, CRITERIA)
    print_topsis_report(results)

    out_path = os.path.join(base, "topsis_results.json")
    with open(out_path, "w") as f:
        json.dump({"ahp_summary": ahp_result, "topsis_ranking": results}, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to: {out_path}")