import sys
from pathlib import Path
import datetime

import streamlit as st
import pandas as pd

# Add src directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from transit_time_engine import (
    load_route_vessel_specs,
    get_available_routes,
    get_available_vessels_for_route
)
from commodity_price_engine import (
    load_commodity_prices,
    get_supported_commodities
)
from port_charges_engine import list_available_tariff_categories
from landed_cost_engine import calculate_landed_cost
from scenario_engine import evaluate_scenario_candidates


def main():
    st.set_page_config(
        page_title="Intelligent Freight & Landed Cost Forecast",
        page_icon="🚢",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🚢 Intelligent Freight & Landed Cost Forecast Engine")
    st.markdown(
        "Estimate bulk-cargo commodity purchase value, ocean freight, port charges, transit duration, "
        "and delivery feasibility for overseas dry-bulk imports."
    )

    # Cache heavy dataset loads
    @st.cache_data
    def fetch_specs():
        return load_route_vessel_specs()

    @st.cache_data
    def fetch_commodities():
        return get_supported_commodities()

    try:
        specs_df = fetch_specs()
        commodities = fetch_commodities()
        available_routes = get_available_routes(specs_df)
    except Exception as e:
        st.error(f"Failed to load engine datasets: {e}")
        return

    # -------------------------------------------------------------------------
    # SIDEBAR: SHIPMENT INPUTS
    # -------------------------------------------------------------------------
    st.sidebar.header("📋 Shipment & Voyage Parameters")

    # Commodity
    default_comm_idx = commodities.index("Coal, Australian") if "Coal, Australian" in commodities else 0
    selected_commodity = st.sidebar.selectbox(
        "Commodity",
        options=commodities,
        index=default_comm_idx,
        help="Select dry-bulk commodity from World Bank Pink Sheet benchmark dataset."
    )

    # Route: Origin & Destination
    route_options = [f"{o} -> {d}" for o, d in available_routes]
    selected_route_str = st.sidebar.selectbox(
        "Origin -> Destination Route",
        options=route_options,
        index=3 if "Newcastle -> Paradip" in route_options else 0
    )
    origin_name, dest_name = [s.strip() for s in selected_route_str.split("->")]

    # Vessel Type (Filtered by route)
    avail_vessels = get_available_vessels_for_route(origin_name, dest_name, specs_df)
    selected_vessel = st.sidebar.selectbox(
        "Vessel Class",
        options=avail_vessels,
        help="Vessel classes supported for the selected route."
    )

    # Quantity in MT
    cargo_quantity_mt = st.sidebar.number_input(
        "Cargo Quantity (Metric Tonnes)",
        min_value=1.0,
        value=50000.0,
        step=5000.0,
        help="Total shipment cargo volume in metric tonnes."
    )

    # Shipment Date
    planned_date = st.sidebar.date_input(
        "Planned Shipment Date",
        value=datetime.date(2026, 5, 1),
        help="Date of planned shipment for tariff effective date verification."
    )
    planned_date_str = planned_date.strftime("%Y-%m-%d")

    # Traffic Type
    traffic_type = st.sidebar.radio(
        "Traffic Classification",
        options=["Foreign", "Coastal"],
        index=0,
        horizontal=True
    )

    # Dispatch Mode
    dispatch_mode = st.sidebar.radio(
        "Multi-vessel Dispatch Schedule",
        options=["parallel", "sequential"],
        index=0,
        horizontal=True,
        help="Parallel: All loads sail simultaneously. Sequential: Loads sail back-to-back."
    )

    # User Annual Throughput
    user_annual_throughput = st.sidebar.number_input(
        "Annual User Throughput (MT/year)",
        min_value=0.0,
        value=400000.0,
        step=50000.0,
        help="Required to evaluate volume-based wharfage tariff slabs."
    )
    user_throughput_val = user_annual_throughput if user_annual_throughput > 0 else None

    st.sidebar.markdown("---")
    st.sidebar.header("💵 Pricing & Commercial Inputs")

    # Ocean Freight Pricing Method
    freight_method = st.sidebar.radio(
        "Ocean Freight Rate Method",
        options=["USD/MT", "USD/day (Charter)"],
        index=0,
        help="Supply explicit monetary ocean freight rate."
    )

    usd_per_mt_val = None
    charter_usd_day_val = None
    bunker_price_val = None
    extra_charter_days_val = 0.0

    if freight_method == "USD/MT":
        usd_per_mt_input = st.sidebar.number_input(
            "Ocean Freight Rate (USD/MT)",
            min_value=0.0,
            value=25.50,
            step=1.0,
            help="User-supplied monetary freight rate per metric tonne."
        )
        usd_per_mt_val = usd_per_mt_input if usd_per_mt_input > 0 else None
    else:
        charter_usd_day_input = st.sidebar.number_input(
            "Time-Charter Rate (USD/day)",
            min_value=0.0,
            value=15000.0,
            step=500.0
        )
        charter_usd_day_val = charter_usd_day_input if charter_usd_day_input > 0 else None
        
        bunker_price_input = st.sidebar.number_input(
            "Bunker Fuel Price (USD/MT Fuel)",
            min_value=0.0,
            value=600.0,
            step=10.0
        )
        bunker_price_val = bunker_price_input if bunker_price_input > 0 else None
        
        extra_charter_days_val = st.sidebar.number_input(
            "Additional Charter Days",
            min_value=0.0,
            value=0.0,
            step=0.5
        )

    # USD/INR Exchange Rate
    usd_to_inr_input = st.sidebar.number_input(
        "USD to INR Exchange Rate",
        min_value=0.0,
        value=83.50,
        step=0.10,
        help="Explicit exchange rate required to unify INR port charges with USD costs."
    )
    usd_to_inr_val = usd_to_inr_input if usd_to_inr_input > 0 else None

    # Delivery Deadline & Operational Allowances
    st.sidebar.markdown("---")
    st.sidebar.header("⏱️ Transit & Port Operations")
    
    has_deadline = st.sidebar.checkbox("Specify Delivery Deadline", value=False)
    requested_days_val = None
    if has_deadline:
        requested_days_val = st.sidebar.number_input(
            "Target Delivery Days",
            min_value=1.0,
            value=25.0,
            step=1.0
        )

    port_allowance = st.sidebar.number_input("Port Operations Allowance (Days)", min_value=0.0, value=4.0, step=0.5)
    delay_margin = st.sidebar.number_input("Sea Delay Margin (%)", min_value=0.0, value=0.0, step=1.0)

    # Vessel & Port Stay Specs
    st.sidebar.markdown("---")
    st.sidebar.header("🚢 Vessel GT & Storage Inputs")
    vessel_gt_input = st.sidebar.number_input("Vessel Gross Tonnage (GT)", min_value=0.0, value=70000.0, step=1000.0)
    vessel_gt_val = vessel_gt_input if vessel_gt_input > 0 else None

    port_stay_input = st.sidebar.number_input("Port Stay Duration (Hours)", min_value=0.0, value=48.0, step=6.0)
    port_stay_val = port_stay_input if port_stay_input > 0 else None

    storage_days_input = st.sidebar.number_input("Total Port Storage (Days)", min_value=0.0, value=0.0, step=1.0)
    total_storage_val = storage_days_input if storage_days_input > 0 else None

    free_storage_input = st.sidebar.number_input("Free Storage Allowance (Days)", min_value=0.0, value=0.0, step=1.0)
    free_storage_val = free_storage_input if storage_days_input > 0 else None

    # Select Port Services
    all_port_categories = list_available_tariff_categories()["categories"]["standard_cargo_per_mt"]
    default_service_keys = ["wharfage", "mchp_unloading", "mchp_shipment", "environmental", "stevedoring", "weighment", "railway", "berth_hire"]
    
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Port Services Included")
    include_berth_hire = st.sidebar.checkbox("Vessel Berth Hire", value=True)
    selected_services_list = ["wharfage", "mchp_unloading", "mchp_shipment", "environmental", "stevedoring", "weighment", "railway"]
    if include_berth_hire:
        selected_services_list.append("berth_hire")

    # -------------------------------------------------------------------------
    # MAIN BODY CALCULATIONS
    # -------------------------------------------------------------------------
    if st.button("🚀 Calculate Shipment Estimate", type="primary", use_container_width=True):
        try:
            res = calculate_landed_cost(
                commodity=selected_commodity,
                quantity_mt=cargo_quantity_mt,
                origin=origin_name,
                destination=dest_name,
                vessel_type=selected_vessel,
                traffic_type=traffic_type,
                planned_shipment_date=planned_date_str,
                user_annual_throughput_mt=user_throughput_val,
                requested_delivery_days=requested_days_val,
                port_allowance_days=port_allowance,
                delay_margin_pct=delay_margin,
                dispatch_mode=dispatch_mode,
                usd_per_mt=usd_per_mt_val,
                charter_usd_per_day=charter_usd_day_val,
                bunker_fuel_price_usd_per_mt=bunker_price_val,
                extra_charter_days=extra_charter_days_val,
                vessel_gt=vessel_gt_val,
                port_stay_hours=port_stay_val,
                total_storage_days=total_storage_val,
                free_storage_days=free_storage_val,
                usd_to_inr_rate=usd_to_inr_val,
                selected_port_services=selected_services_list,
                specs_df=specs_df
            )

            st.success("Calculation completed — review the assumptions and exclusions below.")

            # Custom styling to ensure KPI metrics are clearly legible, responsive, and avoid clipping
            st.markdown(
                """
                <style>
                [data-testid="stMetricValue"] {
                    font-size: 1.55rem !important;
                    font-weight: 700 !important;
                    white-space: normal !important;
                    word-break: break-word !important;
                }
                [data-testid="stMetricLabel"] {
                    font-size: 0.95rem !important;
                    font-weight: 600 !important;
                }
                [data-testid="stMetricDelta"] {
                    font-size: 0.85rem !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            # -----------------------------------------------------------------
            # 1 & 2: IMPROVED KPI & SUMMARY SECTION (Full readable values & units)
            # -----------------------------------------------------------------
            st.markdown("### 📊 Shipment Cost & Voyage Summary")
            
            # Row 1: Primary Financial & Voyage Metrics (4 balanced columns)
            m1, m2, m3, m4 = st.columns(4)

            with m1:
                if res["landed_cost_estimate_usd"] is not None:
                    st.metric(
                        label="Estimated Landed Cost (USD)",
                        value=f"${res['landed_cost_estimate_usd']:,.2f} USD"
                    )
                else:
                    st.metric(
                        label="Partial Landed Cost (USD)",
                        value=f"${res['partial_landed_cost_usd']:,.2f} USD",
                        delta="Incomplete Scope",
                        delta_color="inverse"
                    )

            with m2:
                if res["landed_cost_estimate_inr"] is not None:
                    st.metric(
                        label="Estimated Landed Cost (INR)",
                        value=f"₹{res['landed_cost_estimate_inr']:,.2f} INR",
                        delta=f"@ ₹{usd_to_inr_val:,.2f}/USD" if usd_to_inr_val else None,
                        delta_color="off"
                    )
                else:
                    st.metric(
                        label="Port Charges Total (INR)",
                        value=f"₹{res['port_charges_selected_services_total_inr']:,.2f} INR",
                        delta="Native INR Port Charges",
                        delta_color="off"
                    )

            with m3:
                if res["landed_cost_per_mt_usd"] is not None:
                    st.metric(
                        label="Cost per Metric Tonne",
                        value=f"${res['landed_cost_per_mt_usd']:,.2f} USD/MT",
                        delta=f"Cargo: {cargo_quantity_mt:,.0f} MT",
                        delta_color="off"
                    )
                else:
                    st.metric(
                        label="Cost per Metric Tonne",
                        value="Not Available",
                        delta="Requires complete scope",
                        delta_color="inverse"
                    )

            with m4:
                min_days = res['transit_time_summary']['min_feasible_delivery_days']
                sailing_d = res['transit_time_summary']['sailing_days']
                port_d = res['transit_time_summary']['port_allowance_days']
                st.metric(
                    label="Estimated Transit Duration",
                    value=f"{min_days:.1f} days",
                    delta=f"{sailing_d:.1f}d Sailing + {port_d:.1f}d Port",
                    delta_color="off"
                )

            # Row 2: Status & Scope Clarity Banner
            st.markdown("---")
            col_stat1, col_stat2 = st.columns(2)

            with col_stat1:
                if res["is_complete_within_scope"]:
                    st.info(
                        "**Scope Completeness:** `Complete within selected scope`\n\n"
                        "All required cost components within the declared calculation scope "
                        "(benchmark FOB commodity value, monetary ocean freight, selected port tariff services, "
                        "and USD/INR conversion) have been calculated with user-supplied inputs."
                    )
                else:
                    st.warning(
                        "**Scope Completeness:** `Incomplete within selected scope`\n\n"
                        "One or more required components in the selected scope are missing or unresolved. "
                        "The figure above represents a partial cost estimate only."
                    )

            with col_stat2:
                if res["is_all_in_cost_known"]:
                    st.success(
                        "**All-In Cost Status:** `All-in procurement cost known`\n\n"
                        "All applicable commercial and operational cost categories (port tariffs, berth hire, "
                        "custom inland freight, and marine cargo insurance) are accounted for."
                    )
                else:
                    st.error(
                        "**All-In Cost Status:** `All-in cost not fully known`\n\n"
                        "Excluded cost categories remain (e.g., import customs duties, national taxes/GST, inland transport beyond port, "
                        "cargo insurance, or vessel demurrage). Do not treat this estimate as a final commercial procurement quote."
                    )

            st.markdown("---")

            # -----------------------------------------------------------------
            # 5: DETAILED BREAKDOWN TABS
            # -----------------------------------------------------------------
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "🚢 Transit & Voyage Feasibility",
                "💰 Commodity Value",
                "⚓ Ocean Freight",
                "🏗️ Port Tariff Breakdown",
                "📋 Scope, Notices & Disclaimers",
                "🔄 Scenario Comparison & Optimization"
            ])

            # Tab 1: Transit Feasibility
            with tab1:
                st.subheader("Transit & Voyage Feasibility Breakdown")
                tt = res["engine_breakdowns"]["transit_time"]
                
                if requested_days_val is not None:
                    if tt["is_feasible"]:
                        st.success(f"✅ FEASIBLE: {tt['delivery_status_explanation']}")
                    else:
                        st.error(f"❌ INFEASIBLE: {tt['delivery_status_explanation']}")
                else:
                    st.info(f"ℹ️ {tt['delivery_status_explanation']}")

                t_col1, t_col2 = st.columns(2)
                with t_col1:
                    st.write(f"**Origin Port:** {tt['origin']}")
                    st.write(f"**Destination Port:** {tt['destination']}")
                    st.write(f"**Vessel Class:** {tt['vessel_type']}")
                    st.write(f"**Nautical Distance:** {tt['distance_nm']:,} NM")
                    st.write(f"**Benchmark Speed:** {tt['speed_knots']} Knots")
                with t_col2:
                    st.write(f"**Pure Sailing Days:** {tt['pure_sailing_days']} days")
                    st.write(f"**Adjusted Sailing Days ({delay_margin}% delay margin):** {tt['adjusted_sailing_days']} days")
                    st.write(f"**Port Allowance Days:** {tt['port_allowance_days']} days")
                    st.write(f"**Estimated Transit Duration:** {tt['min_feasible_delivery_days']} days")
                    st.write(f"**Cargo Loads Required:** {tt['loads_required']} load(s) ({dispatch_mode} dispatch)")

                with st.expander("Voyage & Scheduling Assumptions"):
                    for a in tt["assumptions"]:
                        st.write(f"- {a}")

            # Tab 2: Commodity Value
            with tab2:
                st.subheader("Commodity FOB Purchase Value Breakdown")
                cp = res["engine_breakdowns"]["commodity_price"]
                
                st.write(f"**Selected Commodity:** {cp['commodity']}")
                st.write(f"**Latest Price Record Date:** {cp['price_date']}")
                st.write(f"**Recorded Benchmark Price:** ${cp['latest_price']:,.2f} {cp['recorded_unit']}")
                st.write(f"**Converted USD/MT Price:** ${cp['price_per_mt_usd']:,.2f} USD/MT")
                st.write(f"**Total Cargo Quantity:** {cp['quantity_mt']:,.2f} MT")
                
                if res["is_commodity_value_available"]:
                    st.metric("Estimated FOB Commodity Value", f"${res['commodity_value_usd']:,.2f} USD")
                else:
                    st.error(f"Commodity value unavailable: {cp['calculation_notes']}")

            # Tab 3: Ocean Freight
            with tab3:
                st.subheader("Ocean Freight Transport Expense")
                of = res["engine_breakdowns"]["ocean_freight"]
                
                st.write(f"**Pricing Method Used:** `{res['ocean_freight_pricing_method']}`")
                st.write(f"**Freight Provenance:** {res['ocean_freight_provenance']}")
                
                if res["is_ocean_freight_available"]:
                    st.metric("Total Ocean Freight Expense", f"${res['ocean_freight_cost_usd']:,.2f} USD")
                    st.table(pd.DataFrame(of["itemized_costs"]))
                else:
                    st.error("Ocean freight estimate unavailable. Supply an explicit USD/MT or USD/day rate.")

            # Tab 4: Port Charges & Storage Explanations
            with tab4:
                st.subheader("Rule-Based Paradip Port Charges Breakdown")
                pc = res["engine_breakdowns"]["port_charges"]
                
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    st.metric("Port Charges Total (INR)", f"₹{pc['selected_services_total_inr']:,.2f} INR")
                with p_col2:
                    st.metric("Port Charges Total (USD Direct)", f"${pc['selected_services_total_usd']:,.2f} USD")

                # Itemized Charges Table
                if pc["calculated_charges"]:
                    st.markdown("#### Itemized Calculated Charges")
                    df_calc = pd.DataFrame(pc["calculated_charges"])
                    st.dataframe(
                        df_calc[["service", "tariff_source", "rate", "unit", "basis", "currency", "charge_amount", "formula"]],
                        use_container_width=True
                    )

                # Requirement 4: Improved Port Storage & Demurrage Explanations
                st.markdown("#### 📦 Port Storage & Demurrage Assessment")
                if total_storage_val is not None and free_storage_val is not None:
                    if total_storage_val <= free_storage_val:
                        st.info(
                            f"ℹ️ **Storage Demurrage Status:** No cargo storage demurrage is calculated for these inputs "
                            f"because total storage days ({total_storage_val:.1f} days) do not exceed the explicitly supplied "
                            f"free-storage allowance ({free_storage_val:.1f} days). "
                            "Note: This assessment applies solely to cargo transit storage under the supplied parameters; "
                            "it does not assume that this free allowance applies universally across all port terminals or storage contracts, "
                            "nor does it rule out vessel charter demurrage."
                        )
                    else:
                        st.warning(
                            f"⚠️ **Storage Demurrage Accrued:** Cargo storage duration ({total_storage_val:.1f} days) exceeds "
                            f"the free-storage allowance ({free_storage_val:.1f} days) by {total_storage_val - free_storage_val:.1f} chargeable days. "
                            "Tiered demurrage has been applied according to Paradip Port Scale of Rates Section 2.10."
                        )
                elif total_storage_val is not None and free_storage_val is None:
                    st.warning(
                        "⚠️ **Free Storage Allowance Missing:** Total storage days were provided, but free_storage_days was omitted. "
                        "Because free storage periods depend on specific terminal agreements and cargo types, demurrage cannot be calculated."
                    )
                else:
                    st.write(
                        "_Cargo storage demurrage was not calculated because storage duration inputs were not specified._"
                    )

            # Tab 5: Scope, Notices & Disclaimers
            with tab5:
                st.subheader("Calculation Scope & Disclaimers")
                
                sc_col1, sc_col2 = st.columns(2)
                with sc_col1:
                    st.write("### ✅ Explicitly Included in Calculation")
                    for inc in res["scope_summary"]["included"]:
                        st.write(f"- {inc}")
                with sc_col2:
                    st.write("### ❌ Explicitly Excluded from Calculation")
                    for exc in res["scope_summary"]["excluded"]:
                        st.write(f"- {exc}")

                if res["missing_components"]:
                    st.markdown("### ⚠️ Missing / Unresolved Components")
                    for mc in res["missing_components"]:
                        st.warning(f"- {mc}")

                # Port Engine Verification Notices
                if pc["requires_verification"]:
                    st.markdown("### 🔍 Tariff Verification Notices")
                    for v in pc["requires_verification"]:
                        st.info(f"- **{v['service']} ({v['rule']}):** {v['issue']}")

                # Port Engine Excluded Services
                if pc["excluded_charges"]:
                    st.markdown("### 🚫 Inapplicable Port Services for This Cargo")
                    for ex in pc["excluded_charges"]:
                        st.caption(f"- **{ex['service']}:** {ex['reason']}")

                st.info(f"**Official Disclaimer:** {res['disclaimer']}")

            # Tab 6: Scenario Comparison & Optimization
            with tab6:
                st.subheader("🔄 Multi-Scenario Route & Vessel Evaluation")
                st.markdown(
                    "Evaluate alternative candidate routes and vessel classes for the selected cargo and destination. "
                    "Compare transit duration, voyage feasibility, and estimated landed costs side-by-side."
                )

                # Run scenario engine with filter_destination set to the user's destination
                scen_eval = evaluate_scenario_candidates(
                    commodity=selected_commodity,
                    quantity_mt=cargo_quantity_mt,
                    filter_destination=dest_name,
                    traffic_type=traffic_type,
                    planned_shipment_date=planned_date_str,
                    user_annual_throughput_mt=user_throughput_val,
                    requested_delivery_days=requested_days_val,
                    port_allowance_days=port_allowance,
                    delay_margin_pct=delay_margin,
                    dispatch_mode=dispatch_mode,
                    default_usd_per_mt=usd_per_mt_val,
                    default_charter_usd_per_day=charter_usd_day_val,
                    bunker_fuel_price_usd_per_mt=bunker_price_val,
                    vessel_gt=vessel_gt_val,
                    port_stay_hours=port_stay_val,
                    total_storage_days=total_storage_val,
                    free_storage_days=free_storage_val,
                    usd_to_inr_rate=usd_to_inr_val,
                    selected_port_services=selected_services_list,
                    specs_df=specs_df
                )

                recs = scen_eval["recommendations"]

                # Recommendations Row
                r_col1, r_col2 = st.columns(2)

                with r_col1:
                    st.markdown("#### 🏆 Optimal Candidates")
                    if recs["lowest_cost_option"]:
                        best_cost = recs["lowest_cost_option"]
                        st.success(
                            f"**Lowest Comparable Landed Cost:**\n\n"
                            f"**{best_cost['scenario_name']}** — **${best_cost['landed_cost_usd']:,.2f} USD** "
                            f"(${best_cost['landed_cost_per_mt_usd']:,.2f}/MT) in {best_cost['transit_days']:.1f} days.\n\n"
                            f"_{recs['lowest_cost_reason']}_"
                        )
                    else:
                        st.warning(f"**Lowest Cost:** {recs['lowest_cost_reason']}")

                    if recs["fastest_delivery_option"]:
                        fastest = recs["fastest_delivery_option"]
                        cost_str = f"${fastest['landed_cost_usd']:,.2f} USD" if fastest['landed_cost_usd'] else "Price uncalculated"
                        st.info(
                            f"**Shortest Delivery Duration:**\n\n"
                            f"**{fastest['scenario_name']}** — **{fastest['transit_days']:.1f} days** "
                            f"({cost_str}).\n\n"
                            f"_{recs['fastest_delivery_reason']}_"
                        )

                with r_col2:
                    st.markdown("#### 🎯 Deadline Compliance")
                    if requested_days_val is not None:
                        if recs["deadline_compliant_lowest_cost"]:
                            dl = recs["deadline_compliant_lowest_cost"]
                            st.success(
                                f"**Lowest Cost within Deadline ({requested_days_val} days):**\n\n"
                                f"**{dl['scenario_name']}** — **${dl['landed_cost_usd']:,.2f} USD** "
                                f"in {dl['transit_days']:.1f} days."
                            )
                        else:
                            st.error(
                                f"**Deadline Status:** {recs['deadline_compliant_reason']}"
                            )
                    else:
                        st.info(
                            "Specify a **Target Delivery Days** deadline in the sidebar to view "
                            "deadline-compliant optimization."
                        )

                    # Global Optimality Disclaimer
                    if recs["optimality_disclaimer"]:
                        st.caption(f"_{recs['optimality_disclaimer']}_")

                # Comparison Table
                st.markdown("#### 📋 Candidate Scenarios Comparison Table")
                table_rows = []
                for c in scen_eval["all_candidates"]:
                    table_rows.append({
                        "Scenario": c["scenario_name"],
                        "Feasible?": "✅ Yes" if c["is_transit_feasible"] else "❌ Infeasible",
                        "Transit (Days)": f"{c['transit_days']:.1f}" if c["transit_days"] else "N/A",
                        "Loads": c["loads_required"] if c["loads_required"] else "N/A",
                        "Landed Cost (USD)": f"${c['landed_cost_usd']:,.2f}" if c["landed_cost_usd"] else "Unpriced",
                        "Cost / MT (USD)": f"${c['landed_cost_per_mt_usd']:,.2f}" if c["landed_cost_per_mt_usd"] else "N/A",
                        "Cost Complete?": "✅ Complete" if c["is_cost_known"] else "⚠️ Incomplete",
                        "Status / Reason": c["rejection_reason"] if c["rejection_reason"] else "Feasible & Calculated"
                    })

                df_scen = pd.DataFrame(table_rows)
                st.dataframe(df_scen, use_container_width=True)

                # Rejected / Infeasible Options Section
                if scen_eval["infeasible_candidates"]:
                    with st.expander(f"🚫 Rejected / Infeasible Options ({len(scen_eval['infeasible_candidates'])})"):
                        for inf in scen_eval["infeasible_candidates"]:
                            st.write(f"- **{inf['scenario_name']}:** {inf['rejection_reason']}")

                # Transparency Note
                st.caption(
                    "Note: Incomplete candidates are excluded from cost ranking to prevent misleading comparisons. "
                    "BDI points are never converted into monetary rates."
                )

        except Exception as err:
            st.error(f"Calculation Error: {err}")

    else:
        st.info("👈 Set your shipment parameters in the sidebar and click **Calculate Shipment Estimate** to run the landed cost engine.")


if __name__ == "__main__":
    main()
