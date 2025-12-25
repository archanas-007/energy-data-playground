# Global Energy Demand Forecasting 🌍⚡

A Time Series analysis project that predicts future Global Energy Demand based on economic indicators (GDP Growth) using Statistical (VAR) and Machine Learning (XGBoost) approaches. Includes an interactive scenario planner dashboard.

## 🚀 Features

*   **Data Pipeline:** Automates fetching data from World Bank API and merging with local datasets.
*   **EDA & Stats:** Performs Stationarity checks (ADF) and Causality tests (Granger Causality).
*   **Modeling:** Compares Vector Autoregression (VAR) baseline vs. XGBoost Regressor.
*   **Dashboard:** Interactive Streamlit app for "What-If" scenario planning (e.g., "If GDP grows by 5%, what happens to Energy Demand?").

## 📂 Project Structure

*   `data_loader.py`: Ingests raw data, fetches missing features (CO2, Industry) from WDI API, and cleans the dataset.
*   `eda.py`: Runs statistical tests and generates lag features for ML.
*   `model.py`: Trains models, evaluates performance (MAPE), and saves the best model.
*   `app.py`: Streamlit application for visualization and interactive forecasting.

## 🛠️ Setup & Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/YOUR_USERNAME/energy-demand-forecast.git
    cd energy-demand-forecast
    ```

2.  **Create a Virtual Environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

    *Note for Mac Users (Apple Silicon):* You may need `libomp` for XGBoost:
    ```bash
    brew install libomp
    ```

## 🏃‍♂️ Usage Pipeline

Run the scripts in the following order to reproduce the analysis:

1.  **Load Data:**
    ```bash
    python data_loader.py
    ```
2.  **Run EDA:**
    ```bash
    python eda.py
    ```
3.  **Train Models:**
    ```bash
    python model.py
    ```
4.  **Launch Dashboard:**
    ```bash
    streamlit run app.py
    ```

## 📊 Results

*   **VAR Model MAPE:** (See output of model.py)
*   **XGBoost Model MAPE:** (See output of model.py)
*   *See `model_comparison.png` for a visual comparison of forecasts.*
