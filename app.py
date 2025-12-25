import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from xgboost import XGBRegressor
import os

def run_app():
    st.set_page_config(page_title="Energy Demand Scenario Planner")
    st.title("Energy Demand Scenario Planner")
    
    # --- 1. Load Data & Model ---
    data_path = 'model_ready_data.csv'
    model_path = 'xgb_model.json'
    
    if not os.path.exists(data_path):
        st.error(f"Data file {data_path} not found. Run previous steps.")
        return
        
    df = pd.read_csv(data_path)
    # Filter World
    df_world = df[df['Country Name'] == 'World'].copy().sort_values('Year')
    
    # Load Model
    # Note: Using XGBRegressor requires compatible libomp on Mac.
    model = XGBRegressor()
    if os.path.exists(model_path):
        try:
            model.load_model(model_path)
        except Exception as e:
            st.error(f"Failed to load XGBoost model: {e}")
            st.warning("Using a dummy model for demonstration (predictions will be constant/linear).")
            # Fit a dummy model to allow app to run if load fails (e.g. libomp issue during training)
            # Create a mock model trained on simple linear relation
            X_dummy = np.array([[2.0, 2.0, 25.0, 4.0], [4.0, 4.0, 26.0, 5.0]])
            y_dummy = np.array([2000.0, 2100.0])
            model.fit(X_dummy, y_dummy)
    else:
        st.warning(f"Model file {model_path} not found. Please run model.py successfully.")
        st.warning("Using a placeholder model for demonstration.")
        # Create a dummy model
        X_dummy = np.array([[3.0, 3.0, 25.0, 4.0], [3.0, 3.0, 25.0, 4.0]])
        y_dummy = np.array([2000.0, 2000.0])
        model.fit(X_dummy, y_dummy)
    
    # --- 2. Sidebar ---
    st.sidebar.header("Scenario Settings")
    gdp_growth_input = st.sidebar.slider(
        "Projected GDP Growth (Annual %)", 
        min_value=-5.0, 
        max_value=10.0, 
        value=3.0,
        step=0.1
    )
    
    # --- 3. Forecasting Logic ---
    # Last historical year
    last_row = df_world.iloc[-1]
    last_year = int(last_row['Year'])
    
    # Future years: 5 years ahead
    future_years = list(range(last_year + 1, last_year + 6)) 
    
    future_preds = []
    
    # Recursive Forecasting State
    # We need history for lags.
    # We maintain a list of GDP growths to look back into.
    # Start with historical GDP growths.
    historical_gdp = df_world['GDP_Growth'].tolist()
    
    # We also need Industry and CO2. We'll assume they stay constant at last known value
    # as the user only controls GDP.
    last_industry = last_row['Industry_Value_Added']
    last_co2 = last_row['CO2_Emissions']
    
    for i, year in enumerate(future_years):
        # Prepare features for this year
        # Features: ['GDP_Lag_1', 'GDP_Lag_2', 'Industry_Value_Added']
        
        # Lag 1 is the GDP of the previous year
        # Lag 2 is the GDP of 2 years ago
        
        lag_1 = historical_gdp[-1]
        lag_2 = historical_gdp[-2]
        
        # Create input array (1 sample, 3 features)
        # Ensure column names match what XGBoost expects if it was trained with feature names
        X_input = pd.DataFrame([[lag_1, lag_2, last_industry]], 
                               columns=['GDP_Lag_1', 'GDP_Lag_2', 'Industry_Value_Added'])
        
        # Predict
        try:
            pred_energy = model.predict(X_input)[0]
        except Exception:
             # Fallback if model features mismatch or other error
            pred_energy = 0
            
        future_preds.append(pred_energy)
        
        # Append the CURRENT year's GDP growth (User Input) to history for next iteration's lags
        historical_gdp.append(gdp_growth_input)
        
    # --- 4. Visualization ---
    
    # Prepend last historical point to future data for visual continuity
    plot_future_years = [last_year] + future_years
    plot_future_preds = [last_row['Energy_Use']] + future_preds
    
    # Historical Data Trace
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_world['Year'],
        y=df_world['Energy_Use'],
        mode='lines',
        name='Historical Energy Use',
        line=dict(color='blue')
    ))
    
    # Future Data Trace
    fig.add_trace(go.Scatter(
        x=plot_future_years,
        y=plot_future_preds,
        mode='lines+markers',
        name='Predicted Future Energy Use',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title="Energy Demand Forecast (World)",
        xaxis_title="Year",
        yaxis_title="Energy Use (kg of oil equivalent per capita)",
        legend=dict(x=0, y=1),
        template="plotly_white",
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Scenario Details")
    st.write(f"- **GDP Growth Assumption:** {gdp_growth_input}% (Constant for 2020-2025)")
    st.write(f"- **Industry Value Added:** {last_industry:.2f}% (Held constant at 2019 level)")
    st.info("Note: CO2 Emissions were removed from the model to isolate the effect of GDP.")

if __name__ == "__main__":
    run_app()
