import os
from pathlib import Path

import pandas as pd
import wbdata
import numpy as np

def load_data():
    data_dir = os.getenv("DATA_DIR")
    if data_dir:
        file_path = Path(data_dir) / "API_EG.USE.PCAP.KG.OE_DS2_en_csv_v2_2449" / "API_EG.USE.PCAP.KG.OE_DS2_en_csv_v2_2449.csv"
    else:
        file_path = Path(__file__).resolve().parent / "API_EG.USE.PCAP.KG.OE_DS2_en_csv_v2_2449" / "API_EG.USE.PCAP.KG.OE_DS2_en_csv_v2_2449.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found at {file_path}.\nSet DATA_DIR environment variable or place the data folder next to data_loader.py.")
    
    print("Loading local data...")
    df_local = pd.read_csv(str(file_path), skiprows=4)
    
    target_countries = ['United States', 'China', 'India', 'World']
    df_local = df_local[df_local['Country Name'].isin(target_countries)].copy()
    
    if df_local.empty:
        print("Warning: No matching countries found in local file. Check country names.")
    
    id_vars = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
    value_vars = [col for col in df_local.columns if col not in id_vars and 'Unnamed' not in str(col)]
    
    df_melted = df_local.melt(id_vars=id_vars, value_vars=value_vars, var_name='Year', value_name='Energy_Use')
    
    df_melted['Year'] = pd.to_numeric(df_melted['Year'])
    df_melted['Energy_Use'] = pd.to_numeric(df_melted['Energy_Use'], errors='coerce')
    
    print("Fetching API data...")
    indicators = {
        'NY.GDP.MKTP.KD.ZG': 'GDP_Growth',
        'EN.GHG.CO2.PC.CE.AR5': 'CO2_Emissions',
        'NV.IND.TOTL.ZS': 'Industry_Value_Added'
    }
    
    country_map_df = df_local[['Country Name', 'Country Code']].drop_duplicates()
    country_codes = country_map_df['Country Code'].tolist()
    
    df_api = wbdata.get_dataframe(indicators, country=country_codes)
    
    df_api = df_api.reset_index()
    
    df_api = df_api.rename(columns={'country': 'Country Name', 'date': 'Year'})
    
    df_api['Year'] = df_api['Year'].astype(int)
    
    print("Merging and cleaning data...")
    final_df = pd.merge(df_melted[['Country Name', 'Year', 'Energy_Use']],
                        df_api[['Country Name', 'Year', 'GDP_Growth', 'CO2_Emissions', 'Industry_Value_Added']],
                        on=['Country Name', 'Year'],
                        how='outer')
    
    final_df = final_df[final_df['Country Name'].isin(target_countries)]
    
    final_df = final_df.sort_values(by=['Country Name', 'Year'])
    
    def interpolate_group(group):
        group = group.sort_values('Year')
        cols_to_interp = ['Energy_Use', 'GDP_Growth', 'CO2_Emissions', 'Industry_Value_Added']
        group[cols_to_interp] = group[cols_to_interp].interpolate(method='linear')
        return group

    final_df = final_df.groupby('Country Name', group_keys=False).apply(interpolate_group)
    
    output_file = 'final_dataset.csv'
    final_df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

if __name__ == '__main__':
    load_data()
