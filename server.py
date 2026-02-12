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

def has_long_consecutive_run(nums, max_run=3):
    if not nums or len(nums) < max_run + 1:
        return False
    nums = sorted(set(nums))
    current_run = 1
    for i in range(1, len(nums)):
        if nums[i] == nums[i-1] + 1:
            current_run += 1
            if current_run > max_run:
                return True
        else:
            current_run = 1
    return False

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
    # Collect all elements (flatten nested dicts)
    all_elements = []
    raw_elements = []
    raw_elements.extend(body.document_elements)
    for e in raw_elements:
        # print("Raw element:", e)
        # print("type:", type(e))
        # print("hasattr model_dump:", hasattr(e, 'model_dump'))
        # if hasattr(e, 'model_dump'):
        #     print("model_dump:", e.model_dump())
        # aux_dict = {}
        aux_dict = {}
        aux_dict['index_element'] = e.index_element
        aux_dict['type'] = e.type
        if e.paragraph is not None:
            aux_dict['text'] = e.paragraph.text
        if e.header is not None:
            aux_dict['text'] = e.header.text
            aux_dict['level'] = e.header.level
        if e.list_item is not None:
            aux_dict['list_style'] = e.list_item.list_style
            aux_dict['items'] = e.list_item.items
        if e.table is not None:
            aux_dict['table_headers'] = e.table.table_headers
            aux_dict['table_rows'] = e.table.table_rows
            aux_dict['caption'] = e.table.caption
        if e.image is not None:
            aux_dict['id'] = e.image.id
            aux_dict['caption'] = e.image.caption
        if e.equation is not None:
            aux_dict['latex'] = e.equation.latex
            aux_dict['caption'] = e.equation.caption
        all_elements.append(aux_dict)
        print("aux_dict:", aux_dict)
        # Convert to dict if it's a model instance
    #     if isinstance(e, dict):
    #         elem_dict = e
    #     else:
    #         elem_dict = e.model_dump()
        
    #     flat_elem = {"index_element": elem_dict["index_element"], "type": elem_dict["type"]}
    #     # Find the non-None subfield and merge its contents
    #     if "paragraph" in elem_dict and elem_dict["paragraph"] is not None:
    #         flat_elem.update(elem_dict["paragraph"])
    #     elif "header" in elem_dict and elem_dict["header"] is not None:
    #         flat_elem.update(elem_dict["header"])
    #     elif "list_item" in elem_dict and elem_dict["list_item"] is not None:
    #         flat_elem.update(elem_dict["list_item"])
    #     elif "table" in elem_dict and elem_dict["table"] is not None:
    #         flat_elem.update(elem_dict["table"])
    #     elif "image" in elem_dict and elem_dict["image"] is not None:
    #         flat_elem.update(elem_dict["image"])
    #     elif "equation" in elem_dict and elem_dict["equation"] is not None:
    #         flat_elem.update(elem_dict["equation"])
    #     all_elements.append(flat_elem)
    # all_elements.sort(key=lambda x: x["index_element"])

    # all_elements.extend(body.document_headers)
    # all_elements.extend(body.document_lists)
    # all_elements.extend(body.document_tables)
    # all_elements.extend(body.document_images)
    # all_elements.extend(body.document_equations)
    
    # # Check for long consecutive runs in each list
    # lists_to_check = [
    #     ("document_paragraphs", body.document_paragraphs),
    #     ("document_headers", body.document_headers),
    #     ("document_lists", body.document_lists),
    #     ("document_tables", body.document_tables),
    #     ("document_images", body.document_images),
    #     ("document_equations", body.document_equations),
    # ]
    # for list_name, elements in lists_to_check:
    #     if elements:
    #         # check if the elements are not None before extracting index_element
    #         indices = [e.index_element for e in elements if e is not None]
    #         if has_long_consecutive_run(indices):
    #             element_type = list_name.replace('document_', '').replace('_', ' ')
    #             return {"error": {"message": f"Oops! Found more than 3 consecutive index_element values in {list_name}. This could result in pages or sections with only {element_type} (e.g., all headers or all paragraphs), which isn't varied or readable for humans. All elements are combined and sorted by index_element to build the document body in logical order, so space out the indices to mix content types."}}
    
    # # Check for duplicate index_element
    # indexes = [elem.index_element for elem in all_elements]
    # if len(indexes) != len(set(indexes)):
    #     return {"error": {"message": "Oops! There are duplicate index_element values. Each element in document_paragraphs, document_headers, document_lists, document_tables, document_images, and document_equations must have a unique index_element (starting from 1, like 1, 2, 3, etc.). The document is built by sorting all these elements by their index_element in ascending order, which defines the logical order of the document body."}}
    
    # if not all_elements:
    #     return {"error": {"message": "No document elements provided. Please include content in document_paragraphs, document_headers, or other lists."}}
    
    # # Sort by index_element
    # all_elements.sort(key=lambda x: x.index_element)
    
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
