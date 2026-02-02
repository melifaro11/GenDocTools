
from pydantic import BaseModel
from typing import List, Literal, Optional
from pydantic import Field, BaseModel, model_validator

# --- Models for review comments and document elements ---
class ReviewComment(BaseModel):
    index: int
    comment: str

class ImagesList(BaseModel):
    images: str

# --- Models for docx document structure --- 
class Cover(BaseModel):
    title: str = Field(..., description="The main title of the document.")
    subtitle: str = Field(..., description="The subtitle of the document.")
    description: str = Field(..., description="A brief description of the document.")
    author: str = Field(..., description="The author's name.")
    month: str = Field(..., description="The month of publication (e.g., 'January').")
    year: str = Field(..., description="The year of publication (e.g., '2024').")
    page_break: bool = Field(..., description="Whether to add a page break after the cover.")

class ParagraphListItem(BaseModel):
    type: Literal["ParagraphListItem"] = Field(..., description="Discriminator for the list item element.")
    list_style: Literal['List Number', 'List Bullet'] = Field(..., description="The style of the list: 'List Number' or 'List Bullet'.")
    items: List[str] = Field(..., description="A list of text items.")
    index_element: int = Field(..., description="Unique index across all document elements for global ordering in the document. Values must be unique integers starting from 1 or higher, and do not need to be consecutive.")

class Table(BaseModel):
    type: Literal["Table"] = Field(..., description="Discriminator for the table element.")
    table_headers: List[str] = Field(..., description="List of table headers.")
    table_rows: List[List[str]] = Field(..., description="List of rows, where each row is a list of cell values.")
    caption: str = Field(..., description="Caption for the table.")
    index_element: int = Field(..., description="Unique index across all document elements for global ordering in the document. Values must be unique integers starting from 1 or higher, and do not need to be consecutive.")

class Image(BaseModel):
    type: Literal["Image"] = Field(..., description="Discriminator for the image element.")
    id: str = Field(..., description="The image file ID.")
    caption: str = Field(..., description="Caption for the image.")
    index_element: int = Field(..., description="Unique index across all document elements for global ordering in the document. Values must be unique integers starting from 1 or higher, and do not need to be consecutive.")

class Equation(BaseModel):
    type: Literal["Equation"] = Field(..., description="Discriminator for the equation element.")
    latex: str = Field(..., description="The LaTeX code for the equation.")
    caption: str = Field(..., description="Caption for the equation.")
    index_element: int = Field(..., description="Unique index across all document elements for global ordering in the document. Values must be unique integers starting from 1 or higher, and do not need to be consecutive.")

class ParagraphHeader(BaseModel):
    type: Literal["ParagraphHeader"] = Field(..., description="Discriminator for the header element.")
    text: str = Field(..., description="The text content of the heading. Use plain text only.")
    level: Literal[1,2,3,4,5,6] = Field(..., description="The heading level (1-6).")
    index_element: int = Field(..., description="Unique index across all document elements for global ordering in the document. Values must be unique integers starting from 1 or higher, and do not need to be consecutive.")

class ParagraphBody(BaseModel):
    type: Literal["ParagraphBody"] = Field(..., description="Discriminator for the paragraph element.")
    text: str = Field(..., description="The text content of the paragraph. Use **bold** for bold text and *italic* for italic text.")
    index_element: int = Field(..., description="Unique index across all document elements for global ordering in the document. Values must be unique integers starting from 1 or higher, and do not need to be consecutive.")

# --- Composite DocxElement Model ---
# Removed: Now using separate lists for each type with index_element for ordering.