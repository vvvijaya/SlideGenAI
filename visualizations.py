import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
from io import StringIO
import asyncio
import traceback
import logging
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualizationError(Exception):
    """Custom exception for visualization-related errors"""
    pass

async def create_visualization(data: pd.DataFrame, viz_type: str, x_column: str, y_column: str, 
                      color_column: str = None, title: str = None, 
                      x_label: str = None, y_label: str = None,
                      theme: str = "plotly", show_grid: bool = True,
                      show_legend: bool = True, orientation: str = "vertical",
                      animation_frame: str = None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Create a visualization asynchronously and return it as HTML and SVG.
    Returns a tuple of (html_content, svg_content, error_message).
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

        fig = None
        
        # Use custom labels or column names
        x_label = x_label or x_column
        y_label = y_label or y_column
        title = title or f"{viz_type.title()} Chart"
        
        # Handle orientation
        if orientation == "horizontal" and viz_type in ["bar", "scatter", "line"]:
            x_column, y_column = y_column, x_column
            x_label, y_label = y_label, x_label
        
        # Create visualization based on type with error handling
        kwargs = {
            "title": title,
            "labels": {x_column: x_label, y_column: y_label},
            "animation_frame": animation_frame,
            "template": theme
        }
        
        try:
            if viz_type == "bar":
                fig = px.bar(data, x=x_column, y=y_column, color=color_column, **kwargs)
                if orientation == "horizontal":
                    fig.update_layout(barmode='relative')
            elif viz_type == "line":
                fig = px.line(data, x=x_column, y=y_column, color=color_column, **kwargs)
            elif viz_type == "scatter":
                fig = px.scatter(data, x=x_column, y=y_column, color=color_column, **kwargs)
            elif viz_type == "pie":
                if y_column not in get_numeric_columns(data):
                    raise VisualizationError("Values for pie chart must be numeric")
                fig = px.pie(data, values=y_column, names=x_column, title=title)
            elif viz_type == "heatmap":
                try:
                    pivot_data = pd.pivot_table(data, values=y_column, index=x_column, 
                                             columns=color_column, aggfunc='mean')
                    fig = px.imshow(pivot_data, title=title, aspect="auto")
                except Exception as e:
                    logger.error(f"Error creating heatmap: {str(e)}")
                    raise VisualizationError(f"Error creating heatmap: {str(e)}")
            elif viz_type == "box":
                fig = px.box(data, x=x_column, y=y_column, color=color_column, **kwargs)
            
            if fig is None:
                raise VisualizationError(f"Unsupported visualization type: {viz_type}")
            
            # Update layout for better presentation view
            fig.update_layout(
                width=800,
                height=500,
                font=dict(size=14),
                margin=dict(l=50, r=50, t=50, b=50),
                showlegend=show_legend,
                hovermode='closest',
                hoverlabel=dict(bgcolor="white", font_size=12)
            )
            
            # Update grid settings
            fig.update_xaxes(showgrid=show_grid)
            fig.update_yaxes(showgrid=show_grid)
            
            # Handle animation settings
            if animation_frame:
                fig.update_layout(
                    updatemenus=[{
                        "type": "buttons",
                        "showactive": False,
                        "buttons": [
                            {"label": "Play",
                             "method": "animate",
                             "args": [None, {"frame": {"duration": 500, "redraw": True},
                                           "fromcurrent": True}]},
                            {"label": "Pause",
                             "method": "animate",
                             "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                             "mode": "immediate"}]}
                        ]
                    }]
                )
            
            try:
                # Generate interactive HTML
                html_str = fig.to_html(
                    include_plotlyjs='cdn',
                    full_html=False,
                    config={'displayModeBar': True,
                           'responsive': True,
                           'displaylogo': False}
                )
                
                # Generate SVG
                svg_str = fig.to_image(format="svg").decode()
                
                return html_str, svg_str, None
            except Exception as e:
                logger.error(f"Error generating visualization formats: {str(e)}")
                return None, None, f"Error generating visualization: {str(e)}"
        
        except Exception as e:
            logger.error(f"Error creating {viz_type} visualization: {str(e)}\n{traceback.format_exc()}")
            return None, None, f"Error creating visualization: {str(e)}"
    
    except Exception as e:
        logger.error(f"Visualization error: {str(e)}\n{traceback.format_exc()}")
        return None, None, f"Error: {str(e)}"

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
    """Return list of available plotly themes."""
    try:
        return ['plotly', 'plotly_white', 'plotly_dark', 'ggplot2', 
                'seaborn', 'simple_white', 'presentation']
    except Exception as e:
        logger.error(f"Error getting themes: {str(e)}")
        return ['plotly']  # Return default theme as fallback
