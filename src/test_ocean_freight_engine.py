import sys
from pathlib import Path

# Add src directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ocean_freight_engine import calculate_ocean_freight
from transit_time_engine import load_route_vessel_specs, get_available_routes


def run_tests():
    print("=" * 80)
    print("OCEAN FREIGHT ENGINE COMPREHENSIVE UNIT TEST SUITE")
    print("=" * 80)

    specs_df = load_route_vessel_specs()
    print(f"\n[PASS] Loaded route specs dataset successfully ({len(specs_df)} configurations).")

    # 1. Test Valid USD/MT Method
    print("\n--------------------------------------------------------------------------------")
    print("TEST 1: Valid USD/MT Calculation (Newcastle -> Paradip, Panamax, 60,000 MT @ $25.50/MT)")
    print("--------------------------------------------------------------------------------")
    res1 = calculate_ocean_freight(
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        quantity_mt=60000,
        usd_per_mt=25.50,
        specs_df=specs_df
    )
    assert res1["pricing_method"] == "usd_per_mt"
    assert res1["estimate_available"] is True
    assert res1["rate_value"] == 25.50
    assert res1["rate_unit"] == "USD/MT"
    assert res1["total_usd"] == round(60000 * 25.50, 2)
    assert res1["converted_total_inr"] is None
    print(f"  Pricing Method: {res1['pricing_method']}")
    print(f"  Total USD     : ${res1['total_usd']:,.2f} USD")
    print(f"  Formula       : {res1['itemized_costs'][0]['formula']}")
    print("[PASS] Test 1 passed successfully!")

    # 2. Test Valid USD/Day Charter Method with Bunker Fuel
    print("\n--------------------------------------------------------------------------------")
    print("TEST 2: Valid USD/Day Charter Calculation ($15,000/day + $600/MT Bunker Fuel)")
    print("--------------------------------------------------------------------------------")
    res2 = calculate_ocean_freight(
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        quantity_mt=60000,
        charter_usd_per_day=15000,
        bunker_fuel_price_usd_per_mt=600,
        extra_charter_days=2.0,
        specs_df=specs_df
    )
    assert res2["pricing_method"] == "usd_per_day"
    assert res2["estimate_available"] is True
    assert res2["rate_value"] == 15000
    assert len(res2["itemized_costs"]) == 2
    # Billable days = 16.5 + 2.0 = 18.5 days. Charter cost = 18.5 * 15000 = 277,500 USD
    # Fuel MT = 30 MT/day * 12.5 sailing days = 375 MT. Fuel cost = 375 * 600 = 225,000 USD
    assert res2["itemized_costs"][0]["amount_usd"] == round(18.5 * 15000, 2)
    assert res2["itemized_costs"][1]["amount_usd"] == round(375 * 600, 2)
    assert res2["total_usd"] == round(277500 + 225000, 2)
    print(f"  Billable Charter Days: {res2['billable_duration_days']} Days")
    for item in res2["itemized_costs"]:
        print(f"  - {item['component']:<22}: ${item['amount_usd']:>12,.2f} USD ({item['formula']})")
    print(f"  Total Ocean Freight USD: ${res2['total_usd']:,.2f} USD")
    print("[PASS] Test 2 passed successfully!")

    # 3. Test Invalid / Negative Parameters Validation
    print("\n--------------------------------------------------------------------------------")
    print("TEST 3: Invalid Input Parameters Validation (Quantity <= 0, Negative Rates)")
    print("--------------------------------------------------------------------------------")
    invalid_cases = [
        ({"quantity_mt": 0}, "Cargo quantity must be a positive number"),
        ({"quantity_mt": -500}, "Cargo quantity must be a positive number"),
        ({"quantity_mt": 60000, "usd_per_mt": -20}, "USD/MT freight rate must be a positive number"),
        ({"quantity_mt": 60000, "charter_usd_per_day": -5000}, "Charter USD/day rate must be a positive number"),
        ({"quantity_mt": 60000, "bunker_fuel_price_usd_per_mt": -100}, "Bunker fuel price must be a positive number"),
        ({"quantity_mt": 60000, "extra_charter_days": -1}, "Extra charter days must be a non-negative number")
    ]
    for kwargs, err_substr in invalid_cases:
        try:
            calculate_ocean_freight("Newcastle", "Paradip", "Panamax", **kwargs, specs_df=specs_df)
            assert False, f"Should have raised ValueError for invalid kwargs: {kwargs}"
        except ValueError as e:
            assert err_substr in str(e)
            print(f"  Caught expected error for {kwargs}: {e}")
    print("[PASS] Test 3 passed successfully!")

    # 4. Test Unsupported Routes & Vessel Classes
    print("\n--------------------------------------------------------------------------------")
    print("TEST 4: Unsupported Route and Vessel Class Validation")
    print("--------------------------------------------------------------------------------")
    try:
        calculate_ocean_freight("London", "Paradip", "Panamax", 50000, usd_per_mt=30, specs_df=specs_df)
        assert False, "Should have raised ValueError for invalid route."
    except ValueError as e:
        print(f"  Caught expected error for invalid route: {e}")

    try:
        calculate_ocean_freight("Newcastle", "Paradip", "Submarine", 50000, usd_per_mt=30, specs_df=specs_df)
        assert False, "Should have raised ValueError for unsupported vessel."
    except ValueError as e:
        print(f"  Caught expected error for unsupported vessel: {e}")
    print("[PASS] Test 4 passed successfully!")

    # 5. Test Currency Conversion Only When Supplied
    print("\n--------------------------------------------------------------------------------")
    print("TEST 5: Explicit Currency Conversion (Rate = 83.5 INR/USD)")
    print("--------------------------------------------------------------------------------")
    res_conv = calculate_ocean_freight(
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        quantity_mt=60000,
        usd_per_mt=25.50,
        usd_to_inr_rate=83.5,
        specs_df=specs_df
    )
    assert res_conv["total_usd"] == 1530000.0
    assert res_conv["converted_total_inr"] == round(1530000.0 * 83.5, 2)
    print(f"  Total USD             : ${res_conv['total_usd']:,.2f} USD")
    print(f"  Converted Total INR   : Rs.{res_conv['converted_total_inr']:,.2f} INR (@ Rs.83.5/USD)")
    print("[PASS] Test 5 passed successfully!")

    # 6. Test Prevention of BDI Index Points as Monetary Rates & Unavailable Estimate Fallback
    print("\n--------------------------------------------------------------------------------")
    print("TEST 6: Prevention of BDI Index Points Usage & Unavailable Estimate Behavior")
    print("--------------------------------------------------------------------------------")
    res_unavail = calculate_ocean_freight(
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        quantity_mt=60000,
        specs_df=specs_df
    )
    assert res_unavail["pricing_method"] == "unavailable"
    assert res_unavail["estimate_available"] is False
    assert res_unavail["total_usd"] is None
    assert "Baltic Dry Index (BDI) points" in res_unavail["status_explanation"]
    assert "usd_per_mt OR charter_usd_per_day" in res_unavail["missing_inputs"][0]
    print(f"  Pricing Method     : {res_unavail['pricing_method']}")
    print(f"  Estimate Available : {res_unavail['estimate_available']}")
    print(f"  Status Explanation : {res_unavail['status_explanation']}")
    print("[PASS] Test 6 passed successfully!")

    # 7. Test Determinism
    print("\n--------------------------------------------------------------------------------")
    print("TEST 7: Determinism Check")
    print("--------------------------------------------------------------------------------")
    res_a = calculate_ocean_freight("Newcastle", "Paradip", "Panamax", 60000, usd_per_mt=25.50, specs_df=specs_df)
    res_b = calculate_ocean_freight("Newcastle", "Paradip", "Panamax", 60000, usd_per_mt=25.50, specs_df=specs_df)
    assert res_a == res_b
    print("  Two consecutive calls produced identical result dicts.")
    print("[PASS] Test 7 passed successfully!")

    print("\n" + "=" * 80)
    print("ALL UNIT TESTS PASSED SUCCESSFULLY (7/7 PASS)!")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
