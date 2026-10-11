import sys
from pathlib import Path

# Add src directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from transit_time_engine import (
    load_route_vessel_specs,
    get_available_routes,
    get_available_vessels_for_route,
    calculate_transit_time
)


def run_tests():
    print("=" * 80)
    print("TRANSIT TIME ENGINE COMPREHENSIVE UNIT TEST SUITE")
    print("=" * 80)

    # Load specs once
    specs_df = load_route_vessel_specs()
    print(f"\n[PASS] Loaded route specs dataset successfully ({len(specs_df)} unique configurations).")

    # 1. Available Routes Check
    routes = get_available_routes(specs_df)
    print(f"[PASS] Available routes found: {len(routes)} route pairs.")

    # 2. Test Case 1: Newcastle to Paradip with Panamax (Quantity within capacity: 60,000 MT)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 1: Standard Route (Newcastle -> Paradip with Panamax, 60,000 MT)")
    print("--------------------------------------------------------------------------------")
    res1 = calculate_transit_time(
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        quantity_mt=60000,
        requested_delivery_days=20,
        specs_df=specs_df
    )
    assert res1["origin"] == "Newcastle"
    assert res1["destination"] == "Paradip"
    assert res1["vessel_type"] == "Panamax"
    assert res1["distance_nm"] == 3900.0
    assert res1["speed_knots"] == 13.0
    assert res1["pure_sailing_days"] == 12.5  # 3900 / (13 * 24) = 12.5
    assert res1["adjusted_sailing_days"] == 12.5
    assert res1["port_allowance_days"] == 4.0
    assert res1["min_feasible_delivery_days"] == 16.5
    assert res1["total_estimated_delivery_days"] == 16.5
    assert res1["loads_required"] == 1
    assert res1["exceeds_single_vessel_capacity"] is False
    assert res1["is_feasible"] is True
    print("Result:")
    for k, v in res1.items():
        if k != "assumptions":
            print(f"  {k:<32}: {v}")
    print("[PASS] Test 1 passed successfully!")

    # 3. Test Case 2: Zero / Negative Cargo Validation
    print("\n--------------------------------------------------------------------------------")
    print("TEST 2: Zero & Negative Cargo Quantity Validation")
    print("--------------------------------------------------------------------------------")
    for invalid_qty in [0, -500, None]:
        try:
            calculate_transit_time("Newcastle", "Paradip", "Panamax", invalid_qty, specs_df=specs_df)
            assert False, f"Should have raised ValueError for cargo quantity {invalid_qty}"
        except ValueError as e:
            print(f"  Caught expected error for quantity={invalid_qty}: {e}")
    print("[PASS] Test 2 passed successfully!")

    # 4. Test Case 3: Invalid Route Validation
    print("\n--------------------------------------------------------------------------------")
    print("TEST 3: Invalid Route Validation (Atlantis -> Paradip)")
    print("--------------------------------------------------------------------------------")
    try:
        calculate_transit_time("Atlantis", "Paradip", "Panamax", 50000, specs_df=specs_df)
        assert False, "Should have raised ValueError for invalid route."
    except ValueError as e:
        print(f"  Caught expected error: {e}")
    print("[PASS] Test 3 passed successfully!")

    # 5. Test Case 4: Unsupported Vessel Type Validation
    print("\n--------------------------------------------------------------------------------")
    print("TEST 4: Unsupported Vessel Type Validation (Newcastle -> Paradip with Submarine)")
    print("--------------------------------------------------------------------------------")
    try:
        calculate_transit_time("Newcastle", "Paradip", "Submarine", 50000, specs_df=specs_df)
        assert False, "Should have raised ValueError for unsupported vessel."
    except ValueError as e:
        print(f"  Caught expected error: {e}")
    print("[PASS] Test 4 passed successfully!")

    # 6. Test Case 5: Invalid Requested Delivery Time, Margin, Port Allowance & Dispatch Mode
    print("\n--------------------------------------------------------------------------------")
    print("TEST 5: Invalid Parameters Validation (Delivery Time <= 0, Margin < 0, Mode)")
    print("--------------------------------------------------------------------------------")
    invalid_cases = [
        ({"requested_delivery_days": 0}, "Requested delivery days must be a positive number"),
        ({"requested_delivery_days": -10}, "Requested delivery days must be a positive number"),
        ({"delay_margin_pct": -5.0}, "Delay margin percentage cannot be negative"),
        ({"port_allowance_days": -2.0}, "Port allowance days cannot be negative"),
        ({"dispatch_mode": "instant"}, "Dispatch mode must be either 'parallel' or 'sequential'")
    ]
    for kwargs, err_substr in invalid_cases:
        try:
            calculate_transit_time("Newcastle", "Paradip", "Panamax", 50000, **kwargs, specs_df=specs_df)
            assert False, f"Should have raised ValueError for invalid kwargs: {kwargs}"
        except ValueError as e:
            assert err_substr in str(e)
            print(f"  Caught expected error for {kwargs}: {e}")
    print("[PASS] Test 5 passed successfully!")

    # 7. Test Case 6: Capacity Boundary Conditions (Exact Capacity vs Exceeding Capacity)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 6: Capacity Boundary Conditions (75,000 MT vs 75,001 MT on Panamax)")
    print("--------------------------------------------------------------------------------")
    res_exact = calculate_transit_time("Newcastle", "Paradip", "Panamax", 75000, specs_df=specs_df)
    assert res_exact["exceeds_single_vessel_capacity"] is False
    assert res_exact["loads_required"] == 1
    print(f"  Exact Capacity (75,000 MT): Exceeds={res_exact['exceeds_single_vessel_capacity']}, Loads={res_exact['loads_required']}")

    res_over = calculate_transit_time("Newcastle", "Paradip", "Panamax", 75001, specs_df=specs_df)
    assert res_over["exceeds_single_vessel_capacity"] is True
    assert res_over["loads_required"] == 2
    print(f"  Over Capacity (75,001 MT) : Exceeds={res_over['exceeds_single_vessel_capacity']}, Loads={res_over['loads_required']}")
    print("[PASS] Test 6 passed successfully!")

    # 8. Test Case 7: Delay Margin Calculation Impact
    print("\n--------------------------------------------------------------------------------")
    print("TEST 7: Configurable Delay Margin Impact (0% vs 10% Sea Delay Margin)")
    print("--------------------------------------------------------------------------------")
    res_margin0 = calculate_transit_time("Newcastle", "Paradip", "Panamax", 60000, delay_margin_pct=0.0, specs_df=specs_df)
    res_margin10 = calculate_transit_time("Newcastle", "Paradip", "Panamax", 60000, delay_margin_pct=10.0, specs_df=specs_df)

    # Pure sailing is 12.5 days. 10% delay margin adds 1.25 days -> 13.75 days adjusted sailing.
    assert res_margin0["pure_sailing_days"] == 12.5
    assert res_margin0["adjusted_sailing_days"] == 12.5
    assert res_margin10["pure_sailing_days"] == 12.5
    assert res_margin10["adjusted_sailing_days"] == 13.75
    assert res_margin10["min_feasible_delivery_days"] == 17.75  # 13.75 + 4.0
    print(f"  0% Margin  : Pure Sailing = {res_margin0['pure_sailing_days']}d, Adjusted = {res_margin0['adjusted_sailing_days']}d, Total = {res_margin0['min_feasible_delivery_days']}d")
    print(f"  10% Margin : Pure Sailing = {res_margin10['pure_sailing_days']}d, Adjusted = {res_margin10['adjusted_sailing_days']}d, Total = {res_margin10['min_feasible_delivery_days']}d")
    print("[PASS] Test 7 passed successfully!")

    # 9. Test Case 8: Multi-Load Dispatch Modes (Parallel vs Sequential)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 8: Multi-Load Dispatch Modes (150,000 MT Panamax: 2 Loads)")
    print("--------------------------------------------------------------------------------")
    res_parallel = calculate_transit_time("Newcastle", "Paradip", "Panamax", 150000, dispatch_mode="parallel", specs_df=specs_df)
    res_sequential = calculate_transit_time("Newcastle", "Paradip", "Panamax", 150000, dispatch_mode="sequential", specs_df=specs_df)

    assert res_parallel["loads_required"] == 2
    assert res_parallel["total_estimated_delivery_days"] == 16.5  # Does NOT multiply voyage duration
    assert res_sequential["loads_required"] == 2
    assert res_sequential["total_estimated_delivery_days"] == 33.0  # 2 * 16.5 = 33.0 days

    print(f"  Parallel Mode   : Loads={res_parallel['loads_required']}, Estimated Delivery Days={res_parallel['total_estimated_delivery_days']}d")
    print(f"  Sequential Mode : Loads={res_sequential['loads_required']}, Estimated Delivery Days={res_sequential['total_estimated_delivery_days']}d")
    print("[PASS] Test 8 passed successfully!")

    # 10. Test Case 9: Delivery Time Feasibility Rejection
    print("\n--------------------------------------------------------------------------------")
    print("TEST 9: Requested Delivery Time Feasibility Rejection (10 Days vs 16.5 Min Feasible)")
    print("--------------------------------------------------------------------------------")
    res_short = calculate_transit_time("Newcastle", "Paradip", "Panamax", 60000, requested_delivery_days=10, specs_df=specs_df)
    assert res_short["is_feasible"] is False
    assert "REJECTED" in res_short["delivery_status_explanation"]
    print(f"  Explanation: {res_short['delivery_status_explanation']}")
    print("[PASS] Test 9 passed successfully!")

    # 11. Test Case 10: Determinism Verification
    print("\n--------------------------------------------------------------------------------")
    print("TEST 10: Determinism Check")
    print("--------------------------------------------------------------------------------")
    res_a = calculate_transit_time("Newcastle", "Paradip", "Panamax", 60000, delay_margin_pct=5.0, specs_df=specs_df)
    res_b = calculate_transit_time("Newcastle", "Paradip", "Panamax", 60000, delay_margin_pct=5.0, specs_df=specs_df)
    assert res_a == res_b
    print("  Two consecutive calls with identical inputs produced identical result dicts.")
    print("[PASS] Test 10 passed successfully!")

    print("\n" + "=" * 80)
    print("ALL UNIT TESTS PASSED SUCCESSFULLY (10/10 PASS)!")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
