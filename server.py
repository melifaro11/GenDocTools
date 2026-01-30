"""
Main module for the GenFilesMCP server converted to FastAPI.

This module initializes the FastAPI server and defines endpoints for generating
Excel, Word, PowerPoint, and Markdown files using AI-generated Python scripts.
It also includes endpoints for analyzing and reviewing existing documents.
"""

# Native libraries
from os import getenv
from typing import Annotated, Literal, List, Tuple, Union, Any, Optional
import logging

# Third-party libraries
from fastapi import FastAPI, HTTPException, Request, Depends, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field, BaseModel, field_validator, model_validator
import uvicorn

# Utilities
from utils.load_md_templates import load_md_templates
from utils.argument_descriptions import ARGUMENT_DESCRIPTIONS

# Import tools from the tools directory
from tools.powerpoint_tool import generate_powerpoint as _generate_powerpoint
from tools.excel_tool import generate_excel as _generate_excel
from tools.markdown_tool import generate_markdown as _generate_markdown
from tools.docx_tool import full_context_docx as _full_context_docx, review_docx as _review_docx, generate_word_from_template as _generate_word_from_template

# Configure Logging
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger("GenFilesOpenAPI Tool Servers")

# Parameters
OWUI_URL = getenv('OWUI_URL', 'http://localhost:8080')
PORT = int(getenv('PORT', '8000'))
POWERPOINT_TEMPLATE, EXCEL_TEMPLATE, WORD_TEMPLATE, MARKDOWN_TEMPLATE, MCP_INSTRUCTIONS = load_md_templates()
ENABLE_CREATE_KNOWLEDGE = getenv('ENABLE_CREATE_KNOWLEDGE', 'true').lower() == 'true'

# Initialize FastAPI app
app = FastAPI(
    title="GenFiles OpenAPI Tool Server",
    version="0.3.0-alpha.4",
    description=MCP_INSTRUCTIONS,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mock Context for Compatibility ---
class MockRequest:
    def __init__(self, headers):
        self.headers = headers

class MockRequestContext:
    def __init__(self, request):
        self.request = request

class MockContext:
    def __init__(self, headers):
        self.request_context = MockRequestContext(MockRequest(headers))

def get_context(request: Request) -> MockContext:
    return MockContext(request.headers)

# --- Pydantic Models for Data Structures ---

class ReviewComment(BaseModel):
    index: int
    comment: str

class ImagesList(BaseModel):
    images: str

class Cover(BaseModel):
    title: str = Field("Document Title", description="The main title of the document.")
    subtitle: str = Field("", description="The subtitle of the document.")
    description: str = Field("Document Description", description="A brief description of the document.")
    author: str = Field("Author Name", description="The author's name.")
    month: str = Field("January", description="The month of publication (e.g., 'January').")
    year: str = Field("2024", description="The year of publication (e.g., '2024').")
    page_break: bool = Field(False, description="Whether to add a page break after the cover.")

class ParagraphListItem(BaseModel):
    type: Literal["ParagraphListItem"] = Field("ParagraphListItem", description="Discriminator for the list item element.")
    list_style: Literal['List Number', 'List Bullet'] = Field("List Bullet", description="The style of the list: 'List Number' or 'List Bullet'.")
    items: List[str] = Field(["Item 1", "Item 2", "Item 3"], description="A list of text items.")

class Table(BaseModel):
    type: Literal["Table"] = Field("Table", description="Discriminator for the table element.")
    headers: List[str] = Field(["Header 1", "Header 2", "Header 3"], description="List of table headers.")
    rows: List[List[str]] = Field([["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"]], description="List of rows, where each row is a list of cell values.")
    caption: str = Field("Table 1 Caption", description="Caption for the table.")

class Image(BaseModel):
    type: Literal["Image"] = Field("Image", description="Discriminator for the image element.")
    id: Optional[str] = Field(None, description="The image file ID.")
    caption: str = Field("Fig. 1. Caption", description="Caption for the image.")

class Equation(BaseModel):
    type: Literal["Equation"] = Field("Equation", description="Discriminator for the equation element.")
    latex: str = Field(..., description="The LaTeX code for the equation.")
    caption: str = Field("Equation 1 Caption", description="Caption for the equation.")

class ParagraphHeader(BaseModel):
    type: Literal["ParagraphHeader"] = Field("ParagraphHeader", description="Discriminator for the header element.")
    text: str = Field(..., description="The content of the heading.")
    level: Literal[1,2,3,4,5,6] = Field(2, description="The heading level (1-6).")

class ParagraphBody(BaseModel):
    type: Literal["ParagraphBody"] = Field("ParagraphBody", description="Discriminator for the paragraph element.")
    text: str = Field("", description="The text content of the paragraph. Do NOT use Markdown.")

class WordsWithBoldOrItalic(BaseModel):
    type: Literal["WordsWithBoldOrItalic"] = Field("WordsWithBoldOrItalic", description="Discriminator for bold/italic text element.")
    text: str = Field("", description="The text to format.")
    bold: bool = Field(False, description="Whether to apply bold formatting.")
    italic: bool = Field(False, description="Whether to apply italic formatting.")

# --- Request Models for Endpoints ---

class DocxElement(BaseModel):
    type: Literal["ParagraphHeader", "ParagraphBody", "ParagraphListItem", "Table", "Image", "Equation", "WordsWithBoldOrItalic"] = Field(..., description="The type of the element.")
    
    # Header/Body/Bold fields
    text: Optional[str] = Field(None, description="Required for ParagraphHeader type, ParagraphBody type, WordsWithBoldOrItalic type.")
    level: Optional[int] = Field(None, description="Required for ParagraphHeader type (1-6).")
    
    # Body/Bold fields
    bold: Optional[bool] = Field(None, description="Optional for WordsWithBoldOrItalic type.")
    italic: Optional[bool] = Field(None, description="Optional for WordsWithBoldOrItalic type.")
    
    # List fields
    list_style: Optional[Literal["List Number", "List Bullet"]] = Field(None, description="Required for ParagraphListItem type ('List Number' or 'List Bullet').")
    items: Optional[List[str]] = Field(None, description="Required for ParagraphListItem type.")
    
    # Table fields
    headers: Optional[List[str]] = Field(None, description="Required for Table type.")
    rows: Optional[List[List[str]]] = Field(None, description="Required for Table type.")
    
    # Image/Equation/Table common
    caption: Optional[str] = Field(None, description="Optional for Table type, Image type, Equation type.")
    
    # Image fields
    id: Optional[str] = Field(None, description="Required for Image type.")
    
    # Equation fields
    latex: Optional[str] = Field(None, description="Required for Equation type.")

    @model_validator(mode='after')
    def validate_type_fields(self) -> 'DocxElement':
        if self.type == "ParagraphHeader":
            if not self.text: raise ValueError("text is required for ParagraphHeader type")
            if not self.level: raise ValueError("level is required for ParagraphHeader type")
        elif self.type == "ParagraphBody":
            if self.text is None: raise ValueError("text is required for ParagraphBody type")
        elif self.type == "ParagraphListItem":
            if not self.items: raise ValueError("items is required for ParagraphListItem type")
        elif self.type == "Table":
            if not self.headers: raise ValueError("headers is required for Table type")
            if not self.rows: raise ValueError("rows is required for Table type")
        elif self.type == "Image":
            if not self.id: raise ValueError("id is required for Image type")
        elif self.type == "Equation":
            if not self.latex: raise ValueError("latex is required for Equation type")
        elif self.type == "WordsWithBoldOrItalic":
            if self.text is None: raise ValueError("text is required for WordsWithBoldOrItalic type")
        return self

class GeneratePowerPointRequest(BaseModel):
    python_script: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["python_script"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])

