import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
from io import StringIO

def create_visualization(data: pd.DataFrame, viz_type: str, x_column: str, y_column: str, 
                        color_column: str = None, title: str = None, 
                        x_label: str = None, y_label: str = None,
                        theme: str = "plotly", show_grid: bool = True,
                        show_legend: bool = True, orientation: str = "vertical",
                        animation_frame: str = None) -> tuple:
    """
    Create a visualization and return it as HTML and a static image fallback.
    Returns a tuple of (html_content, error_message).
    """
    try:
        fig = None
        
        # Use custom labels or column names
        x_label = x_label or x_column
        y_label = y_label or y_column
        title = title or f"{viz_type.title()} Chart"
        
        # Handle orientation
        if orientation == "horizontal" and viz_type in ["bar", "scatter", "line"]:
            x_column, y_column = y_column, x_column
            x_label, y_label = y_label, x_label
        
        # Create visualization based on type
        kwargs = {
            "title": title,
            "labels": {x_column: x_label, y_column: y_label},
            "animation_frame": animation_frame,
            "template": theme
        }
        
        if viz_type == "bar":
            fig = px.bar(data, x=x_column, y=y_column, color=color_column, **kwargs)
            if orientation == "horizontal":
                fig.update_layout(barmode='relative')
        elif viz_type == "line":
            fig = px.line(data, x=x_column, y=y_column, color=color_column, **kwargs)
        elif viz_type == "scatter":
            fig = px.scatter(data, x=x_column, y=y_column, color=color_column, **kwargs)
        elif viz_type == "pie":
            fig = px.pie(data, values=y_column, names=x_column, title=title)
        elif viz_type == "heatmap":
            try:
                pivot_data = pd.pivot_table(data, values=y_column, index=x_column, 
                                          columns=color_column, aggfunc='mean')
                fig = px.imshow(pivot_data, title=title, aspect="auto")
            except Exception as e:
                return None, f"Error creating heatmap: {str(e)}"
        elif viz_type == "box":
            fig = px.box(data, x=x_column, y=y_column, color=color_column, **kwargs)
        
        if fig:
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
                    config={'displayModeBar': True}
                )
                return html_str, None
            except Exception as e:
                return None, f"Error generating visualization: {str(e)}"
        
        return None, "Failed to create visualization"
    
    except Exception as e:
        return None, f"Error creating visualization: {str(e)}"

def get_numeric_columns(df: pd.DataFrame) -> list:
    """Return list of numeric columns in the dataframe."""
    return df.select_dtypes(include=['int64', 'float64']).columns.tolist()

def get_categorical_columns(df: pd.DataFrame) -> list:
    """Return list of categorical columns in the dataframe."""
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

def get_available_themes() -> list:
    """Return list of available plotly themes."""
    return ['plotly', 'plotly_white', 'plotly_dark', 'ggplot2', 
            'seaborn', 'simple_white', 'presentation']
