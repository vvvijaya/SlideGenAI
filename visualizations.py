import pandas as pd
import base64
from io import StringIO
import asyncio
import traceback
import logging
from typing import Tuple, Optional, Dict, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualizationError(Exception):
    """Custom exception for visualization-related errors"""
    pass

async def create_visualization(data: pd.DataFrame, viz_type: str, x_column: str, y_column: str,
                             color_column: Optional[str] = None, title: Optional[str] = None,
                             x_label: Optional[str] = None, y_label: Optional[str] = None,
                             theme: str = "default", show_grid: bool = True,
                             show_legend: bool = True, orientation: str = "vertical",
                             animation_frame: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Create chart data for visualization.
    Returns a tuple of (chart_data, error_message).
    """
    try:
        # Validate input parameters
        if not isinstance(data, pd.DataFrame):
            raise VisualizationError("Invalid input: data must be a pandas DataFrame")
        
        if data.empty:
            raise VisualizationError("Cannot create visualization from empty dataset")
            
        if not all(col in data.columns for col in [x_column, y_column]):
            raise VisualizationError(f"Columns {x_column} or {y_column} not found in data")
            
        if color_column and color_column not in data.columns:
            raise VisualizationError(f"Color column {color_column} not found in data")

        # Process data for chart
        categories = data[x_column].unique().tolist()
        
        # Handle series based on color column
        series_data = {}
        if color_column:
            for color_val in data[color_column].unique():
                filtered_data = data[data[color_column] == color_val]
                series_data[str(color_val)] = filtered_data.groupby(x_column)[y_column].mean().tolist()
        else:
            series_data['Series 1'] = data.groupby(x_column)[y_column].mean().tolist()
            
        chart_data = {
            'type': viz_type,
            'categories': categories,
            'series': series_data,
            'title': title or f"{viz_type.title()} Chart",
            'x_label': x_label or x_column,
            'y_label': y_label or y_column
        }
        
        return chart_data, None
    except Exception as e:
        logger.error(f"Visualization error: {str(e)}\n{traceback.format_exc()}")
        return None, f"Error creating chart data: {str(e)}"

def get_numeric_columns(df: pd.DataFrame) -> list:
    """Return list of numeric columns in the dataframe."""
    try:
        return df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    except Exception as e:
        logger.error(f"Error getting numeric columns: {str(e)}")
        return []

def get_categorical_columns(df: pd.DataFrame) -> list:
    """Return list of categorical columns in the dataframe."""
    try:
        return df.select_dtypes(include=['object', 'category']).columns.tolist()
    except Exception as e:
        logger.error(f"Error getting categorical columns: {str(e)}")
        return []

def get_available_themes() -> list:
    """Return list of available themes."""
    try:
        return ['default', 'light', 'dark', 'presentation']
    except Exception as e:
        logger.error(f"Error getting themes: {str(e)}")
        return ['default']  # Return default theme as fallback