import sys
from pathlib import Path

# Add src directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from port_charges_engine import (
    load_all_port_tariffs,
    list_available_tariff_categories,
    calculate_port_charges
)


def run_tests():
    print("=" * 80)
    print("FINAL TARGETED PORT CHARGES ENGINE UNIT TEST SUITE")
    print("=" * 80)

    # 1. Dataset Count & Reconciliation (18 Parquet datasets)
    tariffs = load_all_port_tariffs()
    print(f"\n[PASS] Loaded all port tariff Parquet files successfully ({len(tariffs)} datasets).")
    assert len(tariffs) == 18

    cats = list_available_tariff_categories(tariffs)
    assert "Paradip" in cats["supported_ports"]
    assert cats["total_tariff_datasets"] == 18
    print(f"[PASS] Tariff categories summary verified (Total datasets: {cats['total_tariff_datasets']}).")

    # 2. Test Standard Cargo Charges Calculation with User Annual Throughput
    print("\n--------------------------------------------------------------------------------")
    print("TEST 2: Standard Cargo Charges (50,000 MT Coal Foreign with Annual Throughput)")
    print("--------------------------------------------------------------------------------")
    res1 = calculate_port_charges(
        quantity_mt=50000,
        commodity="Coal/Coke",
        traffic_type="Foreign",
        user_annual_throughput_mt=400000,
        planned_shipment_date="2026-05-01",
        processed_dir=Path(__file__).resolve().parent.parent / "data" / "processed"
    )
    assert res1["port"] == "Paradip"
    assert res1["quantity_mt"] == 50000.0
    assert res1["traffic_type"] == "Foreign"
    assert len(res1["calculated_charges"]) >= 6
    assert res1["selected_services_total_inr"] > 0
    assert res1["selected_services_total_usd"] == 0.0
    print("Calculated Charges Breakdown:")
    for ch in res1["calculated_charges"]:
        print(f"  - {ch['service']:<38}: Rs.{ch['charge_amount']:>12,.2f} INR ({ch['formula']})")
    print(f"  SELECTED SERVICES TOTAL INR: Rs.{res1['selected_services_total_inr']:,.2f} INR")
    print("[PASS] Test 2 passed successfully!")

    # 3. Test Missing Annual Throughput Handling (Wharfage uncalculated notice returned)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 3: Missing Annual Throughput Handling (Wharfage Not Calculated)")
    print("--------------------------------------------------------------------------------")
    res_no_thru = calculate_port_charges(quantity_mt=50000, commodity="Coal/Coke", user_annual_throughput_mt=None, selected_services=["wharfage"])
    assert len(res_no_thru["calculated_charges"]) == 0
    assert len(res_no_thru["uncalculated_notices"]) == 1
    assert res_no_thru["is_complete_port_total"] is False
    assert res_no_thru["is_complete_selected_services"] is False
    print(f"  Notice returned for missing throughput: {res_no_thru['uncalculated_notices'][0]['reason']}")
    print(f"  Completeness flag is_complete_port_total: {res_no_thru['is_complete_port_total']}")
    print("[PASS] Test 3 passed successfully!")

    # 4. Test Missing Free Storage Period Handling (Demurrage Not Calculated)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 4: Missing Free Storage Period Handling (Demurrage Not Calculated)")
    print("--------------------------------------------------------------------------------")
    res_no_free = calculate_port_charges(quantity_mt=50000, total_storage_days=10, free_storage_days=None, selected_services=["demurrage"])
    assert len(res_no_free["calculated_charges"]) == 0
    assert len(res_no_free["uncalculated_notices"]) == 1
    assert res_no_free["is_complete_port_total"] is False
    print(f"  Notice returned for missing free period: {res_no_free['uncalculated_notices'][0]['reason']}")
    print("[PASS] Test 4 passed successfully!")

    # 5. Test Storage Free Period & Chargeable Demurrage Days Calculation
    print("\n--------------------------------------------------------------------------------")
    print("TEST 5: Storage Free Period & Chargeable Days (10 Total Days - 3 Free Days = 7 Chargeable Days)")
    print("--------------------------------------------------------------------------------")
    res_storage = calculate_port_charges(
        quantity_mt=10000,
        total_storage_days=10,
        free_storage_days=3,
        selected_services=["demurrage"]
    )
    assert len(res_storage["calculated_charges"]) == 1
    amount_storage = res_storage["calculated_charges"][0]["charge_amount"]
    # 7 chargeable days @ Rs.4.77/MT/day for 10,000 MT = 333,900 INR
    assert amount_storage == round(10000 * 7 * 4.77, 2)
    print(f"  Chargeable storage demurrage amount: Rs.{amount_storage:,.2f} INR")
    print("[PASS] Test 5 passed successfully!")

    # 6. Test Wharfage Annual Throughput Slab Boundaries (Coal Foreign)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 6: Wharfage Annual Throughput Slab Boundaries (Coal Foreign)")
    print("--------------------------------------------------------------------------------")
    # Boundary 1: 500,000 MT/annum -> Slab 1 (Rs. 60.43/MT)
    r500k = calculate_port_charges(quantity_mt=50000, user_annual_throughput_mt=500000, selected_services=["wharfage"])["calculated_charges"][0]["rate"]
    assert r500k == 60.43

    # Boundary 2: 500,001 MT/annum -> Slab 2 (Rs. 50.86/MT)
    r500k_1 = calculate_port_charges(quantity_mt=50000, user_annual_throughput_mt=500001, selected_services=["wharfage"])["calculated_charges"][0]["rate"]
    assert r500k_1 == 50.86

    # Boundary 3: 750,000 MT/annum -> Slab 2 (Rs. 50.86/MT)
    r750k = calculate_port_charges(quantity_mt=50000, user_annual_throughput_mt=750000, selected_services=["wharfage"])["calculated_charges"][0]["rate"]
    assert r750k == 50.86

    # Boundary 4: 750,001 MT/annum -> Slab 3 (Rs. 41.32/MT)
    r750k_1 = calculate_port_charges(quantity_mt=50000, user_annual_throughput_mt=750001, selected_services=["wharfage"])["calculated_charges"][0]["rate"]
    assert r750k_1 == 41.32

    print(f"  Wharfage Rate at 500,000 MT/yr : Rs.{r500k}/MT (Slab 1)")
    print(f"  Wharfage Rate at 500,001 MT/yr : Rs.{r500k_1}/MT (Slab 2)")
    print(f"  Wharfage Rate at 750,000 MT/yr : Rs.{r750k}/MT (Slab 2)")
    print(f"  Wharfage Rate at 750,001 MT/yr : Rs.{r750k_1}/MT (Slab 3)")
    print("[PASS] Test 6 passed successfully!")

    # 7. Test Inapplicable Services Exclusion (MCHP Handling for Iron Ore)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 7: Inapplicable Services Exclusion (MCHP Handling for Iron Ore)")
    print("--------------------------------------------------------------------------------")
    res_excl = calculate_port_charges(
        quantity_mt=50000,
        commodity="Iron Ore",
        user_annual_throughput_mt=400000,
        selected_services=["mchp_unloading", "mchp_shipment", "wharfage"]
    )
    assert len(res_excl["calculated_charges"]) == 1
    assert len(res_excl["excluded_charges"]) == 2
    print("Excluded Charges Notices:")
    for ex in res_excl["excluded_charges"]:
        print(f"  Excluded {ex['service_key']}: {ex['reason']}")
    print("[PASS] Test 7 passed successfully!")

    # 8. Test Distinction Between Selected Services Total & Complete Port Estimate
    print("\n--------------------------------------------------------------------------------")
    print("TEST 8: Distinction Between Selected Services Total & Complete Port Estimate")
    print("--------------------------------------------------------------------------------")
    res_dist = calculate_port_charges(
        quantity_mt=50000,
        user_annual_throughput_mt=400000,
        selected_services=["wharfage"]
    )
    assert res_dist["selected_services_total_inr"] > 0
    assert res_dist["complete_port_cost_estimate_inr"] is None
    assert res_dist["is_complete_port_total"] is False
    print(f"  Selected Services Total INR : Rs.{res_dist['selected_services_total_inr']:,.2f} INR")
    print(f"  Complete Port Cost Estimate : {res_dist['complete_port_cost_estimate_inr']} (False due to missing vessel/demurrage inputs)")
    print("[PASS] Test 8 passed successfully!")

    # 9. Test Determinism
    print("\n--------------------------------------------------------------------------------")
    print("TEST 9: Determinism Check")
    print("--------------------------------------------------------------------------------")
    res_a = calculate_port_charges(quantity_mt=50000, commodity="Coal/Coke", user_annual_throughput_mt=400000)
    res_b = calculate_port_charges(quantity_mt=50000, commodity="Coal/Coke", user_annual_throughput_mt=400000)
    assert res_a == res_b
    print("  Two consecutive calls produced identical result dicts.")
    print("[PASS] Test 9 passed successfully!")

    print("\n" + "=" * 80)
    print("ALL UNIT TESTS PASSED SUCCESSFULLY (9/9 PASS)!")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
