import openai
import os
import pandas as pd
import streamlit as st
from typing import List, Optional
import time
from tenacity import retry, stop_after_attempt, wait_exponential

class AIError(Exception):
    """Custom exception for AI-related errors"""
    pass

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_openai_api(messages: List[dict], max_tokens: int = 150, temperature: float = 0.7) -> str:
    """
    Make API call to OpenAI with retry logic and error handling.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    except openai.error.AuthenticationError:
        raise AIError("Invalid API key. Please check your OpenAI API key.")
    except openai.error.RateLimitError:
        raise AIError("Rate limit exceeded. Please try again later.")
    except Exception as e:
        raise AIError(f"Error calling OpenAI API: {str(e)}")

def prepare_data_summary(df: pd.DataFrame) -> str:
    """
    Prepare a concise summary of the data for the AI.
    """
    try:
        summary = []
        summary.append(f"Columns: {', '.join(df.columns)}")
        summary.append(f"Number of rows: {len(df)}")
        
        # Add basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if not numeric_cols.empty:
            stats = df[numeric_cols].agg(['mean', 'min', 'max']).round(2)
            summary.append("\nNumeric column statistics:")
            for col in numeric_cols:
                summary.append(f"{col}: mean={stats.loc['mean', col]}, "
                             f"min={stats.loc['min', col]}, "
                             f"max={stats.loc['max', col]}")
        
        return "\n".join(summary)
    except Exception as e:
        raise AIError(f"Error preparing data summary: {str(e)}")

def generate_summary(data: pd.DataFrame) -> List[str]:
    """
    Generate AI-powered summaries from the processed data using OpenAI API.
    Includes enhanced error handling and retry logic.
    """
    if not isinstance(data, pd.DataFrame):
        raise AIError("Invalid input: data must be a pandas DataFrame")

    if data.empty:
        raise AIError("Cannot generate summary from empty dataset")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise AIError("OpenAI API key not found in environment variables")

    try:
        openai.api_key = api_key
        
        # Prepare data summary
        data_summary = prepare_data_summary(data)
        
        # Create messages for API call
        messages = [
            {"role": "system", "content": "You are a data analyst expert. Provide 3-5 key insights from the following data."},
            {"role": "user", "content": f"Please analyze this data and provide key insights:\n{data_summary}"}
        ]
        
        # Make API call with retry logic
        summary_text = call_openai_api(messages)
        
        # Process and validate the summary
        summaries = [s.strip() for s in summary_text.split('\n') if s.strip()]
        
        if not summaries:
            raise AIError("No valid insights generated")
        
        return summaries[:5]  # Limit to maximum 5 insights
        
    except AIError as e:
        st.error(str(e))
        return ["Unable to generate AI summary: " + str(e)]
    except Exception as e:
        st.error(f"Unexpected error in summary generation: {str(e)}")
        return ["An unexpected error occurred while generating the summary."]
