import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# Load processed data
df = pd.read_csv("data/processed/google_trends_clean.csv")

# Convert date into numeric
df["date"] = pd.to_datetime(df["date"])
df["Day_Number"] = (df["date"] - df["date"].min()).dt.days

# Features (X)
X = df[["Day_Number"]]

# Target (y)
y = df["interest_score"]

# Train Model
model = LinearRegression()
model.fit(X, y)

# Save Model
joblib.dump(model, "models/trend_model.pkl")

print("✅ Model Trained Successfully")