import openai
import os
import pandas as pd

def generate_summary(data: pd.DataFrame) -> list:
    """
    Generate AI-powered summaries from the processed data using OpenAI API.
    """
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    
    # Convert DataFrame to string representation
    data_str = data.to_string()
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a data analyst expert. Provide 3-5 key insights from the following data."},
                {"role": "user", "content": f"Please analyze this data and provide key insights:\n{data_str}"}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        # Extract and process the summary
        summary_text = response.choices[0].message.content
        summaries = [s.strip() for s in summary_text.split('\n') if s.strip()]
        
        return summaries
        
    except Exception as e:
        return ["Unable to generate AI summary. Please check your data and try again."]
