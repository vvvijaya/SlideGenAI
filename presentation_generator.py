from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.shapes.base import BaseShape
from pptx.text.text import _Run
import pandas as pd
import tempfile
import os
import base64
from io import BytesIO
from typing import Optional, List, Dict, Union

def add_image_to_slide(slide, image_data: str, left: float, top: float, width: float, height: float) -> Union[BaseShape, None]:
    """Add an SVG image to the slide."""
    try:
        # Convert base64 string to bytes
        image_bytes = base64.b64decode(image_data)
        
        # Create a temporary file for the SVG
        temp_svg = tempfile.NamedTemporaryFile(delete=False, suffix='.svg')
        temp_svg.write(image_bytes)
        temp_svg.close()
        
        # Add image to slide
        left = Inches(left)
        top = Inches(top)
        width = Inches(width)
        height = Inches(height)
        
        try:
            pic = slide.shapes.add_picture(temp_svg.name, left, top, width, height)
            os.unlink(temp_svg.name)
            return pic
        except Exception as e:
            os.unlink(temp_svg.name)
            raise e
            
    except Exception as e:
        # If image addition fails, add a text box with error message
        txBox = slide.shapes.add_textbox(left, top, width, height)
        tf = txBox.text_frame
        tf.text = f"Visualization could not be added: {str(e)}"
        return None

def create_presentation(data: pd.DataFrame, summaries: List[str], visualizations: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Create a PowerPoint presentation with the processed data, AI summaries, and visualizations.
    """
    prs = Presentation()
    
    # Title Slide
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_shape = title_slide.shapes.title
    subtitle_shape = title_slide.placeholders[1]
    
    if title_shape and hasattr(title_shape, 'text_frame'):
        title_shape.text_frame.text = "Data Analysis Report"
    if subtitle_shape and hasattr(subtitle_shape, 'text_frame'):
        subtitle_shape.text_frame.text = "Generated with AI Insights"

    # Summary Slide
    summary_slide = prs.slides.add_slide(prs.slide_layouts[1])
    summary_title = summary_slide.shapes.title
    summary_content = summary_slide.placeholders[1]
    
    if summary_title and hasattr(summary_title, 'text_frame'):
        summary_title.text_frame.text = "Key Insights"
    if summary_content and hasattr(summary_content, 'text_frame'):
        summary_content.text_frame.text = "\n".join([f"• {summary}" for summary in summaries])

    # Visualization Slides
    if visualizations:
        for idx, viz in enumerate(visualizations):
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            slide_title = slide.shapes.title
            if slide_title and hasattr(slide_title, 'text_frame'):
                slide_title.text_frame.text = f"Visualization {idx + 1}"
            
            # Add visualization image using SVG data
            if 'svg' in viz:
                add_image_to_slide(slide, viz['svg'], left=1, top=2, width=8, height=5)

    # Data Slides
    for i in range(0, len(data), 5):  # 5 rows per slide
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        
        # Add title
        slide_title = slide.shapes.title
        if slide_title and hasattr(slide_title, 'text_frame'):
            slide_title.text_frame.text = "Data Analysis"
        
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
