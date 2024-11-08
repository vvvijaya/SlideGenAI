import streamlit as st

def apply_styles():
    """
    Apply consistent styling to the Streamlit app.
    """
    st.set_page_config(
        page_title="AI Presentation Generator",
        page_icon="📊",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        .stSelectbox {
            margin-bottom: 1rem;
        }
        .stMultiSelect {
            margin-bottom: 1rem;
        }
        h1 {
            margin-bottom: 2rem;
        }
        h2 {
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .stAlert {
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
