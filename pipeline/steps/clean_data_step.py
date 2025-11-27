from pipeline.steps.pipeline_step import PipelineStep
import pandas as pd

class CleanDataStep(PipelineStep):

    def __init__(self):
        super().__init__(name='Clean Data Step')

    def process(self, data):
        """
        Perform data cleaning operations on the dataset.
        """
        print("CleanDataStep: Cleaning the dataset...")

        # Drop non-informative columns 
        columns_to_drop = [
            "Incident_ID",
            "number_cnt",
            "Alert_Status",
            "CI_Name",
            "Related_Interaction",
            "Related_Change",
            "Reopen_Time",
            "No_of_Related_Incidents",
            "No_of_Related_Changes",
            "KB_number",
            "WBS"
        ]

        # Before dropping columns
        print("Columns before dropping non-informative ones:")
        print(data.columns.tolist())

        dropped_columns = [col for col in columns_to_drop if col in data.columns]
        data = data.drop(columns=dropped_columns, errors="ignore")

        # After dropping columns
        print()
        print("Dropped columns:")
        print(dropped_columns)
        print()
        print("Columns after dropping non-informative ones:")
        print(data.columns.tolist())

        #  Drop rows where Priority is missing (target) 
        if "Priority" in data.columns:
            before_rows = data.shape[0]
            data = data[data["Priority"].notna()]
            after_rows = data.shape[0]
            print(f"Dropped rows with missing Priority: {before_rows - after_rows}")

        # Fill missing categorical values with 'Unknown' 
        cat_fill_cols = ["CI_Cat", "CI_Subcat", "Closure_Code"]
        for col in cat_fill_cols:
            if col in data.columns:
                missing_before = data[col].isnull().sum()
                data[col] = data[col].fillna("Unknown")
                missing_after = data[col].isnull().sum()
                print(f"Filled missing values in '{col}': {missing_before - missing_after}")

        # Fill missing numeric fields where 0 = absence 
        if "No_of_Reassignments" in data.columns:
            missing_before = data["No_of_Reassignments"].isnull().sum()
            data["No_of_Reassignments"] = data["No_of_Reassignments"].fillna(0)
            missing_after = data["No_of_Reassignments"].isnull().sum()
            print(f"Filled missing values in 'No_of_Reassignments': {missing_before - missing_after}")

        if "No_of_Related_Interactions" in data.columns:
            missing_before = data["No_of_Related_Interactions"].isnull().sum()
            data["No_of_Related_Interactions"] = data["No_of_Related_Interactions"].fillna(0)
            missing_after = data["No_of_Related_Interactions"].isnull().sum()
            print(f"Filled missing values in 'No_of_Related_Interactions': {missing_before - missing_after}")

        print("CleanDataStep: Completed.")
        return data
