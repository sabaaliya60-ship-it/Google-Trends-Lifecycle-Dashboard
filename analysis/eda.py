import pandas as pd

# Read Excel File
df = pd.read_excel("data/raw/GOOGLE_TRENDS_1.xlsx")

# Convert Date
df["date"] = pd.to_datetime(df["date"])

# Remove Duplicates
df = df.drop_duplicates()

# Remove Missing Values
df = df.dropna()

# Summary
print(df.head())

print("\nRows :", len(df))
print("Columns :", len(df.columns))

# Save Processed File
df.to_csv("data/processed/google_trends_clean.csv", index=False)

print("\nData Saved Successfully")