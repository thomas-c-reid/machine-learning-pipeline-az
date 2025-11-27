import argparse
import json
import os
import time
from datetime import datetime

from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model, ManagedOnlineEndpoint, ManagedOnlineDeployment

# --- Arguments ---
parser = argparse.ArgumentParser()
parser.add_argument("--metrics_path", required=True)
parser.add_argument("--model_path", required=True)
parser.add_argument("--accuracy_threshold", type=float, default=0.8)
parser.add_argument("--endpoint_name", default="itsm-endpoint")
parser.add_argument("--metric_name", default="auto")
args = parser.parse_args()

# --- Load metrics ---
with open(os.path.join(args.metrics_path, "metrics.json")) as f:
    metrics = json.load(f)

metric_name = args.metric_name
if metric_name == "auto":
    task = metrics.get("task", "classification")
    if task == "regression":
        metric_name = "r2" if "r2" in metrics else "mse" if "mse" in metrics else None
    else:
        metric_name = "accuracy" if "accuracy" in metrics else None

if metric_name not in metrics:
    print("Metric not found — skipping deployment.")
    deploy_decision = False
else:
    metric_value = metrics[metric_name]
    if metric_name == "mse":
        deploy_decision = metric_value <= args.accuracy_threshold
    else:
        deploy_decision = metric_value >= args.accuracy_threshold
    print(f"Metric {metric_name} = {metric_value}, deploy? {deploy_decision}")

# --- Initialize ML Client ---
ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id="559ae823-5169-4f10-92f8-cf17ab62db52",
    resource_group_name="ml-eastus-rg",
    workspace_name="CW2-Workspace-EastUS"
)

# --- Deploy model if threshold passed ---
if deploy_decision:
    print("Registering model...")
    
    # WORKAROUND: Specify explicit version to avoid SDK reading existing versions
    version = datetime.now().strftime("%Y%m%d%H%M%S")
    
    model = Model(
        name="incident-model",
        path=args.model_path,
        type="custom_model",
        version=version,  # Add explicit version
        description=f"Model with {metric_name}={metric_value}"
    )
    
    try:
        model = ml_client.models.create_or_update(model)
        print(f"Model registered: {model.name} version {model.version}")
    except Exception as e:
        print(f"Model registration failed: {e}")
        print("Attempting to continue with endpoint creation anyway...")
        # Create a fake model reference for deployment
        model = type('obj', (object,), {
            'id': f"azureml:incident-model:{version}",
            'name': 'incident-model',
            'version': version
        })

    # --- Handle endpoint creation/update ---
    # --- Handle endpoint creation/update ---
    try:
        endpoint = ml_client.online_endpoints.get(args.endpoint_name)
        print(f"Endpoint exists with state: {endpoint.provisioning_state}")
        
        if endpoint.provisioning_state == "Failed":
            print(f"Endpoint '{args.endpoint_name}' is in Failed state, deleting completely...")
            ml_client.online_endpoints.begin_delete(args.endpoint_name).wait()
            print("Deletion complete. Waiting 30 seconds before recreating...")
            time.sleep(30)
            raise Exception("Recreate after deletion")
            
    except Exception as e:
        print(f"Creating new endpoint... (reason: {str(e)})")
        endpoint = ManagedOnlineEndpoint(name=args.endpoint_name, auth_mode="key")
        
        try:
            poller = ml_client.online_endpoints.begin_create_or_update(endpoint)
            endpoint = poller.result()
            print(f"Endpoint created successfully")
        except Exception as create_error:
            print(f"Endpoint creation failed: {create_error}")
            # Check if provider registration is the issue
            if "SubscriptionNotRegistered" in str(create_error):
                print("\nERROR: Resource providers not registered!")
                print("Run these commands:")
                print("  az provider register --namespace Microsoft.MachineLearningServices")
                print("  az provider register --namespace Microsoft.Compute")
                print("  az provider register --namespace Microsoft.Network")
                print("Then wait 5-10 minutes and retry.")
            raise

    # --- Wait for endpoint to be ready ---
    max_wait = 600  # 10 minutes max
    start_time = time.time()

    while time.time() - start_time < max_wait:
        endpoint = ml_client.online_endpoints.get(args.endpoint_name)
        print(f"Endpoint provisioning state: {endpoint.provisioning_state}")
        
        if endpoint.provisioning_state == "Succeeded":
            break
        elif endpoint.provisioning_state == "Failed":
            raise RuntimeError("Endpoint creation failed, cannot deploy model.")
        
        time.sleep(10)

    print("Deploying model as 'blue' deployment...")
    deployment = ManagedOnlineDeployment(
        name="blue",
        endpoint_name=args.endpoint_name,
        model=model.id,
        instance_type="Standard_DS3_v2",
        instance_count=1
    )
    ml_client.online_deployments.begin_create_or_update(deployment).result()

    print("Routing traffic...")
    ml_client.online_endpoints.begin_update(
        ManagedOnlineEndpoint(name=args.endpoint_name, traffic={"blue": 100})
    ).result()

    # Store API key for next step
    api_key = ml_client.online_endpoints.get_keys(args.endpoint_name).primary_key
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/api_key.txt", "w") as f:
        f.write(api_key)

    print("Deployment finished.")
else:
    print("Skipping deployment due to low metric.")