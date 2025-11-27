from pipeline.steps.pipeline_step import PipelineStep
from sklearn.preprocessing import LabelEncoder
import pandas as pd

class CategoricalEncodeStep(PipelineStep):

    def __init__(self):
        super().__init__(name='Categorical Encoding Step')

    def process(self, data):
        """
        Perform categorical encoding on the dataset for relevant columns.
        """
        print("CategoricalEncodeStep: Encoding relevant categorical variables...")

        # Columns that require encoding
        columns_to_encode = ["CI_Cat", "CI_Subcat", "Status", "Impact", "Urgency", "Priority", "Category", "Closure_Code"]

        # Create a subset of the data with only relevant columns
        subset_data = data[columns_to_encode].copy()

        print("Before Encoding:")
        print(subset_data.head())

        # Apply Label Encoding to specified columns
        label_encoder = LabelEncoder()
        for col in columns_to_encode:
            if col in subset_data.columns:
                subset_data[col] = label_encoder.fit_transform(subset_data[col].astype(str))

        print("After Encoding:")
        print(subset_data.head())

        # Update the original data with encoded values
        for col in columns_to_encode:
            if col in data.columns:
                data[col] = subset_data[col]

        print("CategoricalEncodeStep: Completed.")
        return data
