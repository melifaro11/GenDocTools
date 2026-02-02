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
from utils.argument_descriptions import ASCII_INFO
from utils.pydantic_models_endpoints import (
    GeneratePowerPointRequest,
    GenerateExcelRequest,
    GenerateMarkdownRequest,
    DocxBodyElements,
    FullContextDocxRequest,
    ReviewDocxRequest
)

# Import tools from the tools directory
from tools.powerpoint_tool import generate_powerpoint as _generate_powerpoint
from tools.excel_tool import generate_excel as _generate_excel
from tools.markdown_tool import generate_markdown as _generate_markdown
from tools.docx_tool import full_context_docx as _full_context_docx, review_docx as _review_docx, generate_word_from_template as _generate_word_from_template

# Configure Logging
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger("Gen Files OpenAPI Tool Server")

# Parameters
OWUI_URL = getenv('OWUI_URL', 'http://localhost:8080')
PORT = int(getenv('PORT', '8000'))
POWERPOINT_TEMPLATE, EXCEL_TEMPLATE, WORD_TEMPLATE, MARKDOWN_TEMPLATE, MCP_INSTRUCTIONS = load_md_templates()
ENABLE_CREATE_KNOWLEDGE = getenv('ENABLE_CREATE_KNOWLEDGE', 'true').lower() == 'true'

# Initialize FastAPI app
app = FastAPI(
    title="Gen Files OpenAPI Tool Server",
    version="0.3.0-alpha.5",
    description=MCP_INSTRUCTIONS,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API endpoints ---

@app.post(
    "/generate_powerpoint", 
    summary="Generate PowerPoint", 
    description=POWERPOINT_TEMPLATE,
    operation_id="generate_powerpoint_presentation"
)
def generate_powerpoint(request: Request, body: GeneratePowerPointRequest):
    """Generates a PowerPoint presentation using a provided Python script."""
    return _generate_powerpoint(body.python_script, body.file_name, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)
 
@app.post(
    "/generate_excel", 
    summary="Generate Excel", 
    description=EXCEL_TEMPLATE,
    operation_id="generate_excel_workbook"
)
def generate_excel(request: Request, body: GenerateExcelRequest):
    """Generates an Excel workbook using a provided Python script."""
    return _generate_excel(body.python_script, body.file_name, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)

@app.post(
    "/generate_markdown", 
    summary="Generate Markdown", 
    description=MARKDOWN_TEMPLATE,
    operation_id="generate_markdown_document"
)
def generate_markdown(request: Request, body: GenerateMarkdownRequest):
    """Generates a Markdown document using a provided Python script."""
    return _generate_markdown(body.python_script, body.file_name, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)

@app.post(
    "/generate_word", 
    summary="Generate Word", 
    description=WORD_TEMPLATE,
    operation_id="generate_word_document"
)
def generate_word(request: Request, body: DocxBodyElements):
    """Generates a Word document using provided metadata and body elements."""
    # Collect all elements
    all_elements = []
    all_elements.extend(body.document_paragraphs)
    all_elements.extend(body.document_headers)
    all_elements.extend(body.document_lists)
    all_elements.extend(body.document_tables)
    all_elements.extend(body.document_images)
    all_elements.extend(body.document_equations)
    
    if not all_elements:
        return {"error": {"message": "No document elements provided. Please include content in document_paragraphs, document_headers, or other lists."}}
    
    # Sort by index_element
    all_elements.sort(key=lambda x: x.index_element)
    
    return _generate_word_from_template(body.document_cover, body.columns_body, all_elements, body.file_name, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)

@app.post(
    "/list_docx_elements", 
    summary="Return the structure of a docx document",
    operation_id="list_docx_elements"
)
def full_context_docx(request: Request, body: FullContextDocxRequest):
    """Returns the structure of a DOCX document, including index, style, and text of each element."""
    return _full_context_docx(body.file_id, body.file_name, request, OWUI_URL)

@app.post(
    "/review_docx", 
    summary="Review and comment on docx document",
    operation_id="review_docx_document"
)
def review_docx(request: Request, body: ReviewDocxRequest):
    """Reviews an existing DOCX document and adds comments to specific elements."""
    return _review_docx(body.file_id, body.file_name, body.review_comments, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)

# --- Main ---
if __name__ == "__main__":
    logger.info(ASCII_INFO)
    uvicorn.run(app, host="0.0.0.0", port=PORT)
