import streamlit as st
import pandas as pd
from data_processor import process_data
from presentation_generator import create_presentation
from ai_summarizer import generate_summary
from utils import load_data, validate_file
from styles import apply_styles

def main():
    apply_styles()
    
    st.title("AI-Powered Presentation Generator")
    st.write("Upload your data and create professional presentations automatically")

    # File Upload Section
    st.header("1. Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        try:
            # Load and validate data
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

                # Generate Presentation
                if st.button("Generate Presentation"):
                    with st.spinner("Processing data..."):
                        # Process data
                        processed_data = process_data(df, group_cols, agg_methods)
                        
                        # Generate AI summaries
                        summaries = generate_summary(processed_data)
                        
                        # Create presentation
                        pptx_file = create_presentation(processed_data, summaries)
                        
                        # Offer download
                        st.success("Presentation generated successfully!")
                        with open(pptx_file, "rb") as file:
                            st.download_button(
                                label="Download Presentation",
                                data=file,
                                file_name="presentation.pptx",
                                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                            )

        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
