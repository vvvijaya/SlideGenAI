import pandas as pd
import streamlit as st
from typing import Tuple, Optional
import tempfile
import os

def validate_file(file) -> Tuple[bool, str]:
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
            
        # Create temporary file for validation
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            tmp_file.write(file.getbuffer())
            tmp_path = tmp_file.name

        try:
            # Attempt to read file
            if filename.endswith('.csv'):
                pd.read_csv(tmp_path, nrows=1)
            else:
                pd.read_excel(tmp_path, nrows=1)
        except Exception as e:
            os.unlink(tmp_path)
            return False, f"File format validation failed: {str(e)}"
        
        os.unlink(tmp_path)
        return True, ""
        
    except Exception as e:
        return False, f"Error validating file: {str(e)}"

def load_data(file) -> Optional[pd.DataFrame]:
    """
    Load and validate data from uploaded file.
    Returns None if validation fails.
    """
    try:
        # Validate file
        is_valid, error_message = validate_file(file)
        if not is_valid:
            st.error(error_message)
            return None
            
        # Load file based on extension
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return None
        
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

        # Check for duplicate column names
        if len(df.columns) != len(set(df.columns)):
            st.error("File contains duplicate column names. Please ensure all column names are unique.")
            return None

        # Convert column names to string and remove special characters
        df.columns = df.columns.astype(str).str.replace('[^a-zA-Z0-9_]', '_')
        
        return df
        
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def safe_numeric_conversion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Safely convert numeric columns to appropriate types.
    """
    for col in df.columns:
        try:
            # Try to convert to numeric, coerce errors to NaN
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            # Only update if the conversion resulted in less than 10% NaN values
            if numeric_series.isna().sum() / len(numeric_series) < 0.1:
                df[col] = numeric_series
        except:
            continue
    return df
