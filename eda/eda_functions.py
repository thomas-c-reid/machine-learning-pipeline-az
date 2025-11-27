import matplotlib.pyplot as plt

def view_dataset_summary(dataset):
    """
    Function to view summary statistics of the dataset.
    """
    print("Dataset Information:")
    print(dataset.head())  # Prints basic info about the dataset
    print("\nNumber of Rows and Columns:")
    print(f"Rows: {dataset.shape[0]}, Columns: {dataset.shape[1]}")
    print("\nColumn Data Types:")
    print(dataset.dtypes)
    print("\nNumber of Unique Values per Column:")
    print(dataset.nunique())
    print("\nNumber of Missing Values per Column:")
    missing_values = dataset.isnull().sum()
    print(missing_values)
    print("\nNumber of Duplicate Rows:")
    print(dataset.duplicated().sum())
    print("\nSummary Statistics for Numerical Columns:")
    print(dataset.describe())

    # Plot horizontal bar chart for missing values
    missing_values = missing_values[missing_values > 0].sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    bars = plt.barh(missing_values.index, missing_values.values, color='skyblue')
    plt.title('Missing Values per Column')
    plt.xlabel('Number of Missing Values')
    plt.ylabel('Columns')
    plt.gca().invert_yaxis()  # Invert y-axis for better readability

    # Annotate bars with the exact numbers
    for bar in bars:
        plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                 f'{int(bar.get_width())}', va='center')

    plt.tight_layout()
    plt.show()
    
    
def view_small_tables(dataset):
    print('*' * 50)

    # 1. Configuration items and service details
    config_items = dataset[["CI_Name", "CI_Cat", "CI_Subcat", "WBS", "Category"]]
    print("Configuration Items and Service Details:")
    print(config_items.head())
    print("\nThese fields describe the affected system and its categorization in the IT environment.")

    print('*' * 50)

    # 2. Incident Identity and Status
    incident_identity = dataset[["Incident_ID", "Status", "Alert_Status", "Closure_Code"]]
    print("Incident Identity and Status:")
    print(incident_identity.head())
    print("\nThese fields identify the ticket and track its current state in the incident workflow.")

    print('*' * 50)

    # 3. Severity and Business Impact
    severity_impact = dataset[["Impact", "Urgency", "Priority"]]
    print("Severity and Business Impact:")
    print(severity_impact.head())
    print("\nThese fields describe how critical the incident is and how quickly it must be addressed.")

    print('*' * 50)

    # 4. Time and Lifecycle tracking
    time_tracking = dataset[["Open_Time", "Reopen_Time", "Resolved_Time", "Close_Time", "Handle_Time_hrs"]]
    print("Time and Lifecycle Tracking:")
    print(time_tracking.head())
    print("\nThese fields track the full lifecycle of a ticket from creation to closure.")

    print('*' * 50)

    # 5. Operational complexity
    operational_complexity = dataset[["No_of_Reassignments", "number_cnt"]]
    print("Operational Complexity:")
    print(operational_complexity.head())
    print("\nThese fields measure work effort and complexity.")

    print('*' * 50)

    # 6. Related Records
    related_records = dataset[["No_of_Related_Interactions", "Related_Interaction", "No_of_Related_Incidents", "No_of_Related_Changes", "Related_Change", "KB_number"]]
    print("Related Records:")
    print(related_records.head())
    print("\nThese fields show connections to other incidents and changes, useful for identifying clusters, cascading failures, and change-related incidents.")

    print('*' * 50)