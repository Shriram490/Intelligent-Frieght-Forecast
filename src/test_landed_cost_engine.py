import sys
from pathlib import Path

# Add src directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from landed_cost_engine import calculate_landed_cost


def run_tests():
    print("=" * 80)
    print("INTEGRATED LANDED COST ENGINE COMPREHENSIVE UNIT TEST SUITE")
    print("=" * 80)

    # 1. Test Valid Complete Calculation (50,000 MT Coal, Newcastle -> Paradip, Panamax)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 1: Valid Complete Landed Cost Calculation (All Inputs Provided)")
    print("--------------------------------------------------------------------------------")
    res1 = calculate_landed_cost(
        commodity="Coal, Australian",
        quantity_mt=50000,
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        usd_per_mt=25.50,
        user_annual_throughput_mt=400000,
        vessel_gt=70000,
        port_stay_hours=48,
        usd_to_inr_rate=83.5,
        planned_shipment_date="2026-05-01"
    )
    assert res1["is_complete_estimate"] is True
    assert res1["is_transit_feasible"] is True
    assert res1["is_commodity_value_available"] is True
    assert res1["is_ocean_freight_available"] is True
    assert res1["is_port_charges_complete"] is True
    assert res1["landed_cost_estimate_usd"] is not None
    assert res1["landed_cost_estimate_inr"] is not None
    assert res1["landed_cost_per_mt_usd"] > 0
    assert len(res1["missing_components"]) == 0

    print(f"  Commodity Purchase Value USD : ${res1['commodity_value_usd']:>15,.2f} USD")
    print(f"  Ocean Freight Cost USD       : ${res1['ocean_freight_cost_usd']:>15,.2f} USD")
    print(f"  Port Charges INR             : Rs.{res1['port_charges_selected_services_total_inr']:>14,.2f} INR")
    print(f"  Port Charges USD             : ${res1['port_charges_selected_services_total_usd']:>15,.2f} USD")
    print(f"  Complete Landed Cost USD     : ${res1['landed_cost_estimate_usd']:>15,.2f} USD (@ Rs.83.5/USD)")
    print(f"  Complete Landed Cost INR     : Rs.{res1['landed_cost_estimate_inr']:>14,.2f} INR")
    print(f"  Landed Cost Per MT USD       : ${res1['landed_cost_per_mt_usd']:>15,.2f} USD/MT")
    print(f"  Completeness Flag            : {res1['is_complete_estimate']}")
    print("[PASS] Test 1 passed successfully!")

    # 2. Test Unavailable Ocean Freight Rate Handling
    print("\n--------------------------------------------------------------------------------")
    print("TEST 2: Unavailable Ocean Freight Rate Handling (usd_per_mt & charter_usd_per_day = None)")
    print("--------------------------------------------------------------------------------")
    res2 = calculate_landed_cost(
        commodity="Coal, Australian",
        quantity_mt=50000,
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        usd_per_mt=None,
        charter_usd_per_day=None,
        user_annual_throughput_mt=400000,
        vessel_gt=70000,
        port_stay_hours=48,
        usd_to_inr_rate=83.5
    )
    assert res2["is_ocean_freight_available"] is False
    assert res2["is_complete_estimate"] is False
    assert res2["landed_cost_estimate_usd"] is None
    assert res2["partial_landed_cost_usd"] is not None
    assert any("Ocean Freight" in m for m in res2["missing_components"])
    print(f"  Ocean Freight Available      : {res2['is_ocean_freight_available']}")
    print(f"  Is Complete Estimate         : {res2['is_complete_estimate']}")
    print(f"  Partial Landed Cost USD      : ${res2['partial_landed_cost_usd']:,.2f} USD")
    print(f"  Missing Components           : {res2['missing_components']}")
    print("[PASS] Test 2 passed successfully!")

    # 3. Test Incomplete Port Charges Handling (Missing user_annual_throughput_mt)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 3: Incomplete Port Charges Handling (Missing Annual Throughput)")
    print("--------------------------------------------------------------------------------")
    res3 = calculate_landed_cost(
        commodity="Coal, Australian",
        quantity_mt=50000,
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        usd_per_mt=25.50,
        user_annual_throughput_mt=None,
        usd_to_inr_rate=83.5
    )
    assert res3["is_port_charges_complete"] is False
    assert res3["is_complete_estimate"] is False
    assert res3["landed_cost_estimate_usd"] is None
    assert any("Port Charges Incomplete" in m for m in res3["missing_components"])
    print(f"  Port Charges Complete        : {res3['is_port_charges_complete']}")
    print(f"  Is Complete Estimate         : {res3['is_complete_estimate']}")
    print(f"  Missing Components           : {res3['missing_components']}")
    print("[PASS] Test 3 passed successfully!")

    # 4. Test Currency Separation Without Exchange Rate
    print("\n--------------------------------------------------------------------------------")
    print("TEST 4: Currency Isolation Without Exchange Rate (usd_to_inr_rate = None)")
    print("--------------------------------------------------------------------------------")
    res4 = calculate_landed_cost(
        commodity="Coal, Australian",
        quantity_mt=50000,
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        usd_per_mt=25.50,
        user_annual_throughput_mt=400000,
        vessel_gt=70000,
        port_stay_hours=48,
        usd_to_inr_rate=None
    )
    assert res4["is_complete_estimate"] is False
    assert res4["landed_cost_estimate_usd"] is None
    assert res4["partial_landed_cost_inr"] is None
    assert any("Exchange Rate" in m for m in res4["missing_components"])
    print(f"  Native USD Total             : ${res4['partial_landed_cost_usd']:,.2f} USD")
    print(f"  Native INR Total             : Rs.{res4['port_charges_selected_services_total_inr']:,.2f} INR")
    print(f"  Missing Components           : {res4['missing_components']}")
    print("[PASS] Test 4 passed successfully!")

    # 5. Test Invalid Input Validation
    print("\n--------------------------------------------------------------------------------")
    print("TEST 5: Invalid Input Validation (quantity_mt <= 0)")
    print("--------------------------------------------------------------------------------")
    for invalid_qty in [0, -500, None]:
        try:
            calculate_landed_cost("Coal, Australian", invalid_qty, "Newcastle", "Paradip", "Panamax")
            assert False, f"Should have raised ValueError for quantity={invalid_qty}"
        except ValueError as e:
            print(f"  Caught expected error for quantity={invalid_qty}: {e}")
    print("[PASS] Test 5 passed successfully!")

    # 6. Test Transit Infeasibility Independent of Cost Calculation
    print("\n--------------------------------------------------------------------------------")
    print("TEST 6: Transit Infeasibility Independent of Cost Calculation (10 Requested Days)")
    print("--------------------------------------------------------------------------------")
    res6 = calculate_landed_cost(
        commodity="Coal, Australian",
        quantity_mt=50000,
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        usd_per_mt=25.50,
        requested_delivery_days=10,
        user_annual_throughput_mt=400000,
        vessel_gt=70000,
        port_stay_hours=48,
        usd_to_inr_rate=83.5,
        planned_shipment_date="2026-05-01"
    )
    assert res6["is_transit_feasible"] is False
    assert res6["is_complete_estimate"] is True  # Cost estimate remains valid and complete independently
    assert res6["commodity_value_usd"] > 0
    assert res6["ocean_freight_cost_usd"] > 0
    print(f"  Transit Feasible             : {res6['is_transit_feasible']}")
    print(f"  Cost Estimate Complete       : {res6['is_complete_estimate']}")
    print(f"  Explanation                  : {res6['transit_time_summary']['status_explanation']}")
    print("[PASS] Test 6 passed successfully!")

    # 7. Test Partial-Estimate Handling (Missing USD/INR exchange rate)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 7: Partial Estimate Handling (Missing Exchange Rate)")
    print("--------------------------------------------------------------------------------")
    res7 = calculate_landed_cost(
        commodity="Coal, Australian",
        quantity_mt=50000,
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        usd_per_mt=25.50,
        user_annual_throughput_mt=400000,
        usd_to_inr_rate=None,
        planned_shipment_date="2026-05-01"
    )
    assert res7["is_complete_estimate"] is False
    assert res7["landed_cost_estimate_usd"] is None
    assert res7["partial_landed_cost_usd"] > 0
    print(f"  Partial Landed Cost USD      : ${res7['partial_landed_cost_usd']:,.2f} USD")
    print(f"  Complete Estimate Flag       : {res7['is_complete_estimate']}")
    print(f"  Missing Components           : {res7['missing_components']}")
    print("[PASS] Test 7 passed successfully!")

    # 8. Test Determinism
    print("\n--------------------------------------------------------------------------------")
    print("TEST 8: Determinism Check")
    print("--------------------------------------------------------------------------------")
    res_a = calculate_landed_cost("Coal, Australian", 50000, "Newcastle", "Paradip", "Panamax", usd_per_mt=25.50, user_annual_throughput_mt=400000, vessel_gt=70000, port_stay_hours=48, usd_to_inr_rate=83.5, planned_shipment_date="2026-05-01")
    res_b = calculate_landed_cost("Coal, Australian", 50000, "Newcastle", "Paradip", "Panamax", usd_per_mt=25.50, user_annual_throughput_mt=400000, vessel_gt=70000, port_stay_hours=48, usd_to_inr_rate=83.5, planned_shipment_date="2026-05-01")
    assert res_a == res_b
    print("  Two consecutive calls produced identical result dicts.")
    print("[PASS] Test 8 passed successfully!")

    # 9. Test Calculation Verification (Check 4: Component sum, converted total, per-MT)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 9: Independent Calculation Verification (Check 4)")
    print("--------------------------------------------------------------------------------")
    # Sample inputs: Commodity USD 5,383,500; Ocean Freight USD 1,275,000; Port INR 12,986,500; Exchange Rate 83.50
    res9 = calculate_landed_cost(
        commodity="Coal, Australian",
        quantity_mt=50000,
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        usd_per_mt=25.50,
        user_annual_throughput_mt=400000,
        vessel_gt=70000,
        port_stay_hours=48,
        usd_to_inr_rate=83.50,
        planned_shipment_date="2026-05-01"
    )
    expected_commodity_usd = 5383500.00
    expected_freight_usd = 1275000.00
    expected_port_inr = 12986500.00
    expected_port_usd_converted = round(expected_port_inr / 83.50, 2)  # 155,526.95 USD
    expected_total_usd = round(expected_commodity_usd + expected_freight_usd + expected_port_usd_converted, 2)  # 6,814,026.95 USD
    expected_per_mt = round(expected_total_usd / 50000, 2)  # 136.28 USD/MT

    assert abs(res9["commodity_value_usd"] - expected_commodity_usd) < 0.01
    assert abs(res9["ocean_freight_cost_usd"] - expected_freight_usd) < 0.01
    assert abs(res9["port_charges_selected_services_total_inr"] - expected_port_inr) < 0.01
    assert abs(res9["landed_cost_estimate_usd"] - expected_total_usd) < 0.01
    assert abs(res9["landed_cost_per_mt_usd"] - expected_per_mt) < 0.01
    print(f"  Commodity USD Match   : ${res9['commodity_value_usd']:,.2f} USD == ${expected_commodity_usd:,.2f} USD")
    print(f"  Freight USD Match     : ${res9['ocean_freight_cost_usd']:,.2f} USD == ${expected_freight_usd:,.2f} USD")
    print(f"  Port INR Match        : Rs.{res9['port_charges_selected_services_total_inr']:,.2f} INR == Rs.{expected_port_inr:,.2f} INR")
    print(f"  Port Converted USD    : ${expected_port_usd_converted:,.2f} USD")
    print(f"  Total Landed Cost USD : ${res9['landed_cost_estimate_usd']:,.2f} USD == ${expected_total_usd:,.2f} USD")
    print(f"  Per MT USD            : ${res9['landed_cost_per_mt_usd']:,.2f} USD/MT == ${expected_per_mt:,.2f} USD/MT")
    print("[PASS] Test 9 passed successfully!")

    # 10. Test Scope Completeness Distinction (Check 1 & Check 5)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 10: Scope Completeness Distinction (is_complete_within_scope vs is_all_in_cost_known)")
    print("--------------------------------------------------------------------------------")
    res10 = calculate_landed_cost(
        commodity="Coal, Australian",
        quantity_mt=50000,
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        usd_per_mt=25.50,
        user_annual_throughput_mt=400000,
        usd_to_inr_rate=83.5,
        planned_shipment_date="2026-05-01"
    )
    assert res10["is_complete_within_scope"] is True
    assert res10["is_all_in_cost_known"] is False  # False because berth hire (vessel_gt/stay_hours), custom inland and insurance are excluded
    assert "Inland transport beyond destination port" in res10["scope_summary"]["excluded"]
    print(f"  Complete Within Scope : {res10['is_complete_within_scope']}")
    print(f"  All-In Cost Known     : {res10['is_all_in_cost_known']}")
    print(f"  Excluded Categories   : {res10['scope_summary']['excluded']}")
    print("[PASS] Test 10 passed successfully!")

    print("\n" + "=" * 80)
    print("ALL UNIT TESTS PASSED SUCCESSFULLY (10/10 PASS)!")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
