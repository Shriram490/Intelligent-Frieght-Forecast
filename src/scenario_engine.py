from pathlib import Path
import math
import pandas as pd

# Import core engines
from transit_time_engine import (
    load_route_vessel_specs,
    get_available_routes,
    get_available_vessels_for_route
)
from landed_cost_engine import calculate_landed_cost


def get_all_supported_scenarios(specs_df=None):
    """
    Retrieve all valid, supported (Origin, Destination, Vessel_Type) combinations in the dataset.
    
    Returns:
        List[dict]: List of supported candidate configs with route & vessel metadata.
    """
    if specs_df is None:
        specs_df = load_route_vessel_specs()
        
    candidates = []
    for _, row in specs_df.iterrows():
        candidates.append({
            "origin": row["Origin"],
            "destination": row["Destination"],
            "vessel_type": row["Vessel_Type"],
            "distance_nm": float(row["Typical_Distance_NM"]),
            "speed_knots": float(row["Average_Speed_Knots"]),
            "typical_cargo_mt": float(row["Typical_Cargo_MT"])
        })
    return candidates


def evaluate_scenario_candidates(
    commodity,
    quantity_mt,
    candidate_configs=None,
    filter_origin=None,
    filter_destination=None,
    traffic_type="Foreign",
    planned_shipment_date=None,
    user_annual_throughput_mt=None,
    requested_delivery_days=None,
    port_allowance_days=4.0,
    delay_margin_pct=0.0,
    dispatch_mode="parallel",
    freight_rates_by_scenario=None,
    default_usd_per_mt=None,
    default_charter_usd_per_day=None,
    bunker_fuel_price_usd_per_mt=None,
    vessel_gt=None,
    port_stay_hours=None,
    total_storage_days=None,
    free_storage_days=None,
    usd_to_inr_rate=None,
    selected_port_services=None,
    specs_df=None
):
    """
    Evaluate multiple route-vessel scenarios using the landed cost engine.
    
    Args:
        commodity (str): Selected commodity name.
        quantity_mt (float/int): Cargo quantity in metric tonnes (> 0).
        candidate_configs (list of dict, optional): Explicit list of [{'origin': ..., 'destination': ..., 'vessel_type': ...}].
            If None, evaluates all supported route-vessel combinations filtered by filter_origin/filter_destination.
        filter_origin (str, optional): Optional filter for origin port.
        filter_destination (str, optional): Optional filter for destination port.
        traffic_type (str, optional): 'Foreign' or 'Coastal'.
        planned_shipment_date (str, optional): Target shipment date.
        user_annual_throughput_mt (float, optional): User's annual throughput in MT.
        requested_delivery_days (float, optional): Target delivery deadline in days.
        port_allowance_days (float, optional): Configurable port allowance days.
        delay_margin_pct (float, optional): Configurable sea delay margin percentage.
        dispatch_mode (str, optional): 'parallel' or 'sequential'.
        freight_rates_by_scenario (dict, optional): Map of (origin, dest, vessel) -> {'usd_per_mt': ..., 'charter_usd_per_day': ...}.
        default_usd_per_mt (float, optional): Fallback USD/MT freight rate applied to all candidates if not in mapping.
        default_charter_usd_per_day (float, optional): Fallback USD/day charter rate.
        bunker_fuel_price_usd_per_mt (float, optional): Bunker fuel price in USD/MT.
        vessel_gt (float, optional): Vessel Gross Tonnage.
        port_stay_hours (float, optional): Port stay hours.
        total_storage_days (float, optional): Total port transit storage days.
        free_storage_days (float, optional): Free storage allowance days.
        usd_to_inr_rate (float, optional): Explicit USD to INR exchange rate.
        selected_port_services (list, optional): List of port service keys to include.
        specs_df (pd.DataFrame, optional): Pre-loaded specs DataFrame.
        
    Returns:
        dict: Evaluated candidates, feasible candidates, infeasible candidates,
              rankings, and transparent recommendations.
    """
    if quantity_mt is None or not isinstance(quantity_mt, (int, float)) or math.isnan(quantity_mt) or quantity_mt <= 0:
        raise ValueError(f"Cargo quantity must be a positive number (> 0 MT). Provided: {quantity_mt}")

    if specs_df is None:
        specs_df = load_route_vessel_specs()

    # Determine candidate pool
    if candidate_configs is None:
        all_specs = get_all_supported_scenarios(specs_df)
        pool = []
        for s in all_specs:
            if filter_origin and s["origin"].lower() != filter_origin.lower():
                continue
            if filter_destination and s["destination"].lower() != filter_destination.lower():
                continue
            pool.append(s)
    else:
        pool = candidate_configs

    if not pool:
        raise ValueError("No scenario candidates available for evaluation under the specified route filters.")

    evaluated_candidates = []
    supported_tuples = set((s["origin"].lower(), s["destination"].lower(), s["vessel_type"].lower()) for s in get_all_supported_scenarios(specs_df))

    for cand in pool:
        orig = cand.get("origin")
        dest = cand.get("destination")
        vessel = cand.get("vessel_type")

        # 1. Validate if candidate is a supported route-vessel combo
        cand_key = (orig.lower() if orig else "", dest.lower() if dest else "", vessel.lower() if vessel else "")
        if cand_key not in supported_tuples:
            evaluated_candidates.append({
                "scenario_name": f"{orig} -> {dest} ({vessel})",
                "origin": orig,
                "destination": dest,
                "vessel_type": vessel,
                "is_supported_combination": False,
                "is_transit_feasible": False,
                "is_cost_known": False,
                "is_complete_within_scope": False,
                "rejection_reason": f"Unsupported route-vessel combination: '{orig}' -> '{dest}' with '{vessel}'.",
                "landed_cost_usd": None,
                "landed_cost_per_mt_usd": None,
                "transit_days": None,
                "loads_required": None,
                "missing_components": ["Unsupported route-vessel configuration"],
                "raw_result": None
            })
            continue

        # Extract scenario-specific rate or fallback
        rate_info = {}
        if freight_rates_by_scenario:
            rate_info = freight_rates_by_scenario.get((orig, dest, vessel), {})
            if not rate_info:
                # Try case-insensitive lookup
                for (ko, kd, kv), val in freight_rates_by_scenario.items():
                    if ko.lower() == orig.lower() and kd.lower() == dest.lower() and kv.lower() == vessel.lower():
                        rate_info = val
                        break

        cand_usd_per_mt = rate_info.get("usd_per_mt", default_usd_per_mt)
        cand_charter_usd_per_day = rate_info.get("charter_usd_per_day", default_charter_usd_per_day)

        try:
            res = calculate_landed_cost(
                commodity=commodity,
                quantity_mt=quantity_mt,
                origin=orig,
                destination=dest,
                vessel_type=vessel,
                traffic_type=traffic_type,
                planned_shipment_date=planned_shipment_date,
                user_annual_throughput_mt=user_annual_throughput_mt,
                requested_delivery_days=requested_delivery_days,
                port_allowance_days=port_allowance_days,
                delay_margin_pct=delay_margin_pct,
                dispatch_mode=dispatch_mode,
                usd_per_mt=cand_usd_per_mt,
                charter_usd_per_day=cand_charter_usd_per_day,
                bunker_fuel_price_usd_per_mt=bunker_fuel_price_usd_per_mt,
                vessel_gt=vessel_gt,
                port_stay_hours=port_stay_hours,
                total_storage_days=total_storage_days,
                free_storage_days=free_storage_days,
                usd_to_inr_rate=usd_to_inr_rate,
                selected_port_services=selected_port_services,
                specs_df=specs_df
            )

            is_feasible = res["is_transit_feasible"]
            is_complete = res["is_complete_within_scope"]
            cost_usd = res["landed_cost_estimate_usd"]
            cost_per_mt = res["landed_cost_per_mt_usd"]
            transit_days = res["transit_time_summary"]["min_feasible_delivery_days"]
            loads = res["transit_time_summary"]["loads_required"]

            rejection_reason = None
            if not is_feasible:
                rejection_reason = res["transit_time_summary"]["status_explanation"]

            evaluated_candidates.append({
                "scenario_name": f"{orig} -> {dest} ({vessel})",
                "origin": orig,
                "destination": dest,
                "vessel_type": vessel,
                "is_supported_combination": True,
                "is_transit_feasible": is_feasible,
                "is_cost_known": is_complete and (cost_usd is not None),
                "is_complete_within_scope": is_complete,
                "is_all_in_cost_known": res["is_all_in_cost_known"],
                "rejection_reason": rejection_reason,
                "landed_cost_usd": cost_usd,
                "landed_cost_per_mt_usd": cost_per_mt,
                "partial_landed_cost_usd": res["partial_landed_cost_usd"],
                "transit_days": transit_days,
                "sailing_days": res["transit_time_summary"]["sailing_days"],
                "port_allowance_days": res["transit_time_summary"]["port_allowance_days"],
                "loads_required": loads,
                "ocean_freight_available": res["is_ocean_freight_available"],
                "ocean_freight_cost_usd": res["ocean_freight_cost_usd"],
                "ocean_freight_provenance": res["ocean_freight_provenance"],
                "port_charges_inr": res["port_charges_selected_services_total_inr"],
                "port_charges_usd": res["port_charges_selected_services_total_usd"],
                "missing_components": res["missing_components"],
                "raw_result": res
            })

        except Exception as e:
            evaluated_candidates.append({
                "scenario_name": f"{orig} -> {dest} ({vessel})",
                "origin": orig,
                "destination": dest,
                "vessel_type": vessel,
                "is_supported_combination": True,
                "is_transit_feasible": False,
                "is_cost_known": False,
                "is_complete_within_scope": False,
                "rejection_reason": f"Calculation error: {e}",
                "landed_cost_usd": None,
                "landed_cost_per_mt_usd": None,
                "transit_days": None,
                "loads_required": None,
                "missing_components": [str(e)],
                "raw_result": None
            })

    return rank_and_optimize_scenarios(
        evaluated_candidates,
        requested_delivery_days=requested_delivery_days
    )


