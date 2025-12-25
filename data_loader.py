import pandas as pd
import wbdata
import numpy as np

def load_data():
    # File path
    file_path = '/Users/archanasingh/Documents/Parmarth/ts/API_EG.USE.PCAP.KG.OE_DS2_en_csv_v2_2449/API_EG.USE.PCAP.KG.OE_DS2_en_csv_v2_2449.csv'
    
    # --- Step A: Process Local File ---
    print("Loading local data...")
    # Skip the first 4 rows which contain metadata
    # The header is on row 5 (0-indexed index 4)
    df_local = pd.read_csv(file_path, skiprows=4)
    
    # Filter for target countries
    target_countries = ['United States', 'China', 'India', 'World']
    df_local = df_local[df_local['Country Name'].isin(target_countries)].copy()
    
    if df_local.empty:
        print("Warning: No matching countries found in local file. Check country names.")
    
    # Melt the DataFrame
    # Keep metadata columns as ID vars
    id_vars = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
    # Value vars are the years. We filter out columns that are not year columns (e.g. 'Unnamed: 68')
    value_vars = [col for col in df_local.columns if col not in id_vars and 'Unnamed' not in str(col)]
    
    df_melted = df_local.melt(id_vars=id_vars, value_vars=value_vars, var_name='Year', value_name='Energy_Use')
    
    # Convert types
    df_melted['Year'] = pd.to_numeric(df_melted['Year'])
    df_melted['Energy_Use'] = pd.to_numeric(df_melted['Energy_Use'], errors='coerce')
    
    # --- Step B: Fetch Missing Features (API) ---
    print("Fetching API data...")
    # Define indicators
    indicators = {
        'NY.GDP.MKTP.KD.ZG': 'GDP_Growth',
        'EN.GHG.CO2.PC.CE.AR5': 'CO2_Emissions',
        'NV.IND.TOTL.ZS': 'Industry_Value_Added'
    }
    
    # Map country names to codes for wbdata
    # We use the codes present in the local file for consistency
    country_map_df = df_local[['Country Name', 'Country Code']].drop_duplicates()
    country_codes = country_map_df['Country Code'].tolist()
    
    # Fetch data
    # wbdata.get_dataframe takes country codes
    # Note: wbdata returns a dataframe with a MultiIndex (country, date)
    df_api = wbdata.get_dataframe(indicators, country=country_codes)
    
    # Reset index to get 'country' (name) and 'date' (year) as columns
    df_api = df_api.reset_index()
    
    # Rename columns to match df_melted
    # wbdata returns 'country' (name) and 'date'
    df_api = df_api.rename(columns={'country': 'Country Name', 'date': 'Year'})
    
    # Convert Year to integer
    df_api['Year'] = df_api['Year'].astype(int)
    
    # --- Step C: Merge & Clean ---
    print("Merging and cleaning data...")
    # Merge on Country Name and Year
    # Using 'outer' to include all available years from both sources
    final_df = pd.merge(df_melted[['Country Name', 'Year', 'Energy_Use']],
                        df_api[['Country Name', 'Year', 'GDP_Growth', 'CO2_Emissions', 'Industry_Value_Added']],
                        on=['Country Name', 'Year'],
                        how='outer')
    
    # Filter again to ensure we only have our target countries
    final_df = final_df[final_df['Country Name'].isin(target_countries)]
    
    # Sort for correct interpolation
    final_df = final_df.sort_values(by=['Country Name', 'Year'])
    
    # Interpolate missing values (Linear) per country
    def interpolate_group(group):
        # Sort by year just in case
        group = group.sort_values('Year')
        # Interpolate numeric columns
        cols_to_interp = ['Energy_Use', 'GDP_Growth', 'CO2_Emissions', 'Industry_Value_Added']
        # We use assign to avoid SettingWithCopy warnings and ensure return
        # Using ffill and bfill as fallback if linear fails at edges (optional but good practice, though prompt only asked for Linear)
        # Prompt said "Interpolate missing values (Linear)". We stick to that.
        group[cols_to_interp] = group[cols_to_interp].interpolate(method='linear')
        return group

    final_df = final_df.groupby('Country Name', group_keys=False).apply(interpolate_group)
    
    # Save to CSV
    output_file = 'final_dataset.csv'
    final_df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

if __name__ == '__main__':
    load_data()
