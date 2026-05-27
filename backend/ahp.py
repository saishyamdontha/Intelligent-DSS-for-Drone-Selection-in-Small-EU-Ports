"""
AHP (Analytic Hierarchy Process) — Criteria Weight Computation
DV2573: Intelligent DSS for Drone Selection in Small EU Ports
Blekinge Institute of Technology
"""

import numpy as np
from typing import List, Tuple

# Saaty's Random Consistency Index (RI) for n criteria
RI_TABLE = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
    11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59,
    16: 1.60, 17: 1.61, 18: 1.62, 19: 1.63, 20: 1.64,
}

CRITERIA = [
    "flight_time", "flight_range", "night_vision", "payload_capacity",
    "camera_quality", "autonomy_level", "weather_resistance",
    "real_time_transmission", "obstacle_avoidance", "gps_accuracy",
    "battery_swappable", "maintenance_requirements", "initial_cost",
    "operational_cost", "regulatory_compliance", "integration_capability",
    "sensor_compatibility", "data_storage", "launch_recovery_method",
    "redundancy_failsafe"
]


def load_matrix_from_dict(matrix_dict: dict, criteria: List[str]) -> np.ndarray:
    """Convert the JSON pairwise matrix dict into a numpy array."""
    n = len(criteria)
    matrix = np.zeros((n, n))
    for i, ci in enumerate(criteria):
        for j, cj in enumerate(criteria):
            matrix[i][j] = matrix_dict[ci][j]
    return matrix


def compute_ahp(matrix: np.ndarray, criteria: List[str]) -> dict:
    """
    Compute AHP weights from a pairwise comparison matrix.

    Steps:
    1. Normalize each column by its sum
    2. Average each row → priority vector (weights)
    3. Compute lambda_max
    4. Compute CI and CR
    5. Accept if CR < 0.10

    Returns dict with weights, lambda_max, CI, CR, and status.
    """
    n = len(criteria)

    # Step 1: Normalize columns
    col_sums = matrix.sum(axis=0)
    normalized = matrix / col_sums

    # Step 2: Priority vector (row averages)
    weights = normalized.mean(axis=1)

    # Step 3: Weighted sum vector
    weighted_sum = matrix @ weights

    # Step 4: Lambda max
    lambda_vector = weighted_sum / weights
    lambda_max = lambda_vector.mean()

    # Step 5: Consistency Index
    CI = (lambda_max - n) / (n - 1)

    # Step 6: Consistency Ratio
    ri = RI_TABLE.get(n, 1.64)
    CR = CI / ri if ri > 0 else 0.0

    consistent = CR < 0.10

    return {
        "criteria": criteria,
        "weights": dict(zip(criteria, weights.tolist())),
        "weights_array": weights.tolist(),
        "lambda_max": round(lambda_max, 6),
        "consistency_index": round(CI, 6),
        "consistency_ratio": round(CR, 6),
        "random_index": ri,
        "is_consistent": bool(consistent),
        "status": "ACCEPTED" if consistent else "REJECTED — CR >= 0.10, revise pairwise matrix"
    }


def print_ahp_report(result: dict):
    print("\n" + "=" * 60)
    print("AHP RESULTS — CRITERIA WEIGHTS")
    print("=" * 60)
    sorted_weights = sorted(result["weights"].items(), key=lambda x: -x[1])
    for rank, (criterion, weight) in enumerate(sorted_weights, 1):
        bar = "█" * int(weight * 200)
        print(f"  {rank:2}. {criterion:<30} {weight:.4f}  {bar}")
    print(f"\n  λ_max : {result['lambda_max']}")
    print(f"  CI    : {result['consistency_index']}")
    print(f"  RI    : {result['random_index']}")
    print(f"  CR    : {result['consistency_ratio']}")
    print(f"  Status: {result['status']}")
    print("=" * 60)


if __name__ == "__main__":
    import json, os

    matrix_path = os.path.join(os.path.dirname(__file__), "ahp_pairwise_matrix.json")
    with open(matrix_path) as f:
        data = json.load(f)

    matrix = load_matrix_from_dict(data["matrix"], CRITERIA)
    result = compute_ahp(matrix, CRITERIA)
    print_ahp_report(result)
