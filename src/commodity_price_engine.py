from pathlib import Path
import math
import pandas as pd

# Default dataset locations relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATASET_PATH = BASE_DIR / "data" / "processed" / "commodity_prices.parquet"
DEFAULT_EXCEL_PATH = BASE_DIR / "data" / "raw" / "CMO-Historical-Data-Monthly.xlsx"

# World Bank Pink Sheet unit metadata mapping for supported commodities
COMMODITY_UNIT_METADATA = {
    "Aluminum": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Banana, Europe": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Banana, US": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Barley": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Beef **": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Chicken **": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Cocoa": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Coconut oil": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Coffee, Arabica": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Coffee, Robusta": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Coal, Australian": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Coal, South African **": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Copper": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Cotton, A Index": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Crude oil, average": {"unit": "USD/bbl", "currency": "USD", "basis": "barrel", "supports_mt": False, "mt_factor": None},
    "Crude oil, Brent": {"unit": "USD/bbl", "currency": "USD", "basis": "barrel", "supports_mt": False, "mt_factor": None},
    "Crude oil, Dubai": {"unit": "USD/bbl", "currency": "USD", "basis": "barrel", "supports_mt": False, "mt_factor": None},
    "Crude oil, WTI": {"unit": "USD/bbl", "currency": "USD", "basis": "barrel", "supports_mt": False, "mt_factor": None},
    "DAP": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Fish meal": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Gold": {"unit": "USD/troy oz", "currency": "USD", "basis": "troy_ounce", "supports_mt": False, "mt_factor": None},
    "Groundnut oil **": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Groundnuts": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Iron ore, cfr spot": {"unit": "USD/dmtu", "currency": "USD", "basis": "dry_metric_ton_unit", "supports_mt": False, "mt_factor": None},
    "Lamb **": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Lead": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Liquefied natural gas, Japan": {"unit": "USD/mmbtu", "currency": "USD", "basis": "mmbtu", "supports_mt": False, "mt_factor": None},
    "Logs, Cameroon": {"unit": "USD/cubic meter", "currency": "USD", "basis": "cubic_meter", "supports_mt": False, "mt_factor": None},
    "Logs, Malaysian": {"unit": "USD/cubic meter", "currency": "USD", "basis": "cubic_meter", "supports_mt": False, "mt_factor": None},
    "Maize": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Natural gas index": {"unit": "2010=100", "currency": "INDEX", "basis": "index_points", "supports_mt": False, "mt_factor": None},
    "Natural gas, Europe": {"unit": "USD/mmbtu", "currency": "USD", "basis": "mmbtu", "supports_mt": False, "mt_factor": None},
    "Natural gas, US": {"unit": "USD/mmbtu", "currency": "USD", "basis": "mmbtu", "supports_mt": False, "mt_factor": None},
    "Nickel": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Orange": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Palm kernel oil": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Palm oil": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Phosphate rock": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Platinum": {"unit": "USD/troy oz", "currency": "USD", "basis": "troy_ounce", "supports_mt": False, "mt_factor": None},
    "Plywood": {"unit": "cents/sheet", "currency": "USD", "basis": "sheet", "supports_mt": False, "mt_factor": None},
    "Potassium chloride **": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Rapeseed oil": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Rice, Thai 25%": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Rice, Thai 5%": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Rice, Thai A.1": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Rice, Viet Namese 5%": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Rubber, RSS3": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Rubber, TSR20 **": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Sawnwood, Cameroon": {"unit": "USD/cubic meter", "currency": "USD", "basis": "cubic_meter", "supports_mt": False, "mt_factor": None},
    "Sawnwood, Malaysian": {"unit": "USD/cubic meter", "currency": "USD", "basis": "cubic_meter", "supports_mt": False, "mt_factor": None},
    "Shrimps, Mexican": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Silver": {"unit": "USD/troy oz", "currency": "USD", "basis": "troy_ounce", "supports_mt": False, "mt_factor": None},
    "Sorghum": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Soybean meal": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Soybean oil": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Soybeans": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Sugar, EU": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Sugar, US": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Sugar, world": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Sunflower oil": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Tea, avg 3 auctions": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Tea, Colombo": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Tea, Kolkata": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Tea, Mombasa": {"unit": "USD/kg", "currency": "USD", "basis": "kilogram", "supports_mt": True, "mt_factor": 1000.0},
    "Tin": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Tobacco, US import u.v.": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "TSP": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Urea": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Wheat, US HRW": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Wheat, US SRW": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0},
    "Zinc": {"unit": "USD/mt", "currency": "USD", "basis": "metric_ton", "supports_mt": True, "mt_factor": 1.0}
}


