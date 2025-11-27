from pipeline.steps.pipeline_step import PipelineStep
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

class NormalisationStep(PipelineStep):

    def __init__(self):
        super().__init__(name='Normalisation Step')

    def process(self, data):
        """
        Perform normalization on numerical columns in the dataset.
        """
        print("NormalisationStep: Normalizing numerical columns...")

        # Select numerical columns
        numerical_columns = data.select_dtypes(include=['number']).columns

        # Display before normalization
        print("Before Normalization:")
        print(data[numerical_columns].head())

        # Apply Min-Max Scaling
        scaler = MinMaxScaler()
        data[numerical_columns] = scaler.fit_transform(data[numerical_columns])

        # Display after normalization
        print("After Normalization:")
        print(data[numerical_columns].head())

        print("NormalisationStep: Completed.")
        return data
