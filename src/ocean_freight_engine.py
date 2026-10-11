from pathlib import Path
import math
import pandas as pd

# Import reusable transit-time engine functions
from transit_time_engine import (
    load_route_vessel_specs,
    get_available_routes,
    get_available_vessels_for_route,
    calculate_transit_time
)

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATASET_PATH = BASE_DIR / "data" / "processed" / "route_market_dataset.parquet"


def calculate_ocean_freight(
    origin,
    destination,
    vessel_type,
    quantity_mt,
    usd_per_mt=None,
    charter_usd_per_day=None,
    bunker_fuel_price_usd_per_mt=None,
    extra_charter_days=0.0,
    requested_delivery_days=None,
    port_allowance_days=4.0,
    delay_margin_pct=0.0,
    dispatch_mode="parallel",
    usd_to_inr_rate=None,
    exchange_rate_date=None,
    specs_df=None
):
    """
    Calculate ocean freight cost using transparent, user-supplied monetary rates (USD/MT or USD/day),
    reusing route and vessel parameters from the transit-time engine.
    
    IMPORTANT: BDI index points in route_market_dataset.parquet are macroeconomic indicators,
    NOT monetary rates. BDI points will NEVER be treated as USD/MT or USD/day.
    
    Args:
        origin (str): Origin port name.
        destination (str): Destination port name.
        vessel_type (str): Vessel type (e.g. Panamax, Capesize, Supramax).
        quantity_mt (float/int): Cargo quantity in metric tonnes (> 0).
        usd_per_mt (float, optional): User-supplied ocean freight rate in USD per MT (> 0).
        charter_usd_per_day (float, optional): User-supplied daily time-charter rate in USD per day (> 0).
        bunker_fuel_price_usd_per_mt (float, optional): Optional bunker fuel price in USD/MT for charter method.
        extra_charter_days (float, optional): Additional billable charter days (e.g. ballast leg, port waiting).
        requested_delivery_days (float, optional): User's target delivery duration in days.
        port_allowance_days (float, optional): Configurable port operation allowance days.
        delay_margin_pct (float, optional): Configurable sea delay margin percentage.
        dispatch_mode (str, optional): 'parallel' or 'sequential' dispatch mode for transit calculations.
        usd_to_inr_rate (float, optional): Explicit USD-to-INR exchange rate.
        exchange_rate_date (str, optional): Date of supplied exchange rate.
        specs_df (pd.DataFrame, optional): Pre-loaded route/vessel specs DataFrame.
        
    Returns:
        dict: Detailed ocean freight cost breakdown, pricing method, itemized costs, and provenance.
    """
    # 1. Validate quantity and numerical inputs
    if quantity_mt is None or not isinstance(quantity_mt, (int, float)) or math.isnan(quantity_mt):
        raise ValueError("Cargo quantity must be a valid numeric value.")
        
    if quantity_mt <= 0:
        raise ValueError(f"Cargo quantity must be a positive number (> 0 MT). Provided: {quantity_mt}")
        
    if extra_charter_days is None or not isinstance(extra_charter_days, (int, float)) or math.isnan(extra_charter_days) or extra_charter_days < 0:
        raise ValueError(f"Extra charter days must be a non-negative number (>= 0 days). Provided: {extra_charter_days}")

    if usd_per_mt is not None:
        if not isinstance(usd_per_mt, (int, float)) or math.isnan(usd_per_mt) or usd_per_mt <= 0:
            raise ValueError(f"USD/MT freight rate must be a positive number (> 0). Provided: {usd_per_mt}")

    if charter_usd_per_day is not None:
        if not isinstance(charter_usd_per_day, (int, float)) or math.isnan(charter_usd_per_day) or charter_usd_per_day <= 0:
            raise ValueError(f"Charter USD/day rate must be a positive number (> 0). Provided: {charter_usd_per_day}")

    if bunker_fuel_price_usd_per_mt is not None:
        if not isinstance(bunker_fuel_price_usd_per_mt, (int, float)) or math.isnan(bunker_fuel_price_usd_per_mt) or bunker_fuel_price_usd_per_mt <= 0:
            raise ValueError(f"Bunker fuel price must be a positive number (> 0 USD/MT). Provided: {bunker_fuel_price_usd_per_mt}")

    if usd_to_inr_rate is not None:
        if not isinstance(usd_to_inr_rate, (int, float)) or math.isnan(usd_to_inr_rate) or usd_to_inr_rate <= 0:
            raise ValueError(f"USD to INR exchange rate must be a positive number (> 0). Provided: {usd_to_inr_rate}")

    # 2. Reuse transit-time engine to retrieve route specifications & voyage duration
    transit_info = calculate_transit_time(
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

    canonical_origin = transit_info["origin"]
    canonical_dest = transit_info["destination"]
    canonical_vessel = transit_info["vessel_type"]
    distance_nm = transit_info["distance_nm"]
    speed_knots = transit_info["speed_knots"]
    fuel_mt_day = transit_info["fuel_consumption_mt_day"]
    sailing_days = transit_info["adjusted_sailing_days"]
    single_voyage_days = transit_info["min_feasible_delivery_days"]
    loads_required = transit_info["loads_required"]

    # 3. Determine pricing estimation method
    pricing_method = "unavailable"
    estimate_available = False
    rate_value = None
    rate_unit = None
    billable_duration_days = None
    
    itemized_costs = []
    total_usd = None
    total_inr = 0.0
    converted_total_inr = None
    status_explanation = ""
    provenance = ""
    assumptions = []
    missing_inputs = []

    # METHOD A: USD per MT rate supplied
    if usd_per_mt is not None:
        pricing_method = "usd_per_mt"
        estimate_available = True
        rate_value = float(usd_per_mt)
        rate_unit = "USD/MT"
        
        base_freight_usd = round(quantity_mt * rate_value, 2)
        total_usd = base_freight_usd
        
        itemized_costs.append({
            "component": "Ocean Freight (Per MT)",
            "rate": rate_value,
            "unit": "USD/MT",
            "basis": f"{quantity_mt:,.2f} MT",
            "amount_usd": base_freight_usd,
            "formula": f"{quantity_mt:,.2f} MT * ${rate_value:,.2f}/MT"
        })
        
        provenance = "User-supplied monetary freight rate (USD/MT)."
        status_explanation = f"Ocean freight calculated via USD/MT rate (${rate_value:,.2f}/MT)."
        assumptions.append(f"Freight cost calculated at user-supplied rate of ${rate_value:,.2f}/MT across {quantity_mt:,.2f} MT cargo.")

    # METHOD B: Charter USD per day rate supplied
    elif charter_usd_per_day is not None:
        pricing_method = "usd_per_day"
        estimate_available = True
        rate_value = float(charter_usd_per_day)
        rate_unit = "USD/day"
        
        # Calculate billable charter duration
        base_voyage_days = single_voyage_days
        billable_duration_days = round(base_voyage_days + float(extra_charter_days), 2)
        
        charter_base_cost = round(rate_value * billable_duration_days, 2)
        itemized_costs.append({
            "component": "Vessel Time Charter",
            "rate": rate_value,
            "unit": "USD/day",
            "basis": f"{billable_duration_days:.2f} Days ({base_voyage_days:.2f}d voyage + {extra_charter_days:.2f}d extra)",
            "amount_usd": charter_base_cost,
            "formula": f"{billable_duration_days:.2f} Days * ${rate_value:,.2f}/day"
        })
        
        calc_total_usd = charter_base_cost
        
        # Optional fuel cost itemization
        if bunker_fuel_price_usd_per_mt is not None:
            total_fuel_mt = round(fuel_mt_day * sailing_days, 2)
            bunker_fuel_cost = round(total_fuel_mt * bunker_fuel_price_usd_per_mt, 2)
            calc_total_usd += bunker_fuel_cost
            itemized_costs.append({
                "component": "Bunker Fuel Expense",
                "rate": float(bunker_fuel_price_usd_per_mt),
                "unit": "USD/MT Fuel",
                "basis": f"{total_fuel_mt:.2f} MT Fuel ({fuel_mt_day} MT/day * {sailing_days:.2f} sailing days)",
                "amount_usd": bunker_fuel_cost,
                "formula": f"{total_fuel_mt:.2f} MT Fuel * ${bunker_fuel_price_usd_per_mt:,.2f}/MT"
            })
            assumptions.append(f"Bunker fuel cost calculated for {total_fuel_mt:.2f} MT fuel at ${bunker_fuel_price_usd_per_mt:,.2f}/MT.")
        else:
            missing_inputs.append("bunker_fuel_price_usd_per_mt (Optional bunker fuel price for charter model)")
            
        total_usd = round(calc_total_usd, 2)
        provenance = "User-supplied daily time-charter rate (USD/day) and transit-time engine voyage duration."
        status_explanation = f"Ocean freight calculated via time-charter rate (${rate_value:,.2f}/day) over {billable_duration_days:.2f} billable charter days."
        assumptions.append(f"Charter cost calculated at ${rate_value:,.2f}/day over {billable_duration_days:.2f} charter days ({canonical_vessel}).")

    # METHOD C: Unavailable / Fallback (No monetary rate supplied)
    else:
        pricing_method = "unavailable"
        estimate_available = False
        status_explanation = (
            "ESTIMATE UNAVAILABLE: No monetary ocean freight rate supplied. "
            "Note: The Freight_Rate column in route_market_dataset.parquet represents Baltic Dry Index (BDI) points, "
            "which are macroeconomic market indicators, NOT monetary prices in USD/MT or USD/day. "
            "To calculate monetary ocean freight costs, supply an explicit usd_per_mt or charter_usd_per_day rate."
        )
        provenance = "Dataset BDI market indicator reference (No monetary rate supplied)."
        missing_inputs.append("usd_per_mt OR charter_usd_per_day (Required for monetary ocean freight calculation)")

    # 4. Optional Currency Conversion if exchange rate supplied
    if estimate_available and total_usd is not None:
        if usd_to_inr_rate is not None:
            converted_total_inr = round(total_usd * usd_to_inr_rate, 2)

    return {
        "origin": canonical_origin,
        "destination": canonical_dest,
        "vessel_type": canonical_vessel,
        "quantity_mt": float(quantity_mt),
        "typical_cargo_mt": transit_info["typical_cargo_mt"],
        "distance_nm": distance_nm,
        "speed_knots": speed_knots,
        "pricing_method": pricing_method,
        "estimate_available": estimate_available,
        "rate_value": rate_value,
        "rate_unit": rate_unit,
        "billable_duration_days": billable_duration_days,
        "sailing_days": sailing_days,
        "total_voyage_days": single_voyage_days,
        "loads_required": loads_required,
        "itemized_costs": itemized_costs,
        "total_usd": total_usd,
        "total_inr": total_inr,
        "converted_total_inr": converted_total_inr,
        "usd_to_inr_rate_used": usd_to_inr_rate,
        "exchange_rate_date": exchange_rate_date,
        "status_explanation": status_explanation,
        "provenance": provenance,
        "assumptions": assumptions,
        "missing_inputs": missing_inputs,
        "disclaimer": (
            "NOTICE: Ocean freight cost represents voyage/charter transportation expenses ONLY. "
            "It DOES NOT include commodity purchase price, port tariffs, or demurrage fees."
        )
    }
