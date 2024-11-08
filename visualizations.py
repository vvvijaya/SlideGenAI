import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
from io import StringIO

def create_visualization(data: pd.DataFrame, viz_type: str, x_column: str, y_column: str, color_column: str = None) -> str:
    """
    Create a visualization based on the specified type and return it as a base64 encoded SVG.
    """
    fig = None
    
    if viz_type == "bar":
        fig = px.bar(data, x=x_column, y=y_column, color=color_column)
    elif viz_type == "line":
        fig = px.line(data, x=x_column, y=y_column, color=color_column)
    elif viz_type == "scatter":
        fig = px.scatter(data, x=x_column, y=y_column, color=color_column)
    elif viz_type == "pie":
        fig = px.pie(data, values=y_column, names=x_column)
    
    if fig:
        # Update layout for better presentation view
        fig.update_layout(
            width=800,
            height=500,
            font=dict(size=14),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        # Convert to SVG
        svg_str = fig.to_image(format="svg").decode()
        return base64.b64encode(svg_str.encode()).decode()
    
    return None

def get_numeric_columns(df: pd.DataFrame) -> list:
    """Return list of numeric columns in the dataframe."""
    return df.select_dtypes(include=['int64', 'float64']).columns.tolist()

def get_categorical_columns(df: pd.DataFrame) -> list:
    """Return list of categorical columns in the dataframe."""
    return df.select_dtypes(include=['object', 'category']).columns.tolist()
