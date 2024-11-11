import streamlit as st
import pandas as pd
from data_processor import process_data
from presentation_generator import create_presentation
from ai_summarizer import generate_summary
from utils import load_data, validate_file
from styles import apply_styles
from visualizations import (create_visualization, get_numeric_columns, 
                          get_categorical_columns, get_available_themes)
import asyncio
import logging
from typing import Optional
import traceback
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def handle_error(error: Exception, message: str) -> None:
    """Handle errors with proper logging and user feedback."""
    error_msg = f"{message}: {str(error)}"
    logger.error(f"{error_msg}\n{traceback.format_exc()}")
    st.error(error_msg)

def initialize_session_state():
    """Initialize session state variables with proper error handling."""
    try:
        if 'ai_summaries' not in st.session_state:
            st.session_state.ai_summaries = []
        if 'visualizations' not in st.session_state:
            st.session_state.visualizations = []
        if 'error_log' not in st.session_state:
            st.session_state.error_log = []
        if 'processing_state' not in st.session_state:
            st.session_state.processing_state = None
    except Exception as e:
        handle_error(e, "Error initializing session state")
        st.error("Failed to initialize application state. Please refresh the page.")
        st.stop()

async def create_visualization_with_loading(viz_data: pd.DataFrame, viz_type: str, x_col: str, y_col: str,
                                          color_col: Optional[str], title: str, x_label: str, y_label: str,
                                          theme: str, show_grid: bool, show_legend: bool,
                                          orientation: str, animation_col: Optional[str]) -> tuple:
    """Create visualization with loading state and error handling."""
    try:
        with st.spinner("Generating visualization..."):
            viz_html, viz_svg, viz_png, error = await create_visualization(
                viz_data, viz_type, x_col, y_col, color_col,
                title, x_label, y_label, theme,
                show_grid=show_grid, show_legend=show_legend,
                orientation=orientation, animation_frame=animation_col
            )
            return viz_html, viz_svg, viz_png, error
    except Exception as e:
        handle_error(e, "Error creating visualization")
        return None, None, None, str(e)

def main():
    try:
        # Initialize session state
        initialize_session_state()
        
        # Apply styles with error handling
        try:
            apply_styles()
        except Exception as e:
            handle_error(e, "Error applying styles")
        
        st.title("AI-Powered Presentation Generator")
        st.write("Upload your data and create professional presentations automatically")

        # File Upload Section with improved error handling
        st.header("1. Upload Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file", 
            type=['csv', 'xlsx'],
            help="Maximum file size: 200MB",
            on_change=lambda: setattr(st.session_state, 'processing_state', None)
        )

        if uploaded_file is not None:
            try:
                # Validate file first
                is_valid, error_message = validate_file(uploaded_file)
                if not is_valid:
                    st.error(error_message)
                    st.stop()

                # Load and validate data with loading state
                with st.spinner("Loading and validating data..."):
                    df = load_data(uploaded_file)
                    
                if df is not None:
                    st.success("Data loaded successfully!")
                    st.dataframe(df.head())

                    # Configuration Section
                    st.header("2. Configure Presentation")
                    
                    # Select columns for grouping
                    group_cols = st.multiselect(
                        "Select columns for grouping",
                        options=df.columns.tolist(),
                        help="Select one or more columns to group your data"
                    )

                    # Select aggregation columns and methods
                    agg_cols = st.multiselect(
                        "Select columns to aggregate",
                        options=[col for col in df.columns if col not in group_cols]
                    )

                    agg_methods = {}
                    for col in agg_cols:
                        method = st.selectbox(
                            f"Aggregation method for {col}",
                            options=['sum', 'mean', 'count', 'min', 'max'],
                            key=f"agg_{col}"
                        )
                        agg_methods[col] = method

                    # Add custom prompt for AI analysis
                    custom_prompt = st.text_area(
                        "Custom prompt for AI analysis (optional)",
                        value="Analyze this data and provide key insights",
                        help="Enter your specific instructions for the AI analysis"
                    )

                    # AI Summary Generation with enhanced error handling
                    if st.button("Generate AI Summary"):
                        with st.spinner("Processing data and generating AI insights..."):
                            try:
                                processed_data = process_data(df, group_cols, agg_methods)
                                if processed_data is not None:
                                    summaries = generate_summary(processed_data, custom_prompt)
                                    if summaries and not any("error" in s.lower() for s in summaries):
                                        st.session_state.ai_summaries = summaries
                                        st.success("AI insights generated successfully!")
                                    else:
                                        st.error("Failed to generate meaningful insights. Please try adjusting your data selection.")
                                else:
                                    st.error("Error: Data processing failed. Please check your grouping and aggregation settings.")
                            except Exception as e:
                                handle_error(e, "Error generating AI insights")
                                st.session_state.ai_summaries = []
                                st.warning("Please try again with different settings or contact support if the issue persists.")

                    # Display AI Summaries with error handling
                    if st.session_state.ai_summaries:
                        with st.expander("View AI Insights", expanded=True):
                            for idx, summary in enumerate(st.session_state.ai_summaries, 1):
                                st.markdown(f"{idx}. {summary}")

                    # Visualization Section with improved error handling
                    st.header("3. Configure Visualizations")
                    
                    selected_columns = group_cols + list(agg_methods.keys())
                    if not selected_columns:
                        st.warning("Please select columns for grouping and/or aggregation in Section 2 before configuring visualizations.")
                        st.stop()

                    viz_container = st.container()
                    num_visualizations = st.number_input("Number of visualizations", min_value=0, max_value=5, value=1)
                    
                    # Global visualization settings
                    st.subheader("Global Visualization Settings")
                    theme = st.selectbox(
                        "Select theme",
                        options=get_available_themes(),
                        help="Choose a theme for all visualizations"
                    )
                    
                    selected_numeric_cols = [col for col in selected_columns if col in get_numeric_columns(df)]
                    
                    for i in range(num_visualizations):
                        try:
                            with viz_container:
                                st.subheader(f"Visualization {i+1}")
                                
                                viz_type = st.selectbox(
                                    "Select visualization type",
                                    options=["bar", "line", "scatter", "pie", "heatmap", "box"],
                                    key=f"viz_type_{i}",
                                    help="Choose the type of visualization"
                                )
                                
                                title = st.text_input("Chart title", key=f"title_{i}")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    x_col = st.selectbox(
                                        "Select X-axis column",
                                        options=selected_columns,
                                        key=f"x_col_{i}"
                                    )
                                    x_label = st.text_input("X-axis label", value=x_col, key=f"x_label_{i}")
                                
                                with col2:
                                    y_options = selected_numeric_cols if viz_type != "pie" else selected_columns
                                    y_col = st.selectbox(
                                        "Select Y-axis column",
                                        options=y_options,
                                        key=f"y_col_{i}"
                                    )
                                    y_label = st.text_input("Y-axis label", value=y_col, key=f"y_label_{i}")
                                
                                color_col = None
                                if viz_type in ["bar", "line", "scatter", "box", "heatmap"]:
                                    color_options = ["None"] + group_cols
                                    color_col = st.selectbox(
                                        "Select color/group column (optional)",
                                        options=color_options,
                                        key=f"color_col_{i}"
                                    )
                                    if color_col == "None":
                                        color_col = None
                                
                                # Advanced Options
                                with st.expander("Advanced Options"):
                                    if viz_type in ["scatter", "bar", "line"]:
                                        animation_col = st.selectbox(
                                            "Animation frame column (optional)",
                                            options=["None"] + group_cols,
                                            key=f"animation_{i}"
                                        )
                                        if animation_col == "None":
                                            animation_col = None
                                    else:
                                        animation_col = None
                                    
                                    show_grid = st.checkbox("Show Grid", value=True, key=f"grid_{i}")
                                    show_legend = st.checkbox("Show Legend", value=True, key=f"legend_{i}")
                                    
                                    if viz_type in ["bar", "scatter", "line"]:
                                        orientation = st.selectbox(
                                            "Chart Orientation",
                                            options=["vertical", "horizontal"],
                                            key=f"orientation_{i}"
                                        )
                                    else:
                                        orientation = "vertical"
                                
                                # Preview visualization with enhanced error handling
                                if st.button("Preview", key=f"preview_{i}"):
                                    try:
                                        viz_data = process_data(df, group_cols, agg_methods) if group_cols else df
                                        if viz_data is not None:
                                            viz_html, viz_svg, viz_png, error_msg = asyncio.run(create_visualization_with_loading(
                                                viz_data, viz_type, x_col, y_col, color_col,
                                                title, x_label, y_label, theme,
                                                show_grid=show_grid, show_legend=show_legend,
                                                orientation=orientation, animation_col=animation_col
                                            ))
                                            
                                            if viz_html:
                                                st.components.v1.html(viz_html, height=600)
                                                st.session_state.visualizations.append({
                                                    'html': viz_html,
                                                    'svg': viz_svg
                                                })
                                            else:
                                                st.error(error_msg or "Failed to create visualization. Please check your settings.")
                                        else:
                                            st.error("Failed to process data for visualization. Please check your settings.")
                                    except Exception as e:
                                        handle_error(e, f"Error previewing visualization")
                        except Exception as e:
                            handle_error(e, f"Error configuring visualization {i+1}")

                    # Generate Presentation with enhanced error handling
                    if st.button("Generate Presentation"):
                        with st.spinner("Processing data and generating presentation..."):
                            try:
                                processed_data = process_data(df, group_cols, agg_methods)
                                if processed_data is not None:
                                    summaries = st.session_state.ai_summaries
                                    if not summaries:
                                        summaries = generate_summary(processed_data, custom_prompt)
                                        st.session_state.ai_summaries = summaries
                                    
                                    if summaries and st.session_state.visualizations:
                                        pptx_file = create_presentation(processed_data, summaries, st.session_state.visualizations)
                                        
                                        st.success("Presentation generated successfully!")
                                        with open(pptx_file, "rb") as file:
                                            st.download_button(
                                                label="Download Presentation",
                                                data=file,
                                                file_name="presentation.pptx",
                                                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                                            )
                                    else:
                                        st.error("Please generate AI insights and create at least one visualization before generating the presentation.")
                                else:
                                    st.error("Error processing data. Please check your settings and try again.")
                            except Exception as e:
                                handle_error(e, "Error generating presentation")
            except Exception as e:
                handle_error(e, "Error processing uploaded file")
    except Exception as e:
        handle_error(e, "Application error")

if __name__ == "__main__":
    main()