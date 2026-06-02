"""
Knowledge Base Filter
DV2573: Intelligent DSS for Drone Selection in Small EU Ports
Blekinge Institute of Technology

Applies hard constraints and regulatory rules to eliminate ineligible drones
BEFORE AHP/TOPSIS evaluation.
"""

from typing import List, Dict, Tuple

IP_RANK = {"IP43": 1, "IP53": 2, "IP55": 3, "IP67": 4}
AUTONOMY_RANK = {"manual": 0, "semi-autonomous": 1, "fully-autonomous": 2}
REDUNDANCY_RANK = {"none": 0, "basic": 1, "advanced": 2, "full-redundancy": 3}


def _ip_gte(drone_ip: str, min_ip: str) -> bool:
    return IP_RANK.get(drone_ip, 0) >= IP_RANK.get(min_ip, 0)


def _autonomy_gte(drone_lvl: str, min_lvl: str) -> bool:
    return AUTONOMY_RANK.get(drone_lvl, 0) >= AUTONOMY_RANK.get(min_lvl, 0)


def _redundancy_gte(drone_red: str, min_red: str) -> bool:
    return REDUNDANCY_RANK.get(drone_red, 0) >= REDUNDANCY_RANK.get(min_red, 0)


def apply_knowledge_base(drones: List[dict], scenario: dict) -> Tuple[List[dict], List[dict]]:
    """
    Filter drones using hard constraints from the scenario and regulatory rules.

    Returns:
        eligible   — list of drones that pass all hard constraints
        eliminated — list of dicts with drone info + reason for elimination
    """
    eligible = []
    eliminated = []
    constraints = scenario.get("hard_constraints", {})
    budget = scenario.get("budget", {})
    allowed_compliance = constraints.get("regulatory_compliance_allowed", [
        "Open-A1", "Open-A2", "Open-A3", "Specific", "Certified"
    ])

    for drone in drones:
        reasons = []

        # REG: Regulatory category allowed
        if drone["regulatory_compliance"] not in allowed_compliance:
            reasons.append(
                f"REG-01: Regulatory category '{drone['regulatory_compliance']}' "
                f"not allowed in this scenario (allowed: {allowed_compliance})"
            )

        # OPS-01: Minimum flight time
        min_ft = constraints.get("min_flight_time_min")
        if min_ft and drone["flight_time_min"] < min_ft:
            reasons.append(
                f"OPS-01: Flight time {drone['flight_time_min']}min < required {min_ft}min"
            )

        # OPS-02: Minimum flight range
        min_fr = constraints.get("min_flight_range_km")
        if min_fr and drone["flight_range_km"] < min_fr:
            reasons.append(
                f"OPS-02: Flight range {drone['flight_range_km']}km < required {min_fr}km"
            )

        # OPS-03: Weather resistance (IP rating)
        min_ip = constraints.get("min_weather_resistance_ip")
        if min_ip and not _ip_gte(drone["weather_resistance_ip"], min_ip):
            reasons.append(
                f"OPS-03: Weather resistance {drone['weather_resistance_ip']} < required {min_ip}"
            )

        # OPS-04: Real-time transmission
        if constraints.get("real_time_transmission_required") and not drone["real_time_transmission"]:
            reasons.append("OPS-04: Real-time transmission required but not supported")

        # OPS-05: Night vision
        if constraints.get("night_vision_required") and drone["night_vision"] == "none":
            reasons.append("OPS-05: Night vision required but not available")

        # OPS-06: Initial cost budget
        max_cost = budget.get("max_initial_cost_eur")
        if max_cost and drone["initial_cost_eur"] > max_cost:
            reasons.append(
                f"OPS-06: Initial cost €{drone['initial_cost_eur']:,} exceeds budget €{max_cost:,}"
            )

        # OPS-07: Operational cost budget
        max_op_cost = budget.get("max_operational_cost_eur_hr")
        if max_op_cost and drone["operational_cost_eur_hr"] > max_op_cost:
            reasons.append(
                f"OPS-07: Operational cost €{drone['operational_cost_eur_hr']}/hr exceeds budget €{max_op_cost}/hr"
            )

        # OPS-08: Minimum camera quality
        min_cam = constraints.get("min_camera_quality_mp")
        if min_cam and drone["camera_quality_mp"] < min_cam:
            reasons.append(
                f"OPS-08: Camera {drone['camera_quality_mp']}MP < required {min_cam}MP"
            )

        # OPS-09: Minimum payload
        min_payload = constraints.get("min_payload_capacity_kg")
        if min_payload and drone["payload_capacity_kg"] < min_payload:
            reasons.append(
                f"OPS-09: Payload {drone['payload_capacity_kg']}kg < required {min_payload}kg"
            )

        # OPS-10: Minimum sensor compatibility
        min_sensors = constraints.get("min_sensor_compatibility")
        if min_sensors and drone["sensor_compatibility"] < min_sensors:
            reasons.append(
                f"OPS-10: Sensor compatibility {drone['sensor_compatibility']} < required {min_sensors}"
            )

        # Autonomy level
        min_autonomy = constraints.get("min_autonomy_level")
        if min_autonomy and not _autonomy_gte(drone["autonomy_level"], min_autonomy):
            reasons.append(
                f"Autonomy '{drone['autonomy_level']}' < required '{min_autonomy}'"
            )

        # Redundancy
        min_redundancy = constraints.get("min_redundancy")
        if min_redundancy and not _redundancy_gte(drone["redundancy_failsafe"], min_redundancy):
            reasons.append(
                f"Redundancy '{drone['redundancy_failsafe']}' < required '{min_redundancy}'"
            )

        if reasons:
            eliminated.append({
                "id": drone["id"],
                "name": drone["name"],
                "elimination_reasons": reasons
            })
        else:
            eligible.append(drone)

    return eligible, eliminated


def print_filter_report(scenario: dict, eligible: List[dict], eliminated: List[dict]):
    print("\n" + "=" * 60)
    print(f"KNOWLEDGE BASE FILTER — {scenario['name']}")
    print("=" * 60)
    print(f"  Total drones evaluated : {len(eligible) + len(eliminated)}")
    print(f"  Eligible for TOPSIS    : {len(eligible)}")
    print(f"  Eliminated             : {len(eliminated)}")

    if eliminated:
        print("\n  ELIMINATED DRONES:")
        for e in eliminated:
            print(f"\n  ✗ {e['name']}")
            for r in e["elimination_reasons"]:
                print(f"      — {r}")

    print("\n  ELIGIBLE DRONES:")
    for d in eligible:
        print(f"  ✓ {d['name']}")
    print("=" * 60)


if __name__ == "__main__":
    import json, os

    base = os.path.dirname(__file__)
    with open(os.path.join(base, "drone_dataset.json")) as f:
        drone_data = json.load(f)
    with open(os.path.join(base, "port_scenarios.json")) as f:
        scenario_data = json.load(f)

    drones = drone_data["drones"]

    for scenario in scenario_data["scenarios"]:
        eligible, eliminated = apply_knowledge_base(drones, scenario)
        print_filter_report(scenario, eligible, eliminated)
