import streamlit as st
from engine.queue_text import analyze_batches, rotate_generators, evaluate_ecommerce_inventory
from engine.topology_sets import SmartGridTopology, solve_survey_venn
from views.ui_components import page_heading

# Clearly-labelled demo fixture because the syllabus device table was not supplied.
DEVICES = {
    "D1": {"Name": "Smart Light", "Room": "Living Room", "Status": "ON", "kWh": 0.4},
    "D2": {"Name": "Smart TV", "Room": "Living Room", "Status": "OFF", "kWh": 1.2},
    "D3": {"Name": "Smart AC", "Room": "Bedroom", "Status": "ON", "kWh": 2.8},
    "D4": {"Name": "Smart Fan", "Room": "Bedroom", "Status": "ON", "kWh": 0.7},
    "D5": {"Name": "Smart Fridge", "Room": "Kitchen", "Status": "ON", "kWh": 3.1},
    "D6": {"Name": "Smart Oven", "Room": "Kitchen", "Status": "OFF", "kWh": 1.9},
    "D7": {"Name": "Smart Speaker", "Room": "Living Room", "Status": "ON", "kWh": 0.2},
    "D8": {"Name": "Smart Washer", "Room": "Utility", "Status": "OFF", "kWh": 1.6},
    "D9": {"Name": "Smart Heater", "Room": "Bedroom", "Status": "OFF", "kWh": 2.2},
    "D10": {"Name": "Smart Camera", "Room": "Entry", "Status": "ON", "kWh": 0.3},
}


def render():
    page_heading("network", "DISPATCH / PRACTICALS 2 & 3", "Telemetry Queue & Topology", "Explore order batches, generator rotations, device status, and survey cohorts.")
    st.caption("Order IDs and device readings below are exercise/demo data, not live telemetry.")
    queue_tab, devices_tab, survey_tab, inventory_tab = st.tabs(["Dispatch queue", "Device topology", "Survey sets", "Inventory"])

    with queue_tab:
        generators = ["Gen_1", "Gen_2", "Gen_3", "Gen_4", "Gen_5"]
        k = st.number_input("Left-rotation steps", min_value=0, value=1, step=1)
        st.write("Original order:", generators)
        st.write("Rotated order:", rotate_generators(generators, int(k)))
        if st.button("Analyze sample order batches"):
            result = analyze_batches(list(range(1, 64)), list(range(64, 130)))
            for key, value in result.items():
                st.write(f"**{key.replace('_', ' ').title()}:**", value)

    with devices_tab:
        state = st.session_state.setdefault("device_statuses", {key: value["Status"] for key, value in DEVICES.items()})
        records = {key: {**value, "Status": state[key]} for key, value in DEVICES.items()}
        topology = SmartGridTopology(records)
        st.write("Demo readings are illustrative. Replace this fixture with the exact syllabus table if required.")
        for device_id, device in records.items():
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            col1.write(device_id)
            col2.write(device["Name"])
            col3.write(device["Room"])
            chosen = col4.selectbox("Status", ["ON", "OFF"], index=["ON", "OFF"].index(state[device_id]), key=f"status_{device_id}", label_visibility="collapsed")
            if chosen != state[device_id]:
                state[device_id] = chosen
        records = {key: {**value, "Status": state[key]} for key, value in DEVICES.items()}
        topology = SmartGridTopology(records)
        c1, c2, c3 = st.columns(3)
        c1.metric("Active device energy", f"{topology.calculate_active_energy():.2f} kWh")
        peak = topology.get_max_energy_device()
        c2.metric("Highest listed device reading", peak[1]["Name"] if peak else "None", f"{peak[1]['kWh']:.2f} kWh" if peak else None)
        living = topology.filter_by_room("Living Room")
        c3.metric("Living Room devices", len(living))
        st.dataframe([{"Device ID": key, **value} for key, value in records.items()], hide_index=True, use_container_width=True)

    with survey_tab:
        results = solve_survey_venn()
        st.caption("Percentages and counts use the supplied exercise survey assumptions.")
        st.json({key: results[key] for key in ["subscribed_to_all_three", "exactly_one_scheme", "at_least_two_schemes", "solely_solar_to_solely_wind_ratio"]})

    with inventory_tab:
        qty_text = st.text_input("Quantities, comma-separated", "4,7,2")
        price_text = st.text_input("Prices, comma-separated", "10,8,25")
        if st.button("Calculate inventory metrics"):
            try:
                quantities = [float(value.strip()) for value in qty_text.split(",") if value.strip()]
                prices = [float(value.strip()) for value in price_text.split(",") if value.strip()]
                st.json(evaluate_ecommerce_inventory(quantities, prices))
            except (ValueError, TypeError) as exc:
                st.error(f"Check the comma-separated numeric inputs: {exc}")
