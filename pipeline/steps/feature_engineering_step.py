from pipeline.steps.pipeline_step import PipelineStep
import pandas as pd
import numpy as np

class FeatureEngineeringStep(PipelineStep):

    def __init__(self):
        super().__init__(name='feature engineering step')

    def process(self, data):
        """
        Perform feature engineering operations on the dataset.
        """
        print("FeatureEngineeringStep started...")

        data = data.copy()

        # --- Subset Before and After for Handle_Time_hrs ---
        relevant_columns = ["Handle_Time_hrs", "Open_Time", "Resolved_Time", "Close_Time"]
        if any(col in data.columns for col in relevant_columns):
            affected_rows = data[relevant_columns].copy()
            print("Before Handling Relevant Columns:")
            print(affected_rows.head())

        # Clean Handle_Time_hrs text & convert to float
        if "Handle_Time_hrs" in data.columns:
            data["Handle_Time_hrs"] = (
                data["Handle_Time_hrs"]
                .astype(str)
                .str.replace(",", "", regex=False)
                .astype(float)
            )

        # Time columns to parse
        time_cols = ["Open_Time", "Resolved_Time", "Close_Time", "Reopen_Time"]

        # Custom datetime parser for mixed date formats
        def parse_date(x):
            for fmt in ("%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M", "%m/%d/%Y %H:%M"):
                try:
                    return pd.to_datetime(x, format=fmt)
                except:
                    continue
            return pd.to_datetime(x, errors='coerce')

        # Convert to datetime
        for col in time_cols:
            if col in data.columns:
                data[col] = data[col].apply(parse_date)

        # Compute Handle_Time_hrs if missing or corrupted
        if "Handle_Time_hrs" not in data.columns or data["Handle_Time_hrs"].isna().sum() > 0:
            data["Handle_Time_hrs_calc"] = (
                (data["Close_Time"] - data["Open_Time"]).dt.total_seconds() / 3600
            )
            # Use calculated value where original is missing
            data["Handle_Time_hrs"] = data["Handle_Time_hrs"].fillna(data["Handle_Time_hrs_calc"])
            data.drop(columns=["Handle_Time_hrs_calc"], inplace=True, errors="ignore")

        # Remove negative times
        data.loc[data["Handle_Time_hrs"] < 0, "Handle_Time_hrs"] = np.nan

        # --- Subset After Handling Relevant Columns ---
        if any(col in data.columns for col in relevant_columns):
            print("After Handling Relevant Columns:")
            print(data[relevant_columns].head())

        # Drop raw datetime columns — modelling ready!
        data = data.drop(columns=time_cols, errors='ignore')

        print("FeatureEngineeringStep complete.")

        return data