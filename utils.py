import pandas as pd
import streamlit as st

def validate_file(file) -> bool:
    """
    Validate the uploaded file format and content.
    """
    filename = file.name.lower()
    return filename.endswith(('.csv', '.xlsx'))

def load_data(file) -> pd.DataFrame:
    """
    Load and validate data from uploaded file.
    """
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # Basic validation
        if df.empty:
            raise ValueError("The uploaded file is empty")
        
        # Remove any completely empty columns or rows
        df = df.dropna(how='all', axis=1)
        df = df.dropna(how='all', axis=0)
        
        return df
        
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None
