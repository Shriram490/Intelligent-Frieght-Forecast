import math
from pathlib import Path
import pandas as pd

# Default dataset location relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATASET_PATH = BASE_DIR / "data" / "processed" / "route_market_dataset.parquet"

# Configurable default port operation assumptions (in days)
DEFAULT_LOADING_ALLOWANCE_DAYS = 2.0
DEFAULT_UNLOADING_ALLOWANCE_DAYS = 2.0
DEFAULT_PORT_ALLOWANCE_DAYS = DEFAULT_LOADING_ALLOWANCE_DAYS + DEFAULT_UNLOADING_ALLOWANCE_DAYS
DEFAULT_DELAY_MARGIN_PCT = 0.0
DEFAULT_DISPATCH_MODE = "parallel"


def load_route_vessel_specs(dataset_path=None):
    """
    Load unique route and vessel specifications from the processed dataset.
    
    Returns:
        pd.DataFrame containing unique route-vessel configurations.
    """
    if dataset_path is None:
        dataset_path = DEFAULT_DATASET_PATH
    
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Route market dataset not found at: {path}")
    
    df = pd.read_parquet(path)
    
    req_cols = [
        "Origin", "Destination", "Vessel_Type",
        "Typical_Distance_NM", "Average_Speed_Knots",
        "Typical_Cargo_MT", "Fuel_Consumption_MT_Day"
    ]
    
    missing_cols = [col for col in req_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset is missing required columns: {missing_cols}")
    
    # Deduplicate specifications per route and vessel type
    specs = df[req_cols].drop_duplicates().reset_index(drop=True)
    return specs


def get_available_routes(specs_df=None):
    """
    Get all available Origin -> Destination route pairs in the dataset.
    
    Returns:
        List of tuples: [(Origin, Destination), ...]
    """
    if specs_df is None:
        specs_df = load_route_vessel_specs()
        
    routes = specs_df[["Origin", "Destination"]].drop_duplicates()
    return list(zip(routes["Origin"], routes["Destination"]))


def get_available_vessels_for_route(origin, destination, specs_df=None):
    """
    Get available vessel types for a specific route.
    
    Returns:
        List of vessel type strings.
    """
    if specs_df is None:
        specs_df = load_route_vessel_specs()
        
    matched = specs_df[
        (specs_df["Origin"].str.lower() == origin.lower()) &
        (specs_df["Destination"].str.lower() == destination.lower())
    ]
    
    if matched.empty:
        available = get_available_routes(specs_df)
        avail_str = ", ".join([f"{o} -> {d}" for o, d in available])
        raise ValueError(
            f"Invalid route: '{origin}' -> '{destination}'. "
            f"Available routes are: {avail_str}"
        )
        
    return list(matched["Vessel_Type"].unique())


def calculate_transit_time(
    origin,
    destination,
    vessel_type,
    quantity_mt,
    requested_delivery_days=None,
    port_allowance_days=DEFAULT_PORT_ALLOWANCE_DAYS,
    delay_margin_pct=DEFAULT_DELAY_MARGIN_PCT,
    dispatch_mode=DEFAULT_DISPATCH_MODE,
    specs_df=None
):
    """
    Calculate pure sailing time, sea delay margin, port operation allowances,
    vessel cargo capacity checks, and total minimum feasible delivery time.
    
    Args:
        origin (str): Origin port name.
        destination (str): Destination port name.
        vessel_type (str): Vessel type (e.g., Panamax, Capesize, Supramax).
        quantity_mt (float/int): Cargo quantity in metric tonnes (> 0).
        requested_delivery_days (float, optional): User's target delivery duration in days (> 0).
        port_allowance_days (float, optional): Configurable allowance for port operations (>= 0).
        delay_margin_pct (float, optional): Configurable sea/operational delay margin percentage (>= 0).
        dispatch_mode (str, optional): Multi-vessel scheduling mode: 'parallel' or 'sequential'.
        specs_df (pd.DataFrame, optional): Pre-loaded route/vessel specs DataFrame.
        
    Returns:
        dict: Detailed transit time calculation breakdown.
    """
    # 1. Validate numerical and string inputs
    if quantity_mt is None or not isinstance(quantity_mt, (int, float)) or math.isnan(quantity_mt):
        raise ValueError("Cargo quantity must be a valid numeric value.")
        
    if quantity_mt <= 0:
        raise ValueError(f"Cargo quantity must be a positive number (> 0 MT). Provided: {quantity_mt}")
        
    if port_allowance_days is None or not isinstance(port_allowance_days, (int, float)) or math.isnan(port_allowance_days):
        raise ValueError("Port allowance days must be a valid numeric value.")
        
    if port_allowance_days < 0:
        raise ValueError(f"Port allowance days cannot be negative (>= 0 days). Provided: {port_allowance_days}")
        
    if delay_margin_pct is None or not isinstance(delay_margin_pct, (int, float)) or math.isnan(delay_margin_pct):
        raise ValueError("Delay margin percentage must be a valid numeric value.")
        
    if delay_margin_pct < 0:
        raise ValueError(f"Delay margin percentage cannot be negative (>= 0%). Provided: {delay_margin_pct}")

    if dispatch_mode is None or not isinstance(dispatch_mode, str) or dispatch_mode.lower() not in ["parallel", "sequential"]:
        raise ValueError(f"Dispatch mode must be either 'parallel' or 'sequential'. Provided: '{dispatch_mode}'")
    
    normalized_dispatch_mode = dispatch_mode.lower()

    if requested_delivery_days is not None:
        if not isinstance(requested_delivery_days, (int, float)) or math.isnan(requested_delivery_days):
            raise ValueError("Requested delivery days must be a valid numeric value.")
        if requested_delivery_days <= 0:
            raise ValueError(f"Requested delivery days must be a positive number (> 0 days). Provided: {requested_delivery_days}")

    if specs_df is None:
        specs_df = load_route_vessel_specs()

    # 2. Validate route & vessel selection
    available_vessels = get_available_vessels_for_route(origin, destination, specs_df)
    
    vessel_matched = [v for v in available_vessels if v.lower() == vessel_type.lower()]
    if not vessel_matched:
        avail_str = ", ".join(available_vessels)
        raise ValueError(
            f"Vessel type '{vessel_type}' is not supported for route '{origin}' -> '{destination}'. "
            f"Supported vessel types for this route: {avail_str}"
        )
    
    canonical_vessel = vessel_matched[0]

    # 3. Retrieve route-vessel specification parameters
    row = specs_df[
        (specs_df["Origin"].str.lower() == origin.lower()) &
        (specs_df["Destination"].str.lower() == destination.lower()) &
        (specs_df["Vessel_Type"].str.lower() == vessel_type.lower())
    ].iloc[0]

    distance_nm = float(row["Typical_Distance_NM"])
    speed_knots = float(row["Average_Speed_Knots"])
    typical_cargo_mt = float(row["Typical_Cargo_MT"])
    fuel_mt_day = float(row["Fuel_Consumption_MT_Day"])

    # 4. Pure sailing time calculation (Formula: distance_nm / (speed_knots * 24))
    sailing_hours = distance_nm / speed_knots
    pure_sailing_days = round(sailing_hours / 24.0, 2)

    # 5. Adjusted sailing days with sea/operational delay margin
    delay_multiplier = 1.0 + (float(delay_margin_pct) / 100.0)
    adjusted_sailing_days = round(pure_sailing_days * delay_multiplier, 2)

    # 6. Capacity check & cargo loads required calculation
    loads_required = math.ceil(quantity_mt / typical_cargo_mt)
    exceeds_capacity = quantity_mt > typical_cargo_mt

    # 7. Calculate single voyage duration and total estimated delivery time based on dispatch mode
    single_voyage_days = round(adjusted_sailing_days + float(port_allowance_days), 2)

    if normalized_dispatch_mode == "sequential":
        min_feasible_delivery_days = round(loads_required * single_voyage_days, 2)
    else:  # parallel (default)
        min_feasible_delivery_days = single_voyage_days

    # 8. Check feasibility against requested delivery time
    is_feasible = True
    delivery_status_msg = ""

    if requested_delivery_days is not None:
        if requested_delivery_days < min_feasible_delivery_days:
            is_feasible = False
            deficit_days = round(min_feasible_delivery_days - requested_delivery_days, 2)
            delivery_status_msg = (
                f"REJECTED: Requested delivery time ({requested_delivery_days} days) is BELOW "
                f"the minimum feasible duration ({min_feasible_delivery_days} days). "
                f"Deficit of {deficit_days} days. (Pure sailing: {pure_sailing_days}d, "
                f"Adjusted sailing [{delay_margin_pct}% delay margin]: {adjusted_sailing_days}d, "
                f"Port allowance: {port_allowance_days}d, Dispatch mode: '{normalized_dispatch_mode}')."
            )
        else:
            delivery_status_msg = (
                f"FEASIBLE: Requested delivery time ({requested_delivery_days} days) meets or exceeds "
                f"the minimum calculated delivery duration ({min_feasible_delivery_days} days)."
            )
    else:
        delivery_status_msg = f"ESTIMATED: Minimum calculated delivery duration is {min_feasible_delivery_days} days."

    # 9. Return comprehensive result dictionary
    return {
        "origin": row["Origin"],
        "destination": row["Destination"],
        "vessel_type": canonical_vessel,
        "quantity_mt": quantity_mt,
        "typical_cargo_mt": typical_cargo_mt,
        "distance_nm": distance_nm,
        "speed_knots": speed_knots,
        "fuel_consumption_mt_day": fuel_mt_day,
        "pure_sailing_days": pure_sailing_days,
        "sailing_days": pure_sailing_days,  # Backward compatibility alias
        "delay_margin_pct": float(delay_margin_pct),
        "adjusted_sailing_days": adjusted_sailing_days,
        "port_allowance_days": float(port_allowance_days),
        "min_feasible_delivery_days": min_feasible_delivery_days,
        "total_estimated_delivery_days": min_feasible_delivery_days,
        "requested_delivery_days": requested_delivery_days,
        "is_feasible": is_feasible,
        "exceeds_single_vessel_capacity": exceeds_capacity,
        "loads_required": loads_required,
        "dispatch_mode": normalized_dispatch_mode,
        "delivery_status_explanation": delivery_status_msg,
        "assumptions": [
            f"Pure sailing duration calculated at average speed of {speed_knots} knots over {distance_nm} NM.",
            f"Sea/operational delay margin set to {delay_margin_pct}% (Adjusted sailing: {adjusted_sailing_days} days).",
            f"Port operations allowance set to {port_allowance_days} days (assumes loading + unloading/port ops).",
            f"Single vessel cargo capacity benchmark for {canonical_vessel} is {typical_cargo_mt:,.0f} MT.",
            f"Multi-load cargo requirement of {loads_required} trip(s) assumes '{normalized_dispatch_mode}' dispatch schedule (not verified fleet availability)."
        ]
    }