class GenerateExcelRequest(BaseModel):
    python_script: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["python_script"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])

class GenerateMarkdownRequest(BaseModel):
    python_script: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["python_script"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])

class DocxBodyElements(BaseModel):
    document_cover: Cover = Field(description="This argument defines the cover page of the document. Set page_break to True for generating general reports and False for academic papers. Backend is able to center the cover page content automatically so no need to add extra spaces or new lines.")
    columns_body: int = Field(description="This argument defines the number of columns in the document body. Set to 1 for single column or 2 for double column layout for academic papers.")
    document_body_elements: List[DocxElement] = Field(description="This argument defines the body elements of the document. The order of elements in the list defines the order in the document body.")
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])

class FullContextDocxRequest(BaseModel):
    file_id: str = Field(description=ARGUMENT_DESCRIPTIONS["full_context_docx"]["file_id"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["full_context_docx"]["file_name"])

class ReviewDocxRequest(BaseModel):
    file_id: str = Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["file_id"])
    review_comments: List[ReviewComment] = Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["review_comments"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["file_name"])


# --- Endpoints ---

@app.post(
    "/generate_powerpoint", 
    summary="Generate PowerPoint", 
    description=POWERPOINT_TEMPLATE,
    operation_id="generate_powerpoint_presentation"
)
def generate_powerpoint(request: Request, body: GeneratePowerPointRequest):
    ctx = get_context(request)
    return _generate_powerpoint(body.python_script, body.file_name, ctx, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)

@app.post(
    "/generate_excel", 
    summary="Generate Excel", 
    description=EXCEL_TEMPLATE,
    operation_id="generate_excel_workbook"
)
def generate_excel(request: Request, body: GenerateExcelRequest):
    ctx = get_context(request)
    return _generate_excel(body.python_script, body.file_name, ctx, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)

@app.post(
    "/generate_markdown", 
    summary="Generate Markdown", 
    description=MARKDOWN_TEMPLATE,
    operation_id="generate_markdown_document"
)
def generate_markdown(request: Request, body: GenerateMarkdownRequest):
    ctx = get_context(request)
    return _generate_markdown(body.python_script, body.file_name, ctx, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)

@app.post(
    "/generate_word", 
    summary="Generate Word", 
    description=WORD_TEMPLATE,
    operation_id="generate_word_document"
)
def generate_word(request: Request, body: DocxBodyElements):
    ctx = get_context(request)
    return _generate_word_from_template(body.document_cover, body.columns_body, body.document_body_elements, body.file_name, ctx, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)

@app.post(
    "/list_docx_elements", 
    summary="Return the structure of a docx document",
    operation_id="list_docx_elements"
)
def full_context_docx(request: Request, body: FullContextDocxRequest):
    ctx = get_context(request)
    return _full_context_docx(body.file_id, body.file_name, ctx, OWUI_URL)

@app.post(
    "/review_docx", 
    summary="Review and comment on docx document",
    operation_id="review_docx_document"
)
def review_docx(request: Request, body: ReviewDocxRequest):
    ctx = get_context(request)
    return _review_docx(body.file_id, body.file_name, body.review_comments, ctx, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
