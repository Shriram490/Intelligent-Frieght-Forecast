import sys
from pathlib import Path

# Add src directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from scenario_engine import (
    get_all_supported_scenarios,
    evaluate_scenario_candidates,
    rank_and_optimize_scenarios
)


def run_tests():
    print("=" * 80)
    print("INTEGRATED SCENARIO EVALUATION & OPTIMIZATION ENGINE UNIT TESTS")
    print("=" * 80)

    # 1. Test Multiple Routes and Vessels Evaluation
    print("\n--------------------------------------------------------------------------------")
    print("TEST 1: Multiple Routes and Vessels Evaluation with User-Supplied Rates")
    print("--------------------------------------------------------------------------------")
    # Provide explicit freight rates for different candidate routes to Paradip
    rates = {
        ("Newcastle", "Paradip", "Panamax"): {"usd_per_mt": 25.50},
        ("Newcastle", "Paradip", "Capesize"): {"usd_per_mt": 21.00},
        ("Hay Point", "Paradip", "Panamax"): {"usd_per_mt": 24.00},
        ("Hay Point", "Paradip", "Capesize"): {"usd_per_mt": 20.00},
    }

    res1 = evaluate_scenario_candidates(
        commodity="Coal, Australian",
        quantity_mt=50000,
        filter_destination="Paradip",
        planned_shipment_date="2026-05-01",
        user_annual_throughput_mt=400000,
        freight_rates_by_scenario=rates,
        vessel_gt=70000,
        port_stay_hours=48,
        usd_to_inr_rate=83.5
    )

    assert res1["total_evaluated"] > 0
    assert res1["total_feasible"] > 0
    assert res1["total_with_complete_cost"] >= 4
    assert res1["recommendations"]["lowest_cost_option"] is not None
    assert res1["recommendations"]["fastest_delivery_option"] is not None

    cheapest = res1["recommendations"]["lowest_cost_option"]
    fastest = res1["recommendations"]["fastest_delivery_option"]
    print(f"  Cheapest Feasible Candidate : {cheapest['scenario_name']} @ ${cheapest['landed_cost_usd']:,.2f} USD")
    print(f"  Fastest Feasible Candidate  : {fastest['scenario_name']} @ {fastest['transit_days']:.1f} days")
    print(f"  Lowest Cost Reason          : {res1['recommendations']['lowest_cost_reason']}")
    print("[PASS] Test 1 passed successfully!")

    # 2. Test Multi-Voyage Cargo Capacity Planning
    print("\n--------------------------------------------------------------------------------")
    print("TEST 2: Multi-Voyage Capacity Planning (Large Cargo: 150,000 MT)")
    print("--------------------------------------------------------------------------------")
    res2 = evaluate_scenario_candidates(
        commodity="Coal, Australian",
        quantity_mt=150000,
        candidate_configs=[
            {"origin": "Newcastle", "destination": "Paradip", "vessel_type": "Panamax"},   # 75k MT typical -> 2 loads
            {"origin": "Newcastle", "destination": "Paradip", "vessel_type": "Capesize"},  # 150k MT typical -> 1 load
        ],
        planned_shipment_date="2026-05-01",
        user_annual_throughput_mt=400000,
        default_usd_per_mt=25.00,
        dispatch_mode="sequential",
        usd_to_inr_rate=83.5
    )

    cands2 = {c["vessel_type"]: c for c in res2["all_candidates"]}
    assert cands2["Panamax"]["loads_required"] == 2
    assert cands2["Capesize"]["loads_required"] == 1
    # Sequential dispatch should multiply duration for Panamax
    assert cands2["Panamax"]["transit_days"] > cands2["Capesize"]["transit_days"]
    print(f"  Panamax Loads Required      : {cands2['Panamax']['loads_required']} loads ({cands2['Panamax']['transit_days']:.1f} days sequential)")
    print(f"  Capesize Loads Required     : {cands2['Capesize']['loads_required']} loads ({cands2['Capesize']['transit_days']:.1f} days sequential)")
    print("[PASS] Test 2 passed successfully!")

    # 3. Test Deadline Feasibility Rejection
    print("\n--------------------------------------------------------------------------------")
    print("TEST 3: Delivery Deadline Compliance & Infeasible Candidate Rejection")
    print("--------------------------------------------------------------------------------")
    # Setting tight deadline of 12.0 days (Newcastle -> Paradip requires >= 16.5d, South Kalimantan -> Paradip requires ~11.5d)
    res3 = evaluate_scenario_candidates(
        commodity="Coal, Australian",
        quantity_mt=50000,
        candidate_configs=[
            {"origin": "Newcastle", "destination": "Paradip", "vessel_type": "Panamax"},        # 16.5 days -> Infeasible
            {"origin": "South Kalimantan", "destination": "Paradip", "vessel_type": "Panamax"}, # 11.6 days -> Feasible
        ],
        requested_delivery_days=13.0,
        planned_shipment_date="2026-05-01",
        user_annual_throughput_mt=400000,
        default_usd_per_mt=25.00,
        usd_to_inr_rate=83.5
    )

    cands3 = {c["origin"]: c for c in res3["all_candidates"]}
    assert cands3["Newcastle"]["is_transit_feasible"] is False
    assert "REJECTED" in cands3["Newcastle"]["rejection_reason"]
    assert cands3["South Kalimantan"]["is_transit_feasible"] is True

    assert res3["recommendations"]["deadline_compliant_lowest_cost"] is not None
    assert res3["recommendations"]["deadline_compliant_lowest_cost"]["origin"] == "South Kalimantan"
    print(f"  Newcastle Feasible          : {cands3['Newcastle']['is_transit_feasible']} (Reason: {cands3['Newcastle']['rejection_reason'][:50]}...)")
    print(f"  South Kalimantan Feasible   : {cands3['South Kalimantan']['is_transit_feasible']}")
    print(f"  Deadline Recommendation     : {res3['recommendations']['deadline_compliant_lowest_cost']['scenario_name']}")
    print("[PASS] Test 3 passed successfully!")

    # 4. Test Missing Monetary Freight Rate Handling (No Ranking of Unknown Costs)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 4: Missing Monetary Freight Rate Handling (Prevent Ranking Incomplete Costs)")
    print("--------------------------------------------------------------------------------")
    res4 = evaluate_scenario_candidates(
        commodity="Coal, Australian",
        quantity_mt=50000,
        candidate_configs=[
            {"origin": "Newcastle", "destination": "Paradip", "vessel_type": "Panamax"},
        ],
        planned_shipment_date="2026-05-01",
        user_annual_throughput_mt=400000,
        default_usd_per_mt=None,  # No rate provided!
        default_charter_usd_per_day=None,
        usd_to_inr_rate=83.5
    )

    cand4 = res4["all_candidates"][0]
    assert cand4["is_transit_feasible"] is True
    assert cand4["is_cost_known"] is False
    assert cand4["is_complete_within_scope"] is False
    assert len(res4["ranked_by_cost"]) == 0  # Cannot rank unpriced candidate
    assert res4["recommendations"]["lowest_cost_option"] is None
    print(f"  Feasible                    : {cand4['is_transit_feasible']}")
    print(f"  Cost Known                  : {cand4['is_cost_known']}")
    print(f"  Ranked By Cost Count        : {len(res4['ranked_by_cost'])}")
    print(f"  Lowest Cost Notice          : {res4['recommendations']['lowest_cost_reason']}")
    print("[PASS] Test 4 passed successfully!")

    # 5. Test Unsupported Route-Vessel Configuration Rejection
    print("\n--------------------------------------------------------------------------------")
    print("TEST 5: Unsupported Route and Vessel Configuration Handling")
    print("--------------------------------------------------------------------------------")
    res5 = evaluate_scenario_candidates(
        commodity="Coal, Australian",
        quantity_mt=50000,
        candidate_configs=[
            {"origin": "London", "destination": "Paradip", "vessel_type": "Panamax"},     # Non-existent route
            {"origin": "Newcastle", "destination": "Paradip", "vessel_type": "Submarine"}, # Unsupported vessel
            {"origin": "Newcastle", "destination": "Paradip", "vessel_type": "Panamax"},   # Valid candidate
        ],
        planned_shipment_date="2026-05-01",
        user_annual_throughput_mt=400000,
        default_usd_per_mt=25.50,
        usd_to_inr_rate=83.5
    )

    assert len(res5["all_candidates"]) == 3
    assert len(res5["feasible_candidates"]) == 1
    rejections = [c["rejection_reason"] for c in res5["infeasible_candidates"]]
    assert any("Unsupported route-vessel" in r for r in rejections)
    print(f"  Total Evaluated             : {res5['total_evaluated']}")
    print(f"  Total Feasible              : {res5['total_feasible']}")
    print(f"  Rejections                  : {rejections}")
    print("[PASS] Test 5 passed successfully!")

    # 6. Test Incomplete Port Charges (Missing user_annual_throughput_mt)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 6: Incomplete Port Charges Handling (Missing Throughput)")
    print("--------------------------------------------------------------------------------")
    res6 = evaluate_scenario_candidates(
        commodity="Coal, Australian",
        quantity_mt=50000,
        candidate_configs=[
            {"origin": "Newcastle", "destination": "Paradip", "vessel_type": "Panamax"},
        ],
        planned_shipment_date="2026-05-01",
        user_annual_throughput_mt=None,  # Missing throughput
        default_usd_per_mt=25.50,
        usd_to_inr_rate=83.5
    )

    cand6 = res6["all_candidates"][0]
    assert cand6["is_complete_within_scope"] is False
    assert cand6["is_cost_known"] is False
    assert len(res6["ranked_by_cost"]) == 0
    print(f"  Complete Within Scope       : {cand6['is_complete_within_scope']}")
    print(f"  Missing Components          : {cand6['missing_components']}")
    print("[PASS] Test 6 passed successfully!")

    # 7. Test Global Optimality Disclaimer Transparency
    print("\n--------------------------------------------------------------------------------")
    print("TEST 7: Transparent Optimality Transparency Check")
    print("--------------------------------------------------------------------------------")
    # Mixed pool: One candidate has cost, one candidate lacks cost
    rates7 = {
        ("Newcastle", "Paradip", "Panamax"): {"usd_per_mt": 25.50},
        # Hay Point lacks rate
    }
    res7 = evaluate_scenario_candidates(
        commodity="Coal, Australian",
        quantity_mt=50000,
        candidate_configs=[
            {"origin": "Newcastle", "destination": "Paradip", "vessel_type": "Panamax"},
            {"origin": "Hay Point", "destination": "Paradip", "vessel_type": "Panamax"},
        ],
        planned_shipment_date="2026-05-01",
        user_annual_throughput_mt=400000,
        freight_rates_by_scenario=rates7,
        usd_to_inr_rate=83.5
    )
    assert res7["recommendations"]["is_global_optimality_claimable"] is False
    assert "NOTICE:" in res7["recommendations"]["optimality_disclaimer"]
    print(f"  Global Optimality Claimable : {res7['recommendations']['is_global_optimality_claimable']}")
    print(f"  Disclaimer                  : {res7['recommendations']['optimality_disclaimer']}")
    print("[PASS] Test 7 passed successfully!")

    print("\n" + "=" * 80)
    print("ALL SCENARIO ENGINE UNIT TESTS PASSED SUCCESSFULLY (7/7 PASS)!")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
