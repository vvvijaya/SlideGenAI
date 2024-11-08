import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
from io import StringIO

def create_visualization(data: pd.DataFrame, viz_type: str, x_column: str, y_column: str, 
                        color_column: str = None, title: str = None, 
                        x_label: str = None, y_label: str = None,
                        theme: str = "plotly") -> str:
    """
    Create a visualization based on the specified type and return it as a base64 encoded SVG.
    """
    fig = None
    
    # Use custom labels or column names
    x_label = x_label or x_column
    y_label = y_label or y_column
    title = title or f"{viz_type.title()} Chart"
    
    if viz_type == "bar":
        fig = px.bar(data, x=x_column, y=y_column, color=color_column,
                    title=title, labels={x_column: x_label, y_column: y_label})
    elif viz_type == "line":
        fig = px.line(data, x=x_column, y=y_column, color=color_column,
                     title=title, labels={x_column: x_label, y_column: y_label})
    elif viz_type == "scatter":
        fig = px.scatter(data, x=x_column, y=y_column, color=color_column,
                        title=title, labels={x_column: x_label, y_column: y_label})
    elif viz_type == "pie":
        fig = px.pie(data, values=y_column, names=x_column, title=title)
    elif viz_type == "heatmap":
        pivot_data = pd.pivot_table(data, values=y_column, index=x_column, 
                                  columns=color_column, aggfunc='mean')
        fig = px.imshow(pivot_data, title=title)
    elif viz_type == "box":
        fig = px.box(data, x=x_column, y=y_column, color=color_column,
                    title=title, labels={x_column: x_label, y_column: y_label})
    
    if fig:
        # Update layout for better presentation view
        fig.update_layout(
            width=800,
            height=500,
            font=dict(size=14),
            margin=dict(l=50, r=50, t=50, b=50),
            template=theme,
            showlegend=True if color_column else False
        )
        
        # Make interactive features available in SVG
        fig.update_layout(
            hovermode='closest',
            hoverlabel=dict(bgcolor="white", font_size=12)
        )
        
        # Convert to SVG with interactive features
        svg_str = fig.to_image(format="svg").decode()
        return base64.b64encode(svg_str.encode()).decode()
    
    return None

def get_numeric_columns(df: pd.DataFrame) -> list:
    """Return list of numeric columns in the dataframe."""
    return df.select_dtypes(include=['int64', 'float64']).columns.tolist()

def get_categorical_columns(df: pd.DataFrame) -> list:
    """Return list of categorical columns in the dataframe."""
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

def get_available_themes() -> list:
    """Return list of available plotly themes."""
    return ['plotly', 'plotly_white', 'plotly_dark', 'ggplot2', 
            'seaborn', 'simple_white']