def load_commodity_prices(dataset_path=None):
    """
    Load the commodity prices Parquet dataset.
    
    Returns:
        pd.DataFrame containing Date, Commodity, and Price.
    """
    if dataset_path is None:
        dataset_path = DEFAULT_DATASET_PATH
        
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Commodity prices dataset not found at: {path}")
        
    df = pd.read_parquet(path)
    
    req_cols = ["Date", "Commodity", "Price"]
    missing_cols = [c for c in req_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset is missing required columns: {missing_cols}")
        
    return df


def get_supported_commodities(df=None):
    """
    Get a sorted list of unique commodity names in the dataset.
    
    Returns:
        List[str]: Sorted list of unique commodity names.
    """
    if df is None:
        df = load_commodity_prices()
        
    commodities = sorted(df["Commodity"].unique().tolist())
    return commodities


def search_commodity(query, df=None):
    """
    Search for commodity names matching a case-insensitive query string.
    
    Args:
        query (str): Search term.
        df (pd.DataFrame, optional): Pre-loaded commodity prices DataFrame.
        
    Returns:
        List[str]: Matching commodity names.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query must be a non-empty string.")
        
    all_commodities = get_supported_commodities(df)
    clean_query = query.strip().lower()
    
    matches = [c for c in all_commodities if clean_query in c.lower()]
    return matches


def get_latest_commodity_price(commodity_name, df=None):
    """
    Retrieve the latest valid price record for a selected commodity along with unit metadata.
    
    Args:
        commodity_name (str): Selected commodity name.
        df (pd.DataFrame, optional): Pre-loaded commodity prices DataFrame.
        
    Returns:
        dict: Latest price, date, unit, currency, and MT calculation support flag.
    """
    if not isinstance(commodity_name, str) or not commodity_name.strip():
        raise ValueError("Commodity name must be a non-empty string.")
        
    if df is None:
        df = load_commodity_prices()
        
    all_commodities = get_supported_commodities(df)
    
    # Exact case-insensitive match
    matched = [c for c in all_commodities if c.lower() == commodity_name.strip().lower()]
    
    if not matched:
        # Check partial matches to give helpful error message
        partial = search_commodity(commodity_name, df)
        if len(partial) > 1:
            candidates_str = ", ".join(f"'{c}'" for c in partial)
            raise ValueError(
                f"Ambiguous commodity search '{commodity_name}'. Multiple candidates matched: {candidates_str}. "
                "Please specify the exact commodity name."
            )
        elif len(partial) == 1:
            matched = partial
        else:
            sample_comm = ", ".join(f"'{c}'" for c in all_commodities[:5])
            raise ValueError(
                f"Commodity '{commodity_name}' not found in dataset. "
                f"Example supported commodities: {sample_comm} (Total supported: {len(all_commodities)})."
            )

    canonical_name = matched[0]
    
    # Filter non-null, positive price records for commodity
    sub_df = df[
        (df["Commodity"] == canonical_name) &
        (df["Price"].notnull()) &
        (df["Price"] > 0)
    ]
    
    if sub_df.empty:
        raise ValueError(f"No valid positive price records found for commodity '{canonical_name}'.")
        
    # Get latest row by max Date
    latest_row = sub_df.sort_values(by="Date", ascending=False).iloc[0]
    latest_date = latest_row["Date"]
    latest_price = float(latest_row["Price"])
    
    date_str = latest_date.strftime("%Y-%m-%d") if hasattr(latest_date, "strftime") else str(latest_date)
    
    # Unit metadata lookup
    unit_info = COMMODITY_UNIT_METADATA.get(canonical_name, {
        "unit": "UNKNOWN",
        "currency": "UNKNOWN",
        "basis": "unknown",
        "supports_mt": False,
        "mt_factor": None
    })
    
    return {
        "commodity": canonical_name,
        "date": date_str,
        "latest_price": latest_price,
        "recorded_unit": unit_info["unit"],
        "currency": unit_info["currency"],
        "supports_mt_calculation": unit_info["supports_mt"],
        "unit_basis": unit_info["basis"],
        "mt_factor": unit_info["mt_factor"]
    }


def calculate_commodity_value(commodity_name, quantity_mt, df=None):
    """
    Estimate FOB commodity purchase value for a given quantity in metric tonnes,
    provided the recorded unit metadata supports metric tonne conversion.
    
    Args:
        commodity_name (str): Selected commodity name.
        quantity_mt (float/int): Cargo quantity in metric tonnes (> 0).
        df (pd.DataFrame, optional): Pre-loaded commodity prices DataFrame.
        
    Returns:
        dict: Detailed calculation breakdown and purchase value estimate.
    """
    if quantity_mt is None or not isinstance(quantity_mt, (int, float)) or math.isnan(quantity_mt):
        raise ValueError("Cargo quantity must be a valid numeric value.")
        
    if quantity_mt <= 0:
        raise ValueError(f"Cargo quantity must be a positive number (> 0 MT). Provided: {quantity_mt}")
        
    price_info = get_latest_commodity_price(commodity_name, df)
    
    price_val = price_info["latest_price"]
    recorded_unit = price_info["recorded_unit"]
    supports_mt = price_info["supports_mt_calculation"]
    mt_factor = price_info["mt_factor"]
    
    value_calculated = False
    estimated_purchase_value_usd = None
    price_per_mt_usd = None
    explanation = ""
    
    if supports_mt and mt_factor is not None:
        price_per_mt_usd = round(price_val * mt_factor, 2)
        estimated_purchase_value_usd = round(quantity_mt * price_per_mt_usd, 2)
        value_calculated = True
        explanation = (
            f"FOB purchase value estimated successfully: {quantity_mt:,.2f} MT @ ${price_per_mt_usd:,.2f}/MT "
            f"(converted from recorded price of ${price_val:,.4f} per {price_info['unit_basis']})."
        )
    else:
        explanation = (
            f"UNSUPPORTED UNIT: Commodity '{price_info['commodity']}' has a recorded benchmark price unit of '{recorded_unit}'. "
            f"Purchase value in USD per Metric Ton cannot be directly computed without explicit volume/density or Fe-grade conversion factors."
        )
        
    return {
        "commodity": price_info["commodity"],
        "quantity_mt": float(quantity_mt),
        "price_date": price_info["date"],
        "latest_price": price_val,
        "recorded_unit": recorded_unit,
        "price_per_mt_usd": price_per_mt_usd,
        "value_calculated": value_calculated,
        "estimated_purchase_value_usd": estimated_purchase_value_usd,
        "calculation_notes": explanation,
        "disclaimer": (
            "NOTICE: The calculated value represents estimated FOB commodity purchase cost ONLY. "
            "It DOES NOT include ocean freight, vessel chartering, port tariffs, insurance, or landed cost expenses."
        )
    }
