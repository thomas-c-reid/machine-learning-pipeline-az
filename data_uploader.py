# Imports
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential

class AzureUploader:
    def __init__(self, subscription_id: str, resource_group_name: str, workspace_name: str):
        self.ml_client = MLClient(
            DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
        )

    def upload_dataset(self, dataset_name: str, dataset_path: str, description: str):
        # Check if the dataset already exists
        existing_datasets = self.ml_client.data.list(name=dataset_name)
        
        # Determine the next version number
        version_numbers = [int(ds.version) for ds in existing_datasets if ds.version.isdigit()]
        next_version = max(version_numbers, default=0) + 1

        # Define and register the new dataset version
        new_data = Data(
            name=dataset_name,
            version=str(next_version),
            path=dataset_path,
            type=AssetTypes.URI_FILE,
            description=description,
        )

        self.ml_client.data.create_or_update(new_data)
        print(f"Uploaded dataset '{dataset_name}' as version {next_version}.")