def rank_and_optimize_scenarios(evaluated_candidates, requested_delivery_days=None):
    """
    Rank evaluated scenario candidates and determine transparent optimal recommendations.
    
    Optimization Objectives:
    1. Lowest comparable landed cost among feasible candidates
    2. Shortest delivery duration among feasible candidates
    3. Lowest comparable cost subject to a delivery deadline
    
    Rules:
    - Never rank incomplete/incomparable costs as known costs.
    - Do not claim global optimality if costs are incomplete.
    """
    feasible_candidates = [c for c in evaluated_candidates if c["is_supported_combination"] and c["is_transit_feasible"]]
    infeasible_candidates = [c for c in evaluated_candidates if not (c["is_supported_combination"] and c["is_transit_feasible"])]

    # Candidates with verified complete costs
    feasible_with_cost = [c for c in feasible_candidates if c["is_cost_known"]]

    # 1. Ranking by Shortest Transit Duration (All feasible candidates can be ranked by duration)
    ranked_by_duration = sorted(feasible_candidates, key=lambda x: x["transit_days"]) if feasible_candidates else []

    # 2. Ranking by Lowest Landed Cost (Only feasible candidates with known, complete costs)
    ranked_by_cost = sorted(feasible_with_cost, key=lambda x: x["landed_cost_usd"]) if feasible_with_cost else []

    # Recommendations
    recommendations = {
        "lowest_cost_option": None,
        "lowest_cost_reason": None,
        "fastest_delivery_option": None,
        "fastest_delivery_reason": None,
        "deadline_compliant_lowest_cost": None,
        "deadline_compliant_reason": None,
        "is_global_optimality_claimable": False,
        "optimality_disclaimer": None
    }

    # Evaluate Fastest Delivery
    if ranked_by_duration:
        fastest = ranked_by_duration[0]
        recommendations["fastest_delivery_option"] = fastest
        recommendations["fastest_delivery_reason"] = (
            f"Shortest transit duration of {fastest['transit_days']:.1f} days via {fastest['scenario_name']} "
            f"({fastest['sailing_days']:.1f}d sailing + {fastest['port_allowance_days']:.1f}d port allowance)."
        )

    # Evaluate Lowest Cost Option
    if ranked_by_cost:
        cheapest = ranked_by_cost[0]
        recommendations["lowest_cost_option"] = cheapest
        recommendations["lowest_cost_reason"] = (
            f"Lowest comparable landed cost of ${cheapest['landed_cost_usd']:,.2f} USD "
            f"(${cheapest['landed_cost_per_mt_usd']:,.2f}/MT) among all feasible candidates with complete pricing."
        )

        # Global Optimality Check:
        # Optimality is local to evaluated candidates with verified complete costs.
        # It CANNOT be claimed globally if any candidate has unknown costs or if other routes/tariffs were excluded.
        all_feasible_have_cost = (len(feasible_candidates) == len(feasible_with_cost))
        recommendations["is_global_optimality_claimable"] = all_feasible_have_cost
        if not all_feasible_have_cost:
            unpriced_count = len(feasible_candidates) - len(feasible_with_cost)
            recommendations["optimality_disclaimer"] = (
                f"NOTICE: {unpriced_count} feasible candidate(s) lack monetary ocean freight or required tariff inputs, "
                "so their landed costs cannot be ranked. This recommendation is optimal ONLY among candidates with complete cost data."
            )
        else:
            recommendations["optimality_disclaimer"] = (
                "Recommendation is optimal within the evaluated candidate scenarios under supplied freight rates and port tariffs. "
                "It excludes unmodeled commercial factors such as import duties and dynamic demurrage."
            )
    else:
        recommendations["lowest_cost_reason"] = (
            "No lowest-cost option could be determined because none of the feasible candidates "
            "have a complete monetary cost estimate (missing freight rates or port inputs)."
        )

    # Evaluate Deadline-Compliant Lowest Cost
    if requested_delivery_days is not None:
        if ranked_by_cost:
            # Candidates that are both within deadline and have complete cost
            deadline_and_cost = [c for c in ranked_by_cost if c["transit_days"] <= requested_delivery_days]
            if deadline_and_cost:
                best_deadline = deadline_and_cost[0]
                recommendations["deadline_compliant_lowest_cost"] = best_deadline
                recommendations["deadline_compliant_reason"] = (
                    f"Meets requested deadline ({requested_delivery_days} days) with transit duration of "
                    f"{best_deadline['transit_days']:.1f} days at lowest landed cost of ${best_deadline['landed_cost_usd']:,.2f} USD."
                )
            else:
                recommendations["deadline_compliant_reason"] = (
                    f"No candidate meets the requested delivery deadline of {requested_delivery_days} days "
                    "with a complete cost calculation."
                )
        else:
            recommendations["deadline_compliant_reason"] = (
                "Cannot determine deadline-compliant lowest cost because monetary freight rates are missing."
            )

    return {
        "all_candidates": evaluated_candidates,
        "feasible_candidates": feasible_candidates,
        "infeasible_candidates": infeasible_candidates,
        "ranked_by_cost": ranked_by_cost,
        "ranked_by_duration": ranked_by_duration,
        "recommendations": recommendations,
        "total_evaluated": len(evaluated_candidates),
        "total_feasible": len(feasible_candidates),
        "total_with_complete_cost": len(feasible_with_cost)
    }
