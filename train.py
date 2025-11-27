import argparse
import pandas as pd
import joblib
import json
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# -----------------------------
# Parse arguments
# -----------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--train", type=str, required=True, help="Path to preprocessed train CSV")
parser.add_argument("--model_output", type=str, required=True, help="Folder to save trained model")
parser.add_argument("--metrics_output", type=str, required=True, help="Folder to save metrics JSON")
args = parser.parse_args()

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv(args.train)

# Determine target column
if "target" in df.columns:
    target_col = "target"
elif "Priority" in df.columns:
    target_col = "Priority"
    print("Using 'Priority' column as target.")
else:
    raise KeyError("No target column found. Expected 'target' or 'Priority'.")

X = df.drop(columns=target_col)
y = df[target_col]

# -----------------------------
# Split data
# -----------------------------
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# -----------------------------
# Train model
# -----------------------------
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# -----------------------------
# Evaluate
# -----------------------------
preds = model.predict(X_val)
mse = float(mean_squared_error(y_val, preds))
r2 = float(r2_score(y_val, preds))

metrics = {
    "task": "regression",
    "mse": mse,
    "r2": r2
}

print(f"Evaluation metrics: {metrics}")

# -----------------------------
# Save model
# -----------------------------
os.makedirs(args.model_output, exist_ok=True)
joblib.dump(model, os.path.join(args.model_output, "model.joblib"))
print(f"Model saved to {args.model_output}")

# -----------------------------
# Save metrics
# -----------------------------
os.makedirs(args.metrics_output, exist_ok=True)
with open(os.path.join(args.metrics_output, "metrics.json"), "w") as f:
    json.dump(metrics, f)
print(f"Metrics saved to {args.metrics_output}")
