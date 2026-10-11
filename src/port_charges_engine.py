from pathlib import Path
import math
import pandas as pd

# Default directory relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Mapping of all 18 standard port tariff Parquet filenames in data/processed/
TARIFF_FILES = {
    "wharfage": "wharfage_rates.parquet",
    "handling": "handling_charges.parquet",
    "environmental": "environmental_berth_charges.parquet",
    "stevedoring": "stevedoring_royalty_charges.parquet",
    "weighment": "weighment_charges.parquet",
    "railway": "railway_siding_charges.parquet",
    "transloading": "transloading_charges.parquet",
    "barge": "barge_facilitation_charges.parquet",
    "inland": "inland_waterway_charges.parquet",
    "iohp_mchp": "iohp_mchp_connectivity_charges.parquet",
    "ecl_ccl": "ecl_ccl_handling_charges.parquet",
    "demurrage": "demurrage_charges.parquet",
    "vessel_port": "vessel_port_charges.parquet",
    "pilotage_towage": "pilotage_towage_rates.parquet",
    "pilotage_additional": "pilotage_additional_charges.parquet",
    "water_supply": "water_supply_charges.parquet",
    "sbm": "sbm_charges.parquet",
    "sts": "sts_operation_charges.parquet",
}


def load_all_port_tariffs(processed_dir=None):
    """
    Load available Paradip port tariff datasets from Parquet files.
    
    Returns:
        dict: Mapping of category key -> pd.DataFrame (18 datasets)
    """
    if processed_dir is None:
        processed_dir = DEFAULT_PROCESSED_DIR
        
    p_dir = Path(processed_dir)
    if not p_dir.exists():
        raise FileNotFoundError(f"Processed data directory not found at: {p_dir}")
        
    tariffs = {}
    for key, filename in TARIFF_FILES.items():
        file_path = p_dir / filename
        if file_path.exists():
            tariffs[key] = pd.read_parquet(file_path)
            
    if not tariffs:
        raise ValueError(f"No port tariff Parquet files found in: {p_dir}")
        
    return tariffs


def list_available_tariff_categories(tariffs=None):
    """
    List supported port coverage, tariff categories, and required input parameters.
    
    Returns:
        dict: Coverage summary and category descriptions.
    """
    if tariffs is None:
        tariffs = load_all_port_tariffs()
        
    return {
        "supported_ports": ["Paradip"],
        "total_tariff_datasets": len(tariffs),
        "categories": {
            "standard_cargo_per_mt": [
                "wharfage (Wharfage rates by commodity & annual user throughput slabs - Requires user_annual_throughput_mt)",
                "mchp_unloading (MCHP coal wagon unloading at port - Coal only)",
                "mchp_shipment (MCHP coal vessel shipment/loading - Coal only)",
                "environmental (Water sprinkling, spillage cleaning & dredging charge)",
                "stevedoring (Stevedoring and shore handling agent royalty)",
                "weighment (Cargo weighbridge charges per consignment)",
                "railway (Railway siding usage fees)"
            ],
            "specialized_cargo_per_mt": [
                "transloading (Offshore mother/daughter vessel transloading fees)",
                "barge (Barge loading facilitation charge at IFFCO jetty)",
                "inland (Inland waterway VRC and wharfage)",
                "iohp_mchp (IOHP-MCHP inter-plant conveyor transfer charges)",
                "ecl_ccl (Coal company handling discounted rates)"
            ],
            "vessel_time_based_charges": [
                "berth_hire (Berth Hire per GT/hour & Roadstead fees - Requires vessel_gt and port_stay_hours)",
                "pilotage_towage (Pilotage and tug assistance rates per GRT slab - Requires vessel GRT)",
                "water_supply (Fresh water supply per MT - Requires water volume MT)"
            ],
            "storage_demurrage_charges": [
                "demurrage (Import dry bulk cargo storage demurrage per MT/day beyond free period - Requires total_storage_days & free_storage_days)"
            ]
        }
    }


