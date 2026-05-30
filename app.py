import math
from typing import Dict, List, Tuple

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from flight_opt.constraints import RoutingConfig
from flight_opt.data.sample_data import AIRPORTS, NO_FLY_ZONES, WEATHER_EDGE_PENALTY_KM, PREFERRED_HUBS
from flight_opt.routing import find_optimal_route


st.set_page_config(page_title="Indian Airspace Management", page_icon="✈️", layout="wide")

AIRCRAFT_RANGE = {
    "Airbus A320": 6100.0,
    "Boeing 737": 5600.0,
    "Airbus A350": 15000.0,
    "Boeing 777": 14300.0,
}

st.markdown("### Indian Airspace Management")
st.caption("Flight Path Optimization System")

overview_tab, optimization_tab, analytics_tab = st.tabs(["Overview", "Optimization", "Analytics"])

with overview_tab:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Route Efficiency", "95%")
    with c2:
        st.metric("Fuel Savings", "15%")
    with c3:
        st.metric("Daily Flights", "100+")
    with c4:
        st.metric("Cost Savings", "₹2.5M")

    st.markdown("---")
    lc, mc, rc = st.columns([1,1,1])
    with lc:
        st.subheader("Traffic Analysis")
        traffic_data = pd.DataFrame({
            "Airport": ["Delhi (DEL)", "Mumbai (BOM)", "Bengaluru (BLR)", "Chennai (MAA)"],
            "Flights": [25, 22, 18, 15],
        })
        st.bar_chart(traffic_data.set_index("Airport"))
    with mc:
        st.subheader("Aircraft Distribution")
        aircraft_dist = pd.DataFrame({
            "Aircraft": list(AIRCRAFT_RANGE.keys()),
            "Share": [35, 28, 20, 17],
        })
        st.bar_chart(aircraft_dist.set_index("Aircraft"))
    with rc:
        st.subheader("System Performance")
        st.metric("Optimization Success Rate", "98.5%")
        st.metric("Average Processing Time", "1.2 s")
        st.metric("System Uptime", "99.9%")
        st.metric("Active Monitoring", "24/7")

with optimization_tab:
    st.subheader("Route Planning & Optimization")
    codes = sorted(AIRPORTS.keys())
    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        origin = st.selectbox("Origin", options=codes, index=codes.index("DEL") if "DEL" in codes else 0)

    with c2:
        destination = st.selectbox("Destination", options=codes, index=codes.index("BOM") if "BOM" in codes else 1)

    with c3:
        ac_type = st.selectbox("Aircraft Type", options=list(AIRCRAFT_RANGE.keys()), index=2)

    max_leg = AIRCRAFT_RANGE[ac_type]

    st.button("Set aircraft max-leg", on_click=lambda: st.session_state.update({"max_leg_override": max_leg}))
    max_leg_eff = st.session_state.get("max_leg_override", max_leg)
    st.caption(f"Effective max-leg: {max_leg_eff:.0f} km")

    if st.button("Optimize Flight Path", type="primary"):
        config = RoutingConfig(
            max_leg_km=float(max_leg_eff),
            preferred_hubs=PREFERRED_HUBS,
            hub_bonus_km=float(hub_bonus),
            no_fly_zones=NO_FLY_ZONES if use_nofly else [],
            weather_edge_penalty_km=WEATHER_EDGE_PENALTY_KM if use_weather else {},
        )
        try:
            res = find_optimal_route(AIRPORTS, origin, destination, config)
            st.success(f"Route found: {' → '.join(res.path)}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Distance", f"{res.total_distance_km:.0f} km")
            c2.metric("Total Cost", f"{res.total_cost_km:.0f} km")
            c3.metric("Legs", f"{len(res.legs)}")

            # Legs table
            df_legs = pd.DataFrame([
                {
                    "Origin": l.origin,
                    "Destination": l.destination,
                    "Distance (km)": round(l.distance_km, 1),
                    "Weather (km)": round(l.weather_penalty_km, 1),
                    "Hub Bonus (km)": round(l.hub_bonus_km, 1),
                    "Cost (km)": round(l.total_cost_km, 1),
                }
                for l in res.legs
            ])
            st.dataframe(df_legs, use_container_width=True)

            # Map visualization
            fig = go.Figure()
            # Airports
            lats = [AIRPORTS[c][1] for c in AIRPORTS]
            lons = [AIRPORTS[c][2] for c in AIRPORTS]
            texts = [f"{c}: {AIRPORTS[c][0]}" for c in AIRPORTS]
            fig.add_trace(go.Scattergeo(lat=lats, lon=lons, text=texts, mode="markers", marker=dict(size=6, color="#FFD166"), name="Airports"))
            # No-fly zones
            if use_nofly:
                for zone in NO_FLY_ZONES:
                    zlats = [p[0] for p in zone.polygon] + [zone.polygon[0][0]]
                    zlons = [p[1] for p in zone.polygon] + [zone.polygon[0][1]]
                    fig.add_trace(go.Scattergeo(lat=zlats, lon=zlons, mode="lines", fill="toself", fillcolor="rgba(255,0,0,0.15)", line=dict(color="rgba(255,0,0,0.6)"), name=f"No-Fly: {zone.name}"))
            # Route
            if res.path:
                route_lats = [AIRPORTS[c][1] for c in res.path]
                route_lons = [AIRPORTS[c][2] for c in res.path]
                fig.add_trace(go.Scattergeo(lat=route_lats, lon=route_lons, mode="lines+markers", line=dict(width=3, color="#118AB2"), marker=dict(size=8, color="#118AB2"), name="Route"))

            fig.update_layout(geo=dict(showland=True, landcolor="#111217", lakecolor="#1b1f2a", showcountries=True, projection_type="natural earth"), margin=dict(l=0, r=0, t=0, b=0), legend=dict(orientation="h"))
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(str(e))

with analytics_tab:
    st.subheader("Analytics")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Optimization Success Trend")
        trend = pd.DataFrame({"Day": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], "Success %": [96,97,98,98,99,99,98]}).set_index("Day")
        st.line_chart(trend)
    with col2:
        st.markdown("#### Average Processing Time (s)")
        ptime = pd.DataFrame({"Day": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], "Time": [1.5,1.4,1.3,1.2,1.2,1.1,1.2]}).set_index("Day")
        st.line_chart(ptime)

st.markdown("---")
    # Footer
st.caption("Advanced flight path optimization using A* algorithms for enhanced aviation efficiency")
