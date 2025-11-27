import argparse
import pandas as pd
import requests
from sklearn.metrics import accuracy_score, r2_score, mean_squared_error

parser = argparse.ArgumentParser()
parser.add_argument("--test_data", type=str, required=True)
parser.add_argument("--endpoint_name", type=str, required=True)
parser.add_argument("--api_key", type=str, required=True)
parser.add_argument("--workspace_region", type=str, required=True)
args = parser.parse_args()

# Load test data
df_test = pd.read_csv(args.test_data)
target_col = "target" if "target" in df_test.columns else "Priority"

X_test = df_test.drop(columns=target_col)
y_test = df_test[target_col]

# Build endpoint URL
url = f"https://{args.endpoint_name}.{args.workspace_region}.inference.ml.azure.com/score"

headers = {
    "Authorization": f"Bearer {args.api_key}",
    "Content-Type": "application/json"
}

payload = {"data": X_test.to_dict(orient="records")}
response = requests.post(url, headers=headers, json=payload)
predictions = response.json()["predictions"]

# Compute metric
if df_test[target_col].dtype == "float" or df_test[target_col].dtype == "int":
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    print(f"Test MSE: {mse}, R2: {r2}")
else:
    acc = accuracy_score(y_test, predictions)
    print(f"Test accuracy: {acc}")
