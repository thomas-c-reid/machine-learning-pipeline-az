import sys
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
import os
import tempfile
from pipeline.pipeline_builder import PipelineBuilder

sys.dont_write_bytecode = True
pd.set_option('display.max_columns', None)

# Avoid importing Azure ML SDK at module import time. Components running on
# Azure ML receive inputs as mounted files, so the SDK is not required for
# typical preprocessing. If a dataset name (not a mounted path) is provided,
# the loader will perform a lazy SDK import.


def main():
    args = parse_arguments()

    # Load the dataset from Azure ML
    dataset = load_dataset_from_azure(args.data_path)
    print('Loaded dataset from Azure ML:', args.data_path)

    # Split the dataset into train and test sets
    train_data, test_data = train_test_split(dataset, test_size=0.2, random_state=42)

    # Define the pipeline steps
    steps_list = [
        'CleanDataStep',
        'FeatureEngineeringStep',
        'CategoricalEncodeStep',
        'NormalisationStep',
    ]

    # Build and execute the pipeline for train data
    pipeline_builder = PipelineBuilder(steps_list=steps_list)
    data_pipeline = pipeline_builder.build_pipeline()

    processed_train_data = data_pipeline.execute(train_data)
    processed_test_data = data_pipeline.execute(test_data)

    # Save to Azure ML output paths
    # Ensure parent directories exist (Azure may provide a file path).
    def _save_df(df, out_path):
        parent = os.path.dirname(out_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        df.to_csv(out_path, index=False)

    _save_df(processed_train_data, args.train_output)
    _save_df(processed_test_data, args.test_output)
    print("Saved processed train and test datasets to output paths.")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', type=str, required=True, help='Name of the Azure ML dataset')
    parser.add_argument('--train-output', type=str, required=True, help='Output path for train data')
    parser.add_argument('--test-output', type=str, required=True, help='Output path for test data')
    return parser.parse_args()


def load_dataset_from_azure(dataset_name: str):
    """
    Load a dataset from Azure ML workspace.
    """
    # If Azure ML mounts the input, `dataset_name` will be a local path - read it.
    if os.path.exists(dataset_name):
        return pd.read_csv(dataset_name)

    # Otherwise attempt a lazy import of the Azure ML SDK. If it's not
    # available or credentials are not configured, raise a clear error.
    try:
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential
    except Exception:
        raise RuntimeError(
            "Azure ML SDK not available in this environment. Either pass the dataset "
            "as a mounted input file (recommended) or run in an environment that has "
            "the 'azure-ai-ml' and 'azure-identity' packages installed and configured."
        )

    ml_client = MLClient(
        DefaultAzureCredential(),
        subscription_id="your_subscription_id",
        resource_group_name="your_resource_group_name",
        workspace_name="your_workspace_name",
    )

    dataset = ml_client.data.get(name=dataset_name, version="latest")
    # Try reading via dataset.path if available
    if hasattr(dataset, "path") and dataset.path:
        try:
            return pd.read_csv(dataset.path)
        except Exception:
            pass

    # Fallback: download dataset to a temp dir and read the first CSV found
    local_dir = tempfile.mkdtemp()
    ml_client.data.download(name=dataset_name, download_path=local_dir, version="latest")
    for root, _, files in os.walk(local_dir):
        for f in files:
            if f.lower().endswith(".csv"):
                return pd.read_csv(os.path.join(root, f))

    raise RuntimeError(f"Could not locate a CSV file for dataset '{dataset_name}'")


if __name__ == '__main__':
    main()