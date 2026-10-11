import sys
from pathlib import Path

# Add src directory and project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from landed_cost_engine import calculate_landed_cost
from transit_time_engine import load_route_vessel_specs, get_available_routes
from commodity_price_engine import get_supported_commodities


def test_streamlit_integration_flow():
    """
    Test that the calculation logic called by app.py completes successfully
    with typical UI parameters.
    """
    specs_df = load_route_vessel_specs()
    commodities = get_supported_commodities()
    available_routes = get_available_routes(specs_df)

    assert len(commodities) > 0
    assert len(available_routes) > 0

    # Simulate UI call
    res = calculate_landed_cost(
        commodity="Coal, Australian",
        quantity_mt=50000,
        origin="Newcastle",
        destination="Paradip",
        vessel_type="Panamax",
        traffic_type="Foreign",
        planned_shipment_date="2026-05-01",
        user_annual_throughput_mt=400000,
        requested_delivery_days=25.0,
        port_allowance_days=4.0,
        delay_margin_pct=0.0,
        dispatch_mode="parallel",
        usd_per_mt=25.50,
        vessel_gt=70000,
        port_stay_hours=48,
        usd_to_inr_rate=83.5,
        selected_port_services=["wharfage", "mchp_unloading", "mchp_shipment", "environmental", "stevedoring", "weighment", "railway", "berth_hire"]
    )

    assert res["is_complete_within_scope"] is True
    assert res["landed_cost_estimate_usd"] > 0
    assert res["landed_cost_per_mt_usd"] > 0
    assert res["is_transit_feasible"] is True


def test_ui_invalid_inputs_handling():
    """Test that invalid UI inputs raise expected validation errors."""
    try:
        calculate_landed_cost(
            commodity="Coal, Australian",
            quantity_mt=-100,  # Invalid quantity
            origin="Newcastle",
            destination="Paradip",
            vessel_type="Panamax"
        )
        assert False, "Should have raised ValueError for negative cargo quantity."
    except ValueError as e:
        assert "Cargo quantity must be a positive number" in str(e)


if __name__ == "__main__":
    test_streamlit_integration_flow()
    test_ui_invalid_inputs_handling()
    print("ALL STREAMLIT UI INTEGRATION TESTS PASSED SUCCESSFULLY!")
