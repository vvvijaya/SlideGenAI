import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Tuple

def validate_input(df: pd.DataFrame, group_cols: list, agg_methods: dict) -> Tuple[bool, str]:
    """
    Validate input parameters for data processing.
    """
    if not isinstance(df, pd.DataFrame):
        return False, "Invalid data format"
    
    if group_cols and not all(col in df.columns for col in group_cols):
        return False, "One or more grouping columns not found in data"
        
    if agg_methods:
        valid_methods = ['sum', 'mean', 'count', 'min', 'max']
        if not all(method in valid_methods for method in agg_methods.values()):
            return False, "Invalid aggregation method specified"
        if not all(col in df.columns for col in agg_methods.keys()):
            return False, "One or more aggregation columns not found in data"
    
    return True, ""

def process_data(df: pd.DataFrame, group_cols: Optional[List[str]] = None, 
                agg_methods: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Process the data according to specified grouping and aggregation methods.
    Includes enhanced error handling and input validation.
    """
    try:
        # Input validation
        is_valid, error_message = validate_input(df, group_cols, agg_methods)
        if not is_valid:
            raise ValueError(error_message)

        # Handle empty inputs
        if not group_cols:
            return df.copy()
        
        if not agg_methods:
            return df.groupby(group_cols).first().reset_index()

        # Create aggregation dictionary
        agg_dict = {col: method for col, method in agg_methods.items()}
        
        # Verify numeric columns for aggregation
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        invalid_cols = [col for col in agg_dict.keys() 
                       if col not in numeric_cols and agg_dict[col] not in ['count']]
        if invalid_cols:
            raise ValueError(f"Non-numeric columns cannot be aggregated with methods other than 'count': {invalid_cols}")

        # Group and aggregate data
        grouped_df = df.groupby(group_cols).agg(agg_dict).reset_index()
        
        # Round numeric columns to 2 decimal places
        numeric_columns = grouped_df.select_dtypes(include=['float64']).columns
        grouped_df[numeric_columns] = grouped_df[numeric_columns].round(2)
        
        # Verify output
        if grouped_df.empty:
            raise ValueError("Aggregation resulted in empty dataset")
        
        return grouped_df
    
    except Exception as e:
        error_msg = str(e)
        st.error(f"Error processing data: {error_msg}")
        raise Exception(f"Data processing failed: {error_msg}")
