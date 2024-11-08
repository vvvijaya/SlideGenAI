from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
import pandas as pd
import tempfile
import os
import base64
from io import BytesIO

def add_image_to_slide(slide, image_base64: str, left: float, top: float, width: float, height: float):
    """Add a base64 encoded SVG image to the slide."""
    try:
        image_data = base64.b64decode(image_base64)
        image_stream = BytesIO(image_data)
        slide.shapes.add_picture(image_stream, Inches(left), Inches(top), Inches(width), Inches(height))
    except Exception as e:
        # If image addition fails, add a text box with error message
        left = Inches(left)
        top = Inches(top)
        width = Inches(width)
        height = Inches(height)
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.text = "Visualization could not be added to the slide"

def create_presentation(data: pd.DataFrame, summaries: list, visualizations: list = None) -> str:
    """
    Create a PowerPoint presentation with the processed data, AI summaries, and visualizations.
    """
    prs = Presentation()
    
    # Title Slide
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title = title_slide.shapes.title
    subtitle = title_slide.placeholders[1]
    title.text = "Data Analysis Report"
    subtitle.text = "Generated with AI Insights"

    # Summary Slide
    summary_slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = summary_slide.shapes.title
    content = summary_slide.placeholders[1]
    title.text = "Key Insights"
    content.text = "\n".join([f"• {summary}" for summary in summaries])

    # Visualization Slides
    if visualizations:
        for idx, viz in enumerate(visualizations):
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            title = slide.shapes.title
            title.text = f"Visualization {idx + 1}"
            
            # Add visualization image
            add_image_to_slide(slide, viz, left=1, top=2, width=8, height=5)

    # Data Slides
    for i in range(0, len(data), 5):  # 5 rows per slide
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        
        # Add title
        title = slide.shapes.title
        title.text = "Data Analysis"
        
        # Add table
        rows = min(6, len(data) - i + 1)  # +1 for header
        cols = len(data.columns)
        left = Inches(1)
        top = Inches(2)
        width = Inches(8)
        height = Inches(0.8 * rows)
        
        table = slide.shapes.add_table(rows, cols, left, top, width, height).table
        
        # Add headers
        for j, col in enumerate(data.columns):
            cell = table.cell(0, j)
            cell.text = str(col)
            
        # Add data
        for row in range(rows-1):
            if i + row < len(data):
                for col in range(cols):
                    cell = table.cell(row+1, col)
                    cell.text = str(data.iloc[i + row, col])

    # Save presentation
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pptx')
    prs.save(temp_file.name)
    return temp_file.name
