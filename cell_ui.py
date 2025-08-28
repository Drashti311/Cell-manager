import streamlit as st
import random
import pandas as pd
import time
import plotly.express as px

st.set_page_config(page_title="Cell Simulation", layout="wide")
st.title("🔋 Cell Charging & Discharging Dashboard")

# Sidebar
with st.sidebar:
    st.header("⚡ Cell Data Input")
    num_cells = st.number_input("Number of Cells", min_value=1, max_value=8, value=1)
    
    list_of_cell = []
    for i in range(num_cells):
        cell_type = st.selectbox(
            f"Cell {i+1} Type",
            ["Choose Type", "lfp", "nmc"],
            key=f"type_{i}"
        )
        list_of_cell.append(cell_type)

# Initial Data
cells_data = {}
for idx, cell_type in enumerate(list_of_cell, start=1):
    if cell_type == "Choose Type":
        continue
    
    cell_key = f"Cell {idx} ({cell_type.upper()})"
    voltage = 3.2 if cell_type == "lfp" else 3.6
    min_voltage = 2.8 if cell_type == "lfp" else 3.2
    max_voltage = 3.6 if cell_type == "lfp" else 4.0
    temp = round(random.uniform(25, 40), 1)

    cells_data[cell_key] = {
        "type": cell_type,
        "voltage": voltage,
        "current": 0.0,
        "temp": temp,
        "capacity": 0.0,
        "min_voltage": min_voltage,
        "max_voltage": max_voltage,
        "status": "Idle"
    }

# Sidebar Current Inputs
if cells_data:
    st.sidebar.subheader("Enter Current (A)")
    for key in cells_data:
        current = st.sidebar.number_input(
            f"{key}", min_value=0.0, max_value=10.0, step=0.1, key=f"curr_{key}"
        )
        v = cells_data[key]["voltage"]
        cells_data[key]["current"] = current
        cells_data[key]["capacity"] = round(v * current, 2)

# Convert to DataFrame
df = pd.DataFrame(cells_data).T

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Overview", "📊 Charts", "▶️ Start"])

# --- Tab 1: Overview ---
with tab1:
    st.subheader("Cell Data Overview")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        # CSV Export
        csv = df.to_csv().encode("utf-8")
        st.download_button("💾 Download CSV", csv, "cell_data.csv", "text/csv")
    else:
        st.info("Please select cell types to see overview.")

# --- Tab 2: Charts ---
with tab2:
    if not df.empty:
        st.subheader("📊 Charts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(
                df,
                x=df.index,
                y="capacity",
                title="Cell Capacity (Ah)",
                color="capacity",
                text_auto=True,
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.area(
                df,
                x=df.index,
                y="temp",
                title="Cell Temperature (°C)",
                markers=True,
                color=df.index
            )
            st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("No data to plot yet.")

#--- Tab 3: Simulation ---
with tab3:
    if not df.empty:
        st.subheader("Cell Simulation")

        # Cycle order
        state_cycle = ["Charging", "Idle", "Discharging", "Idle"]
        colors = {
            "Charging": "#2D662D",   
            "Discharging": "#E31919",
            "Idle": "#50B6D8"       
        }

        # Display cells in grid
        keys = list(cells_data.keys())
        rows = [keys[i:i+4] for i in range(0, len(keys), 4)]

        # placeholders arranged in grid
        cell_placeholders = {}
        for row in rows:
            cols = st.columns(4)
            for i, key in enumerate(row):
                with cols[i]:
                    cell_placeholders[key] = st.empty()

        # Start Simulation Button
        if st.button("▶️ Start Simulation for All Cells"):
            for step in range(12):  # quick cycles
                for key in keys:
                    cell = cells_data[key]
                    state = state_cycle[step % 4]
                    cell["status"] = state

                    # update the placeholder box
                    with cell_placeholders[key].container():
                        st.markdown(
                            f"""
                            <div style="border:2px solid black; border-radius:10px; 
                                        padding:10px; margin:5px; 
                                        background-color:{colors[state]};">
                                <h4>{key}</h4>
                                <b>Status:</b> {state}<br>
                                <b>Voltage:</b> {cell['voltage']} V<br>
                                <b>Current:</b> {cell['current']} A<br>
                                <b>Capacity:</b> {cell['capacity']} Ah<br>
                                <b>Temp:</b> {cell['temp']} °C
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                time.sleep(5)  
    else:
        st.info("Select cell types & inputs first to run simulation.")


