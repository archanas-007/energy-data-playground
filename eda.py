import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, grangercausalitytests

def run_eda():
    # Load dataset
    input_file = 'final_dataset.csv'
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please run data_loader.py first.")
        return

    print("Data Loaded. Shape:", df.shape)

    # --- 1. Stationarity Check (ADF Test) ---
    print("\n--- 1. Stationarity Check (ADF Test) - World Data Only ---")
    
    # Filter for 'World'
    # Check if 'World' exists in 'Country Name'
    df_world = df[df['Country Name'] == 'World'].copy()
    
    if df_world.empty:
        print("Warning: 'World' data not found. Checking available countries:", df['Country Name'].unique())
        # Fallback or exit? If World is missing, maybe use another country or just skip.
        # Assuming World exists as per previous steps.
    
    # Columns to check
    numeric_cols = ['Energy_Use', 'GDP_Growth', 'CO2_Emissions', 'Industry_Value_Added']
    
    def check_stationarity(series, name):
        # Drop NaNs for ADF
        clean_series = series.dropna()
        if len(clean_series) < 10: # Minimum samples check
            print(f"{name}: Not enough data for ADF test.")
            return

        result = adfuller(clean_series)
        p_value = result[1]
        
        status = "Stationary" if p_value <= 0.05 else "Non-Stationary (Needs Differencing)"
        print(f"{name}: p-value = {p_value:.4f} -> {status}")

    for col in numeric_cols:
        if col in df_world.columns:
            check_stationarity(df_world[col], col)
        else:
            print(f"Column {col} not found in dataset.")

    # --- 2. Granger Causality Test ---
    print("\n--- 2. Granger Causality Test (World Data) ---")
    print("Hypothesis: Does GDP_Growth predict future Energy_Use?")
    
    # Data for Granger: [Effect, Cause] -> [Energy_Use, GDP_Growth]
    # "Does GDP predict Energy?" means GDP is the lagged predictor (X), Energy is the target (Y).
    # grangercausalitytests takes a 2D array where the 0-th column is the time series to be predicted (Y),
    # and the 1-st column is the predictor (X).
    
    if 'Energy_Use' in df_world.columns and 'GDP_Growth' in df_world.columns:
        gc_data = df_world[['Energy_Use', 'GDP_Growth']].dropna()
        
        if len(gc_data) > 10:
            print(f"Running Granger Causality Test for lags 1 to 3...")
            # verbose=True prints results. We can also suppress and format manually, but verbose is requested "Print the results clearly"
            # The tool output captures stdout.
            grangercausalitytests(gc_data, maxlag=3, verbose=True)
        else:
            print("Not enough data for Granger Causality.")
    else:
        print("Required columns for Granger Causality not found.")

    # --- 3. Feature Engineering ---
    print("\n--- 3. Feature Engineering (Lag Features) ---")
    
    # Use full dataset
    df_feat = df.copy()
    
    # Sort by Country and Year to ensure lags are correct
    df_feat = df_feat.sort_values(by=['Country Name', 'Year'])
    
    # Create Lag Features
    # Group by Country to avoid lagging across country boundaries
    # shift(1) is Previous Year
    df_feat['GDP_Lag_1'] = df_feat.groupby('Country Name')['GDP_Growth'].shift(1)
    df_feat['GDP_Lag_2'] = df_feat.groupby('Country Name')['GDP_Growth'].shift(2)
    
    # Drop NaNs created by lagging
    initial_shape = df_feat.shape
    df_model_ready = df_feat.dropna()
    final_shape = df_model_ready.shape
    
    print(f"Created Lag Features. Rows before drop: {initial_shape[0]}, Rows after drop: {final_shape[0]}")
    
    # Save
    output_model_file = 'model_ready_data.csv'
    df_model_ready.to_csv(output_model_file, index=False)
    print(f"Saved model ready data to {output_model_file}")

    # --- 4. Visualization ---
    print("\n--- 4. Visualization (Correlation Heatmap) ---")
    
    # Compute correlation matrix on numerical columns
    # We include original and new lag features
    corr_cols = ['Energy_Use', 'GDP_Growth', 'CO2_Emissions', 'Industry_Value_Added', 'GDP_Lag_1', 'GDP_Lag_2']
    # Filter for existing columns
    existing_corr_cols = [c for c in corr_cols if c in df_model_ready.columns]
    
    corr_matrix = df_model_ready[existing_corr_cols].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Heatmap (including Lags)')
    plt.xticks(rotation=45, ha='right') # Rotate x labels for better fit
    plt.yticks(rotation=0) # Keep y labels horizontal
    plt.tight_layout() # Adjust layout to prevent cutting off labels
    
    heatmap_file = 'heatmap.png'
    plt.savefig(heatmap_file)
    plt.close() # Close plot to free memory
    print(f"Heatmap saved to {heatmap_file}")

if __name__ == "__main__":
    run_eda()
