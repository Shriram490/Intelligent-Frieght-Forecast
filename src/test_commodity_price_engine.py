import sys
from pathlib import Path

# Add src directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from commodity_price_engine import (
    load_commodity_prices,
    get_supported_commodities,
    search_commodity,
    get_latest_commodity_price,
    calculate_commodity_value
)


def run_tests():
    print("=" * 80)
    print("COMMODITY PRICE ENGINE UNIT TEST SUITE")
    print("=" * 80)

    # Load dataset once
    df = load_commodity_prices()
    print(f"\n[PASS] Loaded commodity prices dataset successfully ({len(df)} records).")

    # 1. Test get_supported_commodities
    commodities = get_supported_commodities(df)
    print(f"[PASS] Found {len(commodities)} unique supported commodities.")
    assert len(commodities) > 0
    assert "Coal, Australian" in commodities
    assert "Aluminum" in commodities

    # 2. Test search_commodity
    print("\n--------------------------------------------------------------------------------")
    print("TEST 2: Commodity Search (Exact & Partial Query Matching)")
    print("--------------------------------------------------------------------------------")
    matches_coal = search_commodity("Coal", df)
    print(f"  Search query 'Coal' matched: {matches_coal}")
    assert len(matches_coal) >= 2
    assert "Coal, Australian" in matches_coal
    assert "Coal, South African **" in matches_coal

    matches_alum = search_commodity("Aluminum", df)
    assert matches_alum == ["Aluminum"]
    print("[PASS] Test 2 passed successfully!")

    # 3. Test get_latest_commodity_price for valid commodity
    print("\n--------------------------------------------------------------------------------")
    print("TEST 3: Latest Price & Unit Metadata Retrieval (Coal, Australian)")
    print("--------------------------------------------------------------------------------")
    latest_coal = get_latest_commodity_price("Coal, Australian", df)
    assert latest_coal["commodity"] == "Coal, Australian"
    assert latest_coal["recorded_unit"] == "USD/mt"
    assert latest_coal["supports_mt_calculation"] is True
    assert latest_coal["latest_price"] > 0
    assert latest_coal["date"] == "2025-12-01"
    print("Result:")
    for k, v in latest_coal.items():
        print(f"  {k:<30}: {v}")
    print("[PASS] Test 3 passed successfully!")

    # 4. Test invalid commodity name & ambiguous name errors
    print("\n--------------------------------------------------------------------------------")
    print("TEST 4: Invalid & Ambiguous Commodity Name Error Handling")
    print("--------------------------------------------------------------------------------")
    try:
        get_latest_commodity_price("Unobtanium", df)
        assert False, "Should have raised ValueError for non-existent commodity."
    except ValueError as e:
        print(f"  Caught expected error for invalid name: {e}")

    try:
        get_latest_commodity_price("Coal", df)
        assert False, "Should have raised ValueError for ambiguous commodity name."
    except ValueError as e:
        assert "Ambiguous commodity search" in str(e)
        print(f"  Caught expected error for ambiguous name: {e}")
    print("[PASS] Test 4 passed successfully!")

    # 5. Test invalid quantity validation (0, negative, None)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 5: Invalid Quantity Validation (<= 0, None)")
    print("--------------------------------------------------------------------------------")
    for invalid_qty in [0, -100, None]:
        try:
            calculate_commodity_value("Coal, Australian", invalid_qty, df)
            assert False, f"Should have raised ValueError for quantity={invalid_qty}"
        except ValueError as e:
            print(f"  Caught expected error for quantity={invalid_qty}: {e}")
    print("[PASS] Test 5 passed successfully!")

    # 6. Test unit-aware calculation for USD/mt commodity (Coal, Australian)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 6: Purchase Value Calculation for USD/mt Commodity (50,000 MT Coal, Australian)")
    print("--------------------------------------------------------------------------------")
    val_coal = calculate_commodity_value("Coal, Australian", 50000, df)
    assert val_coal["value_calculated"] is True
    assert val_coal["recorded_unit"] == "USD/mt"
    assert val_coal["estimated_purchase_value_usd"] == round(50000 * val_coal["price_per_mt_usd"], 2)
    print(f"  Commodity                   : {val_coal['commodity']}")
    print(f"  Quantity MT                 : {val_coal['quantity_mt']:,.2f}")
    print(f"  Price Date                  : {val_coal['price_date']}")
    print(f"  Price / MT (USD)            : ${val_coal['price_per_mt_usd']:,.2f}")
    print(f"  Estimated Purchase Value USD: ${val_coal['estimated_purchase_value_usd']:,.2f}")
    print(f"  Notes                       : {val_coal['calculation_notes']}")
    print("[PASS] Test 6 passed successfully!")

    # 7. Test unit-aware calculation for USD/kg commodity (Cocoa)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 7: Purchase Value Calculation for USD/kg Commodity (100 MT Cocoa)")
    print("--------------------------------------------------------------------------------")
    val_cocoa = calculate_commodity_value("Cocoa", 100, df)
    assert val_cocoa["value_calculated"] is True
    assert val_cocoa["recorded_unit"] == "USD/kg"
    assert val_cocoa["price_per_mt_usd"] == round(val_cocoa["latest_price"] * 1000.0, 2)
    print(f"  Latest Price per KG         : ${val_cocoa['latest_price']:,.4f}/kg")
    print(f"  Converted Price per MT      : ${val_cocoa['price_per_mt_usd']:,.2f}/MT")
    print(f"  Estimated Purchase Value USD: ${val_cocoa['estimated_purchase_value_usd']:,.2f}")
    print("[PASS] Test 7 passed successfully!")

    # 8. Test incompatible unit commodity (Crude oil, Brent in USD/bbl & Iron ore in USD/dmtu)
    print("\n--------------------------------------------------------------------------------")
    print("TEST 8: Incompatible Unit Handling (Crude oil, Brent in USD/bbl & Iron ore in USD/dmtu)")
    print("--------------------------------------------------------------------------------")
    val_brent = calculate_commodity_value("Crude oil, Brent", 1000, df)
    assert val_brent["value_calculated"] is False
    assert val_brent["estimated_purchase_value_usd"] is None
    assert "UNSUPPORTED UNIT" in val_brent["calculation_notes"]
    print(f"  Crude oil, Brent Calculation Result:")
    print(f"    Recorded Unit   : {val_brent['recorded_unit']}")
    print(f"    Value Calculated: {val_brent['value_calculated']}")
    print(f"    Notes           : {val_brent['calculation_notes']}")

    val_iron = calculate_commodity_value("Iron ore, cfr spot", 100000, df)
    assert val_iron["value_calculated"] is False
    assert val_iron["estimated_purchase_value_usd"] is None
    print(f"  Iron ore, cfr spot Calculation Result:")
    print(f"    Recorded Unit   : {val_iron['recorded_unit']}")
    print(f"    Value Calculated: {val_iron['value_calculated']}")
    print(f"    Notes           : {val_iron['calculation_notes']}")
    print("[PASS] Test 8 passed successfully!")

    # 9. Test determinism
    print("\n--------------------------------------------------------------------------------")
    print("TEST 9: Determinism Check")
    print("--------------------------------------------------------------------------------")
    res_a = calculate_commodity_value("Coal, Australian", 50000, df)
    res_b = calculate_commodity_value("Coal, Australian", 50000, df)
    assert res_a == res_b
    print("  Two consecutive calls produced identical result dicts.")
    print("[PASS] Test 9 passed successfully!")

    print("\n" + "=" * 80)
    print("ALL UNIT TESTS PASSED SUCCESSFULLY (9/9 PASS)!")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
