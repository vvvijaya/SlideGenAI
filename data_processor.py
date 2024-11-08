import pandas as pd

def process_data(df: pd.DataFrame, group_cols: list, agg_methods: dict) -> pd.DataFrame:
    """
    Process the data according to specified grouping and aggregation methods.
    """
    if not group_cols:
        return df
    
    try:
        # Create aggregation dictionary
        agg_dict = {col: method for col, method in agg_methods.items()}
        
        # Group and aggregate data
        grouped_df = df.groupby(group_cols).agg(agg_dict).reset_index()
        
        # Round numeric columns to 2 decimal places
        numeric_columns = grouped_df.select_dtypes(include=['float64']).columns
        grouped_df[numeric_columns] = grouped_df[numeric_columns].round(2)
        
        return grouped_df
    
    except Exception as e:
        raise Exception(f"Error processing data: {str(e)}")
