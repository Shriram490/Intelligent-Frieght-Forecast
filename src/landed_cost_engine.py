from pathlib import Path
import math

import pandas as pd

# Import reusable engine modules
from transit_time_engine import calculate_transit_time
from commodity_price_engine import calculate_commodity_value
from ocean_freight_engine import calculate_ocean_freight
from port_charges_engine import calculate_port_charges

BASE_DIR = Path(__file__).resolve().parent.parent


def calculate_landed_cost(
    commodity,
    quantity_mt,
    origin,
    destination,
    vessel_type,
    traffic_type="Foreign",
    planned_shipment_date=None,
    user_annual_throughput_mt=None,
    requested_delivery_days=None,
    port_allowance_days=4.0,
    delay_margin_pct=0.0,
    dispatch_mode="parallel",
    usd_per_mt=None,
    charter_usd_per_day=None,
    bunker_fuel_price_usd_per_mt=None,
    extra_charter_days=0.0,
    vessel_gt=None,
    port_stay_hours=None,
    total_storage_days=None,
    free_storage_days=None,
    usd_to_inr_rate=None,
    exchange_rate_date=None,
    custom_inland_transport_usd=0.0,
    custom_insurance_usd=0.0,
    selected_port_services=None,
    specs_df=None,
    commodity_df=None,
    port_dir=None
):
    """
    Calculate integrated landed cost by coordinating the transit-time, commodity-price,
    ocean-freight, and port-charges engines.
    
    Args:
        commodity (str): Selected commodity name.
        quantity_mt (float/int): Cargo quantity in metric tonnes (> 0).
        origin (str): Origin port name.
        destination (str): Destination port name.
        vessel_type (str): Vessel class (e.g., Panamax, Capesize, Supramax).
        traffic_type (str, optional): 'Foreign' or 'Coastal' traffic classification.
        planned_shipment_date (str/datetime, optional): Target shipment date.
        user_annual_throughput_mt (float, optional): User's total annual volume per commodity for wharfage slab selection.
        requested_delivery_days (float, optional): User's target delivery duration in days.
        port_allowance_days (float, optional): Configurable port operation allowance days.
        delay_margin_pct (float, optional): Configurable sea delay margin percentage.
        dispatch_mode (str, optional): Multi-load dispatch mode ('parallel' or 'sequential').
        usd_per_mt (float, optional): User-supplied freight rate in USD/MT.
        charter_usd_per_day (float, optional): User-supplied daily charter rate in USD/day.
        bunker_fuel_price_usd_per_mt (float, optional): Optional bunker fuel price in USD/MT.
        extra_charter_days (float, optional): Additional billable charter days.
        vessel_gt (float, optional): Vessel Gross Tonnage for berth hire calculation.
        port_stay_hours (float, optional): Total port stay duration in hours for berth hire.
        total_storage_days (float, optional): Total cargo storage days in port transit area.
        free_storage_days (float, optional): Free storage days allowed before demurrage.
        usd_to_inr_rate (float, optional): Explicit USD-to-INR exchange rate for unified conversion.
        exchange_rate_date (str, optional): Date of supplied exchange rate.
        custom_inland_transport_usd (float, optional): Custom inland transport expense in USD.
        custom_insurance_usd (float, optional): Custom cargo insurance expense in USD.
        selected_port_services (list, optional): List of port service keys to calculate.
        specs_df (pd.DataFrame, optional): Pre-loaded route/vessel specs DataFrame.
        commodity_df (pd.DataFrame, optional): Pre-loaded commodity prices DataFrame.
        port_dir (Path/str, optional): Custom path to port tariff Parquet directory.
        
    Returns:
        dict: Detailed integrated landed cost breakdown, component totals, transit feasibility,
              missing components, and strict completeness status.
    """
    # 1. Validate quantity and custom cost inputs
    if quantity_mt is None or not isinstance(quantity_mt, (int, float)) or math.isnan(quantity_mt):
        raise ValueError("Cargo quantity must be a valid numeric value.")
        
    if quantity_mt <= 0:
        raise ValueError(f"Cargo quantity must be a positive number (> 0 MT). Provided: {quantity_mt}")

    if custom_inland_transport_usd is None or not isinstance(custom_inland_transport_usd, (int, float)) or math.isnan(custom_inland_transport_usd) or custom_inland_transport_usd < 0:
        raise ValueError(f"Custom inland transport expense must be a non-negative number. Provided: {custom_inland_transport_usd}")

    if custom_insurance_usd is None or not isinstance(custom_insurance_usd, (int, float)) or math.isnan(custom_insurance_usd) or custom_insurance_usd < 0:
        raise ValueError(f"Custom insurance expense must be a non-negative number. Provided: {custom_insurance_usd}")

    # 2. Call Engine 1: Transit Time Engine
    transit_result = calculate_transit_time(
        origin=origin,
        destination=destination,
        vessel_type=vessel_type,
        quantity_mt=quantity_mt,
        requested_delivery_days=requested_delivery_days,
        port_allowance_days=port_allowance_days,
        delay_margin_pct=delay_margin_pct,
        dispatch_mode=dispatch_mode,
        specs_df=specs_df
    )

    # 3. Call Engine 2: Commodity Price Engine
    commodity_result = calculate_commodity_value(
        commodity_name=commodity,
        quantity_mt=quantity_mt,
        df=commodity_df
    )

    # 4. Call Engine 3: Ocean Freight Engine
    ocean_freight_result = calculate_ocean_freight(
        origin=origin,
        destination=destination,
        vessel_type=vessel_type,
        quantity_mt=quantity_mt,
        usd_per_mt=usd_per_mt,
        charter_usd_per_day=charter_usd_per_day,
        bunker_fuel_price_usd_per_mt=bunker_fuel_price_usd_per_mt,
        extra_charter_days=extra_charter_days,
        requested_delivery_days=requested_delivery_days,
        port_allowance_days=port_allowance_days,
        delay_margin_pct=delay_margin_pct,
        dispatch_mode=dispatch_mode,
        usd_to_inr_rate=usd_to_inr_rate,
        exchange_rate_date=exchange_rate_date,
        specs_df=specs_df
    )

    # 5. Call Engine 4: Port Charges Engine
    port_charges_result = calculate_port_charges(
        quantity_mt=quantity_mt,
        commodity=commodity,
        traffic_type=traffic_type,
        user_annual_throughput_mt=user_annual_throughput_mt,
        planned_shipment_date=planned_shipment_date,
        vessel_gt=vessel_gt,
        port_stay_hours=port_stay_hours,
        total_storage_days=total_storage_days,
        free_storage_days=free_storage_days,
        usd_to_inr_rate=usd_to_inr_rate,
        exchange_rate_date=exchange_rate_date,
        selected_services=selected_port_services,
        processed_dir=port_dir
    )

    # 6. Extract component values
    commodity_value_usd = commodity_result["estimated_purchase_value_usd"]
    is_commodity_available = commodity_result["value_calculated"]

    ocean_freight_usd = ocean_freight_result["total_usd"]
    is_ocean_freight_available = ocean_freight_result["estimate_available"]
    ocean_freight_provenance = ocean_freight_result["provenance"]
    ocean_freight_pricing_method = ocean_freight_result["pricing_method"]

    port_inr = port_charges_result["selected_services_total_inr"]
    port_usd = port_charges_result["selected_services_total_usd"]
    is_port_complete = port_charges_result["is_complete_port_total"]
    is_port_selected_complete = port_charges_result["is_complete_selected_services"]
    port_uncalculated_notices = port_charges_result["uncalculated_notices"]
    port_excluded_charges = port_charges_result["excluded_charges"]
    port_requires_verification = port_charges_result["requires_verification"]

    inland_transport_usd = round(float(custom_inland_transport_usd), 2)
    insurance_usd = round(float(custom_insurance_usd), 2)

    # 7. Check completeness flags and missing components
    missing_components = []
    
    if not is_commodity_available:
        missing_components.append(f"Benchmark Commodity Value ({commodity_result['calculation_notes']})")

    if not is_ocean_freight_available:
        missing_components.append("Ocean Freight Cost (No monetary rate in USD/MT or USD/day supplied)")

    if not is_port_selected_complete or port_uncalculated_notices:
        if port_uncalculated_notices:
            reasons = "; ".join(n["reason"] for n in port_uncalculated_notices)
            missing_components.append(f"Port Charges Incomplete ({reasons})")
        elif port_requires_verification:
            issues = "; ".join(v["issue"] for v in port_requires_verification)
            missing_components.append(f"Port Charges Unverified ({issues})")

    if usd_to_inr_rate is None:
        missing_components.append("USD/INR Exchange Rate (Required to convert port charges INR into USD landed cost)")

    # Distinguish Completeness Concepts:
    # 1. is_complete_within_scope: True iff all selected components within the declared scope were successfully computed with explicit inputs
    is_complete_within_scope = (
        is_commodity_available and
        is_ocean_freight_available and
        is_port_selected_complete and
        (usd_to_inr_rate is not None)
    )

    # 2. is_all_in_cost_known: True ONLY IF all potential commercial cost categories (full port tariff, customs, inland, insurance) are completely verified
    is_all_in_cost_known = (
        is_complete_within_scope and
        is_port_complete and
        (inland_transport_usd > 0) and
        (insurance_usd > 0)
    )

    # Backward compatibility flag
    is_complete_estimate = is_complete_within_scope

    # 8. Calculate partial and complete landed cost totals
    # Sum available USD components
    available_usd_sum = 0.0
    if is_commodity_available and commodity_value_usd is not None:
        available_usd_sum += commodity_value_usd
    if is_ocean_freight_available and ocean_freight_usd is not None:
        available_usd_sum += ocean_freight_usd
    available_usd_sum += port_usd + inland_transport_usd + insurance_usd
    available_usd_sum = round(available_usd_sum, 2)

    available_inr_sum = round(port_inr, 2)

    partial_landed_cost_usd = available_usd_sum
    if usd_to_inr_rate is not None:
        partial_landed_cost_usd = round(available_usd_sum + (available_inr_sum / usd_to_inr_rate), 2)

    complete_landed_cost_usd = partial_landed_cost_usd if is_complete_within_scope else None
    complete_landed_cost_inr = round(partial_landed_cost_usd * usd_to_inr_rate, 2) if (is_complete_within_scope and usd_to_inr_rate is not None) else None

    # Calculate Per-MT cost metrics independently
    landed_cost_per_mt_usd = round(complete_landed_cost_usd / quantity_mt, 2) if complete_landed_cost_usd is not None else None

    # 9. Formulate summary & disclaimer
    scope_included = [
        f"Benchmark FOB Commodity Value (${commodity_value_usd:,.2f} USD)" if is_commodity_available else "Benchmark Commodity Value (UNAVAILABLE)",
        f"Ocean Freight Transport (${ocean_freight_usd:,.2f} USD via {ocean_freight_pricing_method})" if is_ocean_freight_available else "Ocean Freight (UNAVAILABLE)",
        f"Selected Port Charges (Rs.{port_inr:,.2f} INR + ${port_usd:,.2f} USD)",
    ]
    if inland_transport_usd > 0:
        scope_included.append(f"Custom Inland Transport (${inland_transport_usd:,.2f} USD)")
    if insurance_usd > 0:
        scope_included.append(f"Custom Marine Insurance (${insurance_usd:,.2f} USD)")

    scope_excluded = [
        "Unspecified import customs duties & national taxes",
        "Unrequested specialized port operations (e.g. SBM, STS, transloading)",
        "Uncalculated demurrage beyond free storage period" if total_storage_days is None else "Vessel charter demurrage"
    ]
    if inland_transport_usd == 0:
        scope_excluded.append("Inland transport beyond destination port")
    if insurance_usd == 0:
        scope_excluded.append("Marine cargo insurance")

    return {
        "commodity": commodity,
        "quantity_mt": float(quantity_mt),
        "origin": transit_result["origin"],
        "destination": transit_result["destination"],
        "vessel_type": transit_result["vessel_type"],
        "traffic_type": port_charges_result["traffic_type"],
        "planned_shipment_date": planned_shipment_date,
        "is_transit_feasible": transit_result["is_feasible"],
        "transit_time_summary": {
            "sailing_days": transit_result["adjusted_sailing_days"],
            "port_allowance_days": transit_result["port_allowance_days"],
            "min_feasible_delivery_days": transit_result["min_feasible_delivery_days"],
            "requested_delivery_days": requested_delivery_days,
            "loads_required": transit_result["loads_required"],
            "status_explanation": transit_result["delivery_status_explanation"]
        },
        "commodity_value_usd": commodity_value_usd,
        "is_commodity_value_available": is_commodity_available,
        "ocean_freight_cost_usd": ocean_freight_usd,
        "is_ocean_freight_available": is_ocean_freight_available,
        "ocean_freight_pricing_method": ocean_freight_pricing_method,
        "ocean_freight_provenance": ocean_freight_provenance,
        "port_charges_selected_services_total_inr": port_inr,
        "port_charges_selected_services_total_usd": port_usd,
        "is_port_charges_complete": is_port_complete,
        "is_port_selected_services_complete": is_port_selected_complete,
        "port_uncalculated_notices": port_uncalculated_notices,
        "port_excluded_charges": port_excluded_charges,
        "port_requires_verification": port_requires_verification,
        "custom_inland_transport_usd": inland_transport_usd,
        "custom_insurance_usd": insurance_usd,
        "usd_to_inr_rate_used": usd_to_inr_rate,
        "exchange_rate_date": exchange_rate_date,
        "partial_landed_cost_usd": partial_landed_cost_usd,
        "partial_landed_cost_inr": round(partial_landed_cost_usd * usd_to_inr_rate, 2) if usd_to_inr_rate is not None else None,
        "landed_cost_estimate_usd": complete_landed_cost_usd,
        "landed_cost_estimate_inr": complete_landed_cost_inr,
        "landed_cost_per_mt_usd": landed_cost_per_mt_usd,
        "is_complete_within_scope": is_complete_within_scope,
        "is_all_in_cost_known": is_all_in_cost_known,
        "is_complete_estimate": is_complete_estimate,
        "missing_components": missing_components,
        "scope_summary": {
            "included": scope_included,
            "excluded": scope_excluded
        },
        "engine_breakdowns": {
            "transit_time": transit_result,
            "commodity_price": commodity_result,
            "ocean_freight": ocean_freight_result,
            "port_charges": port_charges_result
        },
        "disclaimer": (
            "NOTICE: Landed cost calculation is an integrated estimate combining benchmark FOB commodity prices, "
            "monetary ocean freight rates, and rule-based Paradip Port Scale of Rates (2026-27). "
            "It DOES NOT constitute a binding commercial quote."
        )
    }

