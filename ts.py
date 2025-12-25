import pandas as pd

file_path = "/Users/archanasingh/Downloads/API_EG.USE.PCAP.KG.OE_DS2_en_excel_v2_1020.xls"

# Read Excel with correct header row
df = pd.read_excel(file_path, header=3)

# Show headers
print("Correct headers:")
print(df.columns.tolist())

# Optional: show first few rows of actual data
print(df.head())
