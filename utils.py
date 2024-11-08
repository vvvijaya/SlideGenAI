import pandas as pd
import streamlit as st

def validate_file(file) -> bool:
    """
    Validate the uploaded file format and content.
    Returns a tuple of (is_valid: bool, error_message: str)
    """
    try:
        # Check if file is None
        if file is None:
            return False, "No file was uploaded."
            
        # Validate file format
        filename = file.name.lower()
        if not filename.endswith(('.csv', '.xlsx')):
            return False, "Invalid file format. Please upload a CSV or Excel file."
            
        # Check file size (max 200MB)
        MAX_SIZE_MB = 200
        file_size_mb = file.size / (1024 * 1024)  # Convert to MB
        if file_size_mb > MAX_SIZE_MB:
            return False, f"File size exceeds {MAX_SIZE_MB}MB limit. Please upload a smaller file."
            
        return True, ""
        
    except Exception as e:
        return False, f"Error validating file: {str(e)}"

def load_data(file) -> pd.DataFrame:
    """
    Load and validate data from uploaded file.
    """
    try:
        # Validate file
        is_valid, error_message = validate_file(file)
        if not is_valid:
            st.error(error_message)
            return None
            
        # Load file based on extension
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Basic validation
        if df.empty:
            st.error("The uploaded file is empty")
            return None
        
        # Remove any completely empty columns or rows
        df = df.dropna(how='all', axis=1)
        df = df.dropna(how='all', axis=0)
        
        # Validate minimum data requirements
        if len(df.columns) < 2:
            st.error("The file must contain at least 2 columns")
            return None
            
        if len(df) < 1:
            st.error("The file must contain at least 1 row of data")
            return None
        
        return df
        
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None