def _match_commodity_key(user_commodity, available_commodities):
    """Helper to match user commodity string against tariff table commodities."""
    if not user_commodity:
        return "Other cargo not specified above"
        
    clean_user = user_commodity.strip().lower()
    
    for cand in available_commodities:
        if clean_user == cand.lower():
            return cand
            
    for cand in available_commodities:
        if clean_user in cand.lower() or cand.lower() in clean_user:
            return cand
            
    if "coal" in clean_user or "coke" in clean_user:
        for cand in available_commodities:
            if "coal" in cand.lower():
                return cand
    if "iron" in clean_user or "ore" in clean_user or "chrome" in clean_user:
        for cand in available_commodities:
            if "ore" in cand.lower() or "iron" in cand.lower() or "chrome" in cand.lower():
                return cand
                
    return "Other cargo not specified above"


def calculate_port_charges(
    quantity_mt,
    commodity="Coal/Coke",
    traffic_type="Foreign",
    user_annual_throughput_mt=None,
    planned_shipment_date=None,
    vessel_gt=None,
    port_stay_hours=None,
    total_storage_days=None,
    free_storage_days=None,
    usd_to_inr_rate=None,
    exchange_rate_date=None,
    selected_services=None,
    processed_dir=None
):
    """
    Calculate itemized rule-based Paradip port charges strictly grounded in source Parquet records.
    
    Args:
        quantity_mt (float/int): Cargo quantity in metric tonnes (> 0).
        commodity (str, optional): Commodity name.
        traffic_type (str, optional): Traffic classification ('Foreign' or 'Coastal').
        user_annual_throughput_mt (float, optional): User's total annual throughput in MT per annum for volume slab selection.
        planned_shipment_date (str/datetime, optional): Target shipment date (e.g. '2026-05-01').
        vessel_gt (float, optional): Vessel Gross Tonnage (GT) for berth hire calculation.
        port_stay_hours (float, optional): Total port stay duration in hours.
        total_storage_days (float, optional): Total cargo storage days in port transit area.
        free_storage_days (float, optional): Free storage days allowed by storage location/contract.
        usd_to_inr_rate (float, optional): Explicit USD-to-INR exchange rate for unified conversion.
        exchange_rate_date (str, optional): Date of supplied exchange rate.
        selected_services (list, optional): List of service keys to calculate.
        processed_dir (Path/str, optional): Custom path to processed parquet datasets.
        
    Returns:
        dict: Detailed breakdown containing calculated_charges, excluded_charges, uncalculated_notices,
              requires_verification, selected_services_total_inr/usd, complete_port_cost_estimate_inr/usd,
              and strict completeness flags.
    """
    # 1. Validate inputs
    if quantity_mt is None or not isinstance(quantity_mt, (int, float)) or math.isnan(quantity_mt):
        raise ValueError("Cargo quantity must be a valid numeric value.")
        
    if quantity_mt <= 0:
        raise ValueError(f"Cargo quantity must be a positive number (> 0 MT). Provided: {quantity_mt}")
        
    if traffic_type is None or not isinstance(traffic_type, str) or traffic_type.title() not in ["Foreign", "Coastal"]:
        raise ValueError(f"Traffic type must be either 'Foreign' or 'Coastal'. Provided: '{traffic_type}'")
        
    norm_traffic_type = traffic_type.title()

    if user_annual_throughput_mt is not None:
        if not isinstance(user_annual_throughput_mt, (int, float)) or math.isnan(user_annual_throughput_mt) or user_annual_throughput_mt < 0:
            raise ValueError(f"User annual throughput MT must be a non-negative number. Provided: {user_annual_throughput_mt}")

    shipment_dt = None
    if planned_shipment_date is not None:
        try:
            shipment_dt = pd.to_datetime(planned_shipment_date)
        except Exception:
            raise ValueError(f"Invalid planned shipment date format: '{planned_shipment_date}'")

    if vessel_gt is not None:
        if not isinstance(vessel_gt, (int, float)) or math.isnan(vessel_gt) or vessel_gt < 0:
            raise ValueError(f"Vessel GT must be a non-negative number. Provided: {vessel_gt}")
            
    if port_stay_hours is not None:
        if not isinstance(port_stay_hours, (int, float)) or math.isnan(port_stay_hours) or port_stay_hours < 0:
            raise ValueError(f"Port stay hours must be a non-negative number. Provided: {port_stay_hours}")

    if total_storage_days is not None:
        if not isinstance(total_storage_days, (int, float)) or math.isnan(total_storage_days) or total_storage_days < 0:
            raise ValueError(f"Total storage days must be a non-negative number. Provided: {total_storage_days}")

    if free_storage_days is not None:
        if not isinstance(free_storage_days, (int, float)) or math.isnan(free_storage_days) or free_storage_days < 0:
            raise ValueError(f"Free storage days must be a non-negative number. Provided: {free_storage_days}")
            
    if usd_to_inr_rate is not None:
        if not isinstance(usd_to_inr_rate, (int, float)) or math.isnan(usd_to_inr_rate) or usd_to_inr_rate <= 0:
            raise ValueError(f"USD to INR exchange rate must be a positive number (> 0). Provided: {usd_to_inr_rate}")

    tariffs = load_all_port_tariffs(processed_dir)

    default_standard_services = ["wharfage", "mchp_unloading", "mchp_shipment", "environmental", "stevedoring", "weighment", "railway"]
    active_services = selected_services if selected_services is not None else default_standard_services

    calculated_charges = []
    excluded_charges = []
    missing_inputs_notices = []
    requires_verification = []
    
    total_inr = 0.0
    total_usd = 0.0

    is_coal = any(term in commodity.lower() for term in ["coal", "coke"])

    # -------------------------------------------------------------------------
    # SERVICE 1: Volume-Based Wharfage (Requires user_annual_throughput_mt)
    # -------------------------------------------------------------------------
    if "wharfage" in active_services and "wharfage" in tariffs:
        df_w = tariffs["wharfage"]
        avail_comms = df_w["Commodity"].unique()
        matched_comm = _match_commodity_key(commodity, avail_comms)
        sub_w = df_w[df_w["Commodity"] == matched_comm]

        # Source rule: Wharfage volume slabs depend on user's annual throughput per commodity per annum.
        # If user_annual_throughput_mt is NOT provided, do NOT substitute shipment quantity.
        is_volume_based = not sub_w.empty and (sub_w["Rate_Type"].str.lower() == "volume-based").any()

        if is_volume_based and user_annual_throughput_mt is None:
            missing_inputs_notices.append({
                "service": "Wharfage Charges",
                "service_key": "wharfage",
                "status": "missing_inputs",
                "required_missing_inputs": ["user_annual_throughput_mt (User annual throughput in MT per annum)"],
                "reason": f"Wharfage tariff for '{matched_comm}' specifies volume-based slabs based on annual user throughput per annum. "
                          "Wharfage cannot be calculated without an explicit user_annual_throughput_mt input."
            })
        elif not sub_w.empty:
            rate = None
            rate_col = f"{norm_traffic_type}_Rate"
            volume_eval_mt = user_annual_throughput_mt if is_volume_based else quantity_mt
            
            for _, r in sub_w.iterrows():
                min_v = r["Volume_Min_MT"] if not math.isnan(r["Volume_Min_MT"]) else 0
                max_v = r["Volume_Max_MT"] if not math.isnan(r["Volume_Max_MT"]) else float("inf")
                
                if min_v <= volume_eval_mt <= max_v:
                    rate = float(r[rate_col])
                    break
            if rate is None:
                rate = float(sub_w.iloc[-1][rate_col])
                
            amount = round(quantity_mt * rate, 2)
            total_inr += amount
            
            basis_str = f"{quantity_mt:,.2f} MT (Slab evaluated at {volume_eval_mt:,.2f} MT/annum)" if is_volume_based else f"{quantity_mt:,.2f} MT"
            calculated_charges.append({
                "service": "Wharfage Charges",
                "service_key": "wharfage",
                "tariff_source": TARIFF_FILES["wharfage"],
                "rate": rate,
                "unit": "Rs/MT",
                "basis": basis_str,
                "currency": "INR",
                "charge_amount": amount,
                "status": "calculated",
                "formula": f"{quantity_mt:,.2f} MT * Rs.{rate:.2f}/MT ({matched_comm}, {norm_traffic_type})"
            })

    # -------------------------------------------------------------------------
    # SERVICE 2: MCHP Wagon Unloading (Coal Only)
    # -------------------------------------------------------------------------
    if "mchp_unloading" in active_services:
        if is_coal:
            if "handling" in tariffs:
                df_h = tariffs["handling"]
                sub_h = df_h[df_h["Commodity"] == "Coal/Coke"]
                rate_col = f"{norm_traffic_type}_Rate"
                rows_un = sub_h[sub_h["Charge_Name"].str.contains("Unloading", case=False, na=False)]
                if not rows_un.empty:
                    un_rate = float(rows_un.iloc[0][rate_col])
                    un_amount = round(quantity_mt * un_rate, 2)
                    total_inr += un_amount
                    calculated_charges.append({
                        "service": "MCHP Wagon Unloading",
                        "service_key": "mchp_unloading",
                        "tariff_source": TARIFF_FILES["handling"],
                        "rate": un_rate,
                        "unit": "Rs/MT",
                        "basis": f"{quantity_mt:,.2f} MT",
                        "currency": "INR",
                        "charge_amount": un_amount,
                        "status": "calculated",
                        "formula": f"{quantity_mt:,.2f} MT * Rs.{un_rate:.2f}/MT (MCHP Wagon Unloading, {norm_traffic_type})"
                    })
        else:
            excluded_charges.append({
                "service": "MCHP Wagon Unloading",
                "service_key": "mchp_unloading",
                "reason": f"Excluded: Mechanized Coal Handling Plant (MCHP) wagon unloading tariff applies exclusively to Coal/Coke cargoes. Selected commodity is '{commodity}'."
            })

    # -------------------------------------------------------------------------
    # SERVICE 3: MCHP Vessel Shipment (Coal Only)
    # -------------------------------------------------------------------------
    if "mchp_shipment" in active_services:
        if is_coal:
            if "handling" in tariffs:
                df_h = tariffs["handling"]
                sub_h = df_h[df_h["Commodity"] == "Coal/Coke"]
                rate_col = f"{norm_traffic_type}_Rate"
                rows_sh = sub_h[sub_h["Charge_Name"].str.contains("Shipment", case=False, na=False)]
                if not rows_sh.empty:
                    sh_rate = float(rows_sh.iloc[0][rate_col])
                    sh_amount = round(quantity_mt * sh_rate, 2)
                    total_inr += sh_amount
                    calculated_charges.append({
                        "service": "MCHP Vessel Shipment",
                        "service_key": "mchp_shipment",
                        "tariff_source": TARIFF_FILES["handling"],
                        "rate": sh_rate,
                        "unit": "Rs/MT",
                        "basis": f"{quantity_mt:,.2f} MT",
                        "currency": "INR",
                        "charge_amount": sh_amount,
                        "status": "calculated",
                        "formula": f"{quantity_mt:,.2f} MT * Rs.{sh_rate:.2f}/MT (MCHP Vessel Shipment, {norm_traffic_type})"
                    })
        else:
            excluded_charges.append({
                "service": "MCHP Vessel Shipment",
                "service_key": "mchp_shipment",
                "reason": f"Excluded: Mechanized Coal Handling Plant (MCHP) vessel shipment tariff applies exclusively to Coal/Coke cargoes. Selected commodity is '{commodity}'."
            })

    # -------------------------------------------------------------------------
    # SERVICE 4: Environmental Berth Charge
    # -------------------------------------------------------------------------
    if "environmental" in active_services and "environmental" in tariffs:
        df_env = tariffs["environmental"]
        rate = float(df_env.iloc[0]["Rate"])
        amount = round(quantity_mt * rate, 2)
        total_inr += amount
        calculated_charges.append({
            "service": "Environmental / Berth Maintenance",
            "service_key": "environmental",
            "tariff_source": TARIFF_FILES["environmental"],
            "rate": rate,
            "unit": "Rs/MT",
            "basis": f"{quantity_mt:,.2f} MT",
            "currency": "INR",
            "charge_amount": amount,
            "status": "calculated",
            "formula": f"{quantity_mt:,.2f} MT * Rs.{rate:.2f}/MT (Water sprinkling, spillage cleaning & dredging)"
        })

    # -------------------------------------------------------------------------
    # SERVICE 5: Stevedoring Royalty (Effective Date Checked)
    # -------------------------------------------------------------------------
    if "stevedoring" in active_services and "stevedoring" in tariffs:
        df_stev = tariffs["stevedoring"]
        row_stev = df_stev.iloc[0]
        rate = float(row_stev["Rate"])
        eff_date_str = str(row_stev["Effective_From"])
        eff_dt = pd.to_datetime(eff_date_str)
        
        is_active = True
        
        if shipment_dt is not None:
            if shipment_dt < eff_dt:
                is_active = False
                missing_inputs_notices.append({
                    "service": "Stevedoring & Shore Handling Royalty",
                    "service_key": "stevedoring",
                    "status": "inactive_effective_date",
                    "reason": f"Stevedoring royalty rate of Rs.{rate}/MT is effective from {eff_date_str}, which is after planned shipment date ({shipment_dt.strftime('%Y-%m-%d')})."
                })
        else:
            requires_verification.append({
                "service": "Stevedoring & Shore Handling Royalty",
                "rule": "Effective Date Verification",
                "issue": f"Tariff specifies Effective_From = '{eff_date_str}'. Planned shipment date was not provided; rate was assumed active."
            })

        if is_active:
            amount = round(quantity_mt * rate, 2)
            total_inr += amount
            calculated_charges.append({
                "service": "Stevedoring & Shore Handling Royalty",
                "service_key": "stevedoring",
                "tariff_source": TARIFF_FILES["stevedoring"],
                "rate": rate,
                "unit": "Rs/MT",
                "basis": f"{quantity_mt:,.2f} MT",
                "currency": "INR",
                "charge_amount": amount,
                "status": "calculated",
                "effective_from": eff_date_str,
                "formula": f"{quantity_mt:,.2f} MT * Rs.{rate:.2f}/MT (Effective from {eff_date_str})"
            })

    # -------------------------------------------------------------------------
    # SERVICE 6: Cargo Weighment
    # -------------------------------------------------------------------------
    if "weighment" in active_services and "weighment" in tariffs:
        df_wm = tariffs["weighment"]
        is_ore = any(term in commodity.lower() for term in ["ore", "chrome", "iron", "manganese"])
        cat = "Iron Ore/Chrome Ore/Other Ores" if is_ore else "Other Commodities"
        row_wm = df_wm[df_wm["Commodity_Category"] == cat].iloc[0]
        
        rate = float(row_wm["Rate"])
        min_charge = float(row_wm["Minimum_Charge"])
        calculated_val = quantity_mt * rate
        amount = round(max(calculated_val, min_charge), 2)
        total_inr += amount
        
        calculated_charges.append({
            "service": "Cargo Weighment",
            "service_key": "weighment",
            "tariff_source": TARIFF_FILES["weighment"],
            "rate": rate,
            "unit": "Rs/ton",
            "basis": f"{quantity_mt:,.2f} MT",
            "currency": "INR",
            "charge_amount": amount,
            "status": "calculated",
            "formula": f"max({quantity_mt:,.2f} MT * Rs.{rate:.2f}/ton, min Rs.{min_charge:.2f})"
        })

    # -------------------------------------------------------------------------
    # SERVICE 7: Railway Siding Usage
    # -------------------------------------------------------------------------
    if "railway" in active_services and "railway" in tariffs:
        df_rs = tariffs["railway"]
        row_rs = df_rs.iloc[0]
        rate = float(row_rs["Rate"])
        amount = round(quantity_mt * rate, 2)
        total_inr += amount
        calculated_charges.append({
            "service": "Railway Siding Usage",
            "service_key": "railway",
            "tariff_source": TARIFF_FILES["railway"],
            "rate": rate,
            "unit": "Rs/MT",
            "basis": f"{quantity_mt:,.2f} MT",
            "currency": "INR",
            "charge_amount": amount,
            "status": "calculated",
            "formula": f"{quantity_mt:,.2f} MT * Rs.{rate:.2f}/MT ({row_rs['Siding_Type']})"
        })

    # -------------------------------------------------------------------------
    # SERVICE 8: Vessel Berth Hire (Requires GT & Port Hours)
    # -------------------------------------------------------------------------
    if ("vessel_port" in active_services or "berth_hire" in active_services) and "vessel_port" in tariffs:
        if vessel_gt is not None and port_stay_hours is not None:
            df_vp = tariffs["vessel_port"]
            sub_vp = df_vp[
                (df_vp["Charge_Category"] == "Berth Hire") &
                (df_vp["Traffic_Type"] == norm_traffic_type)
            ]
            if not sub_vp.empty:
                row_vp = sub_vp.iloc[0]
                rate = float(row_vp["Rate"])
                unit = str(row_vp["Unit"])
                curr = "USD" if norm_traffic_type == "Foreign" else "INR"
                amount = round(vessel_gt * port_stay_hours * rate, 2)
                
                if curr == "USD":
                    total_usd += amount
                else:
                    total_inr += amount
                    
                calculated_charges.append({
                    "service": "Vessel Berth Hire",
                    "service_key": "berth_hire",
                    "tariff_source": TARIFF_FILES["vessel_port"],
                    "rate": rate,
                    "unit": unit,
                    "basis": f"{vessel_gt:,.0f} GT * {port_stay_hours:,.1f} Hours",
                    "currency": curr,
                    "charge_amount": amount,
                    "status": "calculated",
                    "formula": f"{vessel_gt:,.0f} GT * {port_stay_hours:,.1f} hrs * {rate} {unit}"
                })
        else:
            missing_inputs_notices.append({
                "service": "Vessel Berth Hire",
                "service_key": "berth_hire",
                "status": "missing_inputs",
                "required_missing_inputs": ["vessel_gt (Gross Tonnage)", "port_stay_hours (Port stay duration in hours)"],
                "reason": "Berth Hire is calculated per GT per hour and cannot be computed without vessel GT and port stay duration."
            })

    # -------------------------------------------------------------------------
    # SERVICE 9: Cargo Storage Demurrage (Requires total_storage_days & free_storage_days)
    # -------------------------------------------------------------------------
    if "demurrage" in active_services and "demurrage" in tariffs:
        if total_storage_days is not None:
            if free_storage_days is not None:
                chargeable_days = max(0.0, float(total_storage_days) - float(free_storage_days))
                
                if chargeable_days > 0:
                    df_dem = tariffs["demurrage"]
                    total_dem_cost = 0.0
                    rem_days = chargeable_days
                    
                    # W1 (Days 1-7 beyond free period)
                    w1_days = min(rem_days, 7.0)
                    r1 = float(df_dem[df_dem["Period"] == "1st week"].iloc[0]["Rate"])
                    total_dem_cost += quantity_mt * w1_days * r1
                    rem_days -= w1_days
                    
                    # W2 (Days 8-14 beyond free period)
                    if rem_days > 0:
                        w2_days = min(rem_days, 7.0)
                        r2 = float(df_dem[df_dem["Period"] == "2nd week"].iloc[0]["Rate"])
                        total_dem_cost += quantity_mt * w2_days * r2
                        rem_days -= w2_days
                        
                    # W3+ (Days 15+ beyond free period)
                    if rem_days > 0:
                        r3 = float(df_dem[df_dem["Period"] == "3rd week onwards"].iloc[0]["Rate"])
                        total_dem_cost += quantity_mt * rem_days * r3
                        
                    amount = round(total_dem_cost, 2)
                    total_inr += amount
                    calculated_charges.append({
                        "service": "Cargo Storage Demurrage",
                        "service_key": "demurrage",
                        "tariff_source": TARIFF_FILES["demurrage"],
                        "rate": "Tiered (Days 1-7: Rs.4.77, Days 8-14: Rs.14.32, Days 15+: Rs.23.88)",
                        "unit": "Rs/MT/day",
                        "basis": f"{quantity_mt:,.2f} MT * {chargeable_days:.1f} Chargeable Days (Total: {total_storage_days:.1f}d - Free: {free_storage_days:.1f}d)",
                        "currency": "INR",
                        "charge_amount": amount,
                        "status": "calculated",
                        "formula": f"Tiered cargo storage demurrage over {chargeable_days:.1f} chargeable days beyond free storage period"
                    })
                else:
                    excluded_charges.append({
                        "service": "Cargo Storage Demurrage",
                        "service_key": "demurrage",
                        "reason": f"No chargeable storage demurrage accrued (Total storage days {total_storage_days:.1f} <= free storage days {free_storage_days:.1f})."
                    })
            else:
                missing_inputs_notices.append({
                    "service": "Cargo Storage Demurrage",
                    "service_key": "demurrage",
                    "status": "missing_inputs",
                    "required_missing_inputs": ["free_storage_days (Free storage period allowed by port/contract)"],
                    "reason": "Section 2.10 specifies demurrage applies beyond the free period. Free period duration varies by storage location and contract regulations, so free_storage_days must be explicitly provided."
                })
        else:
            missing_inputs_notices.append({
                "service": "Cargo Storage Demurrage",
                "service_key": "demurrage",
                "status": "missing_inputs",
                "required_missing_inputs": ["total_storage_days (Total storage days in transit area)"],
                "reason": "Cargo storage demurrage applies only when import dry bulk cargo remains in transit storage beyond the free period."
            })

    # -------------------------------------------------------------------------
    # CURRENCY CONVERSION & STRICT COMPLETENESS CHECK
    # -------------------------------------------------------------------------
    selected_services_total_inr = round(total_inr, 2)
    selected_services_total_usd = round(total_usd, 2)
    converted_total_usd = None
    converted_total_inr = None

    if usd_to_inr_rate is not None:
        converted_total_usd = round(total_usd + (total_inr / usd_to_inr_rate), 2)
        converted_total_inr = round(total_inr + (total_usd * usd_to_inr_rate), 2)

    # Strictly False if any missing input notice, unverified notice exists, or if only a partial subset of services was calculated
    is_complete_selected_services = (len(missing_inputs_notices) == 0)
    
    # Complete port estimate requires that berth hire and all standard services are accounted for
    all_standard_requested = (selected_services is None) or all(s in active_services for s in default_standard_services)
    is_complete_port_total = is_complete_selected_services and (len(requires_verification) == 0) and all_standard_requested and (vessel_gt is not None) and (port_stay_hours is not None)

    # Only present complete_port_cost_estimate if is_complete_port_total is True
    complete_port_cost_estimate_inr = selected_services_total_inr if is_complete_port_total else None
    complete_port_cost_estimate_usd = selected_services_total_usd if is_complete_port_total else None

    return {
        "port": "Paradip",
        "quantity_mt": float(quantity_mt),
        "commodity": commodity,
        "traffic_type": norm_traffic_type,
        "user_annual_throughput_mt": user_annual_throughput_mt,
        "planned_shipment_date": planned_shipment_date,
        "selected_services_total_inr": selected_services_total_inr,
        "selected_services_total_usd": selected_services_total_usd,
        "complete_port_cost_estimate_inr": complete_port_cost_estimate_inr,
        "complete_port_cost_estimate_usd": complete_port_cost_estimate_usd,
        "total_inr": selected_services_total_inr,  # Backward compatibility alias
        "total_usd": selected_services_total_usd,  # Backward compatibility alias
        "converted_total_usd": converted_total_usd,
        "converted_total_inr": converted_total_inr,
        "usd_to_inr_rate_used": usd_to_inr_rate,
        "exchange_rate_date": exchange_rate_date,
        "is_complete_port_total": is_complete_port_total,
        "is_complete_selected_services": is_complete_selected_services,
        "calculated_charges": calculated_charges,
        "excluded_charges": excluded_charges,
        "uncalculated_notices": missing_inputs_notices,
        "requires_verification": requires_verification,
        "disclaimer": (
            "NOTICE: Calculated port charges represent rule-based Paradip Port Scale of Rates (2026-27). "
            "They DO NOT include ocean freight, commodity purchase value, or unrequested specialized port ops."
        )
    }
