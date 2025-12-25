import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.api import VAR
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_percentage_error
import json

def train_and_evaluate():
    # Load data
    try:
        df = pd.read_csv('model_ready_data.csv')
    except FileNotFoundError:
        print("Error: model_ready_data.csv not found.")
        return

    # Filter for 'World'
    df_world = df[df['Country Name'] == 'World'].copy()
    if df_world.empty:
        print("Error: 'World' data not found.")
        return

    # Ensure Year is sorted
    df_world = df_world.sort_values('Year')

    # --- 1. Data Splitting ---
    # Train: 1990-2015, Test: 2016-2019
    train = df_world[(df_world['Year'] >= 1990) & (df_world['Year'] <= 2015)]
    test = df_world[(df_world['Year'] >= 2016) & (df_world['Year'] <= 2019)]

    print(f"Train shape: {train.shape}, Test shape: {test.shape}")
    
    if len(train) == 0 or len(test) == 0:
        print("Error: Train or Test set is empty. Check Year column.")
        return

    # --- 2. Model A: VAR ---
    print("\nTraining VAR Model...")
    # Features for VAR
    var_cols = ['GDP_Growth', 'Energy_Use']
    train_var = train[var_cols]
    
    # Fit VAR
    # We suppress statsmodels warnings if any
    try:
        model_var = VAR(train_var)
        # We let statsmodels select the best lag order based on AIC, maxlags=3 (small sample)
        var_result = model_var.fit(maxlags=3, ic='aic')
        
        # Forecast
        # We need the last k values from train to predict forward
        lag_order = var_result.k_ar
        print(f"VAR Selected Lag Order: {lag_order}")
        
        var_forecast_input = train_var.values[-lag_order:]
        var_pred_values = var_result.forecast(y=var_forecast_input, steps=len(test))
        
        # Extract Energy_Use prediction (it's the 2nd column in var_cols)
        # var_pred_values has shape (steps, features)
        idx_energy = var_cols.index('Energy_Use')
        var_preds = var_pred_values[:, idx_energy]
        
    except Exception as e:
        print(f"VAR Model failed: {e}")
        var_preds = np.zeros(len(test))

    # --- 3. Model B: XGBoost ---
    print("\nTraining XGBoost Model...")
    # Features and Target
    # Removed 'CO2_Emissions' as it dominates importance (98%) and masks GDP effects.
    features = ['GDP_Lag_1', 'GDP_Lag_2', 'Industry_Value_Added']
    target = 'Energy_Use'
    
    X_train = train[features]
    y_train = train[target]
    X_test = test[features]
    y_test = test[target]
    
    # Initialize and Train
    xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    xgb_model.fit(X_train, y_train)
    
    # Predict
    xgb_preds = xgb_model.predict(X_test)
    
    # Save Model
    xgb_model.get_booster().save_model("xgb_model.json")
    print("XGBoost model saved to xgb_model.json")

    # --- 4. Evaluation & Visualization ---
    print("\nEvaluation Results:")
    actuals = y_test.values
    
    # Calculate MAPE
    mape_var = mean_absolute_percentage_error(actuals, var_preds)
    mape_xgb = mean_absolute_percentage_error(actuals, xgb_preds)
    
    print(f"MAPE (VAR): {mape_var:.4f}")
    print(f"MAPE (XGBoost): {mape_xgb:.4f}")
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(test['Year'], actuals, label='Actual Energy Use', marker='o', color='black')
    plt.plot(test['Year'], var_preds, label=f'VAR Prediction (MAPE={mape_var:.2f})', linestyle='--', marker='x')
    plt.plot(test['Year'], xgb_preds, label=f'XGBoost Prediction (MAPE={mape_xgb:.2f})', linestyle='-.', marker='s')
    
    plt.title('Forecasting Comparison: VAR vs XGBoost (World)')
    plt.xlabel('Year')
    plt.ylabel('Energy Use')
    plt.legend()
    plt.grid(True)
    
    plot_file = 'model_comparison.png'
    plt.savefig(plot_file)
    print(f"Comparison plot saved to {plot_file}")

if __name__ == "__main__":
    train_and_evaluate()
