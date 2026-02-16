# Native libraries
from json import dumps
from os import getenv
from typing import Annotated, Literal, List, Tuple, Union, Any, Optional

# Third-party libraries
from fastmcp import FastMCP,  Context
from fastmcp.server.dependencies import get_http_headers
import uvicorn

# Utilities
from utils.logger import configure_logging, get_logger
configure_logging()
from utils.load_md_templates import load_md_templates
from utils.argument_descriptions import SERVER_BANNER, MCP_SERVER_NAME, SERVER_VERSION
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

# Parameters
OWUI_URL = getenv('OWUI_URL', 'http://localhost:8080')
PORT = int(getenv('PORT', '8000'))
REVIEWER_AI_ASSISTANT_NAME = getenv('REVIEWER_AI_ASSISTANT_NAME', 'GenFilesMCP')
POWERPOINT_TEMPLATE, EXCEL_TEMPLATE, WORD_TEMPLATE, MARKDOWN_TEMPLATE, MCP_INSTRUCTIONS = load_md_templates()
ENABLE_CREATE_KNOWLEDGE = getenv('ENABLE_CREATE_KNOWLEDGE', 'true').lower() == 'true'

# Initialize FastMCP server
mcp = FastMCP(
    name = MCP_SERVER_NAME,
    instructions = MCP_INSTRUCTIONS,   
)

# Configure Logging
logger = get_logger(MCP_SERVER_NAME)

@mcp.tool(
    name = "generate_powerpoint",
    title = "Generate PowerPoint",
    description = POWERPOINT_TEMPLATE
)
async def generate_powerpoint(
    body: GeneratePowerPointRequest
):
    """Generates a PowerPoint presentation using a provided Python script."""
    logger.info("Received request to generate PowerPoint presentation")

    try:
        # headers
        request = {"headers": get_http_headers()}
        return _generate_powerpoint(body.python_script, body.file_name, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)
    except Exception as e:
        logger.error(f"Error generating PowerPoint presentation: {e}")
        return dumps({"error": "An error occurred while generating the PowerPoint presentation."}, ensure_ascii=False)

@mcp.tool(
    name = "generate_excel",
    title = "Generate Excel",
    description = EXCEL_TEMPLATE
)
async def generate_excel(
    body: GenerateExcelRequest
):
    """Generates an Excel workbook using a provided Python script."""
    logger.info("Received request to generate Excel workbook")
    try:
        # headers
        request = {"headers": get_http_headers()}
        return _generate_excel(body.python_script, body.file_name, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)
    except Exception as e:
        logger.error(f"Error generating Excel workbook: {e}")
        return dumps({"error": "An error occurred while generating the Excel workbook."}, ensure_ascii=False)

@mcp.tool(
    name = "generate_markdown",
    title = "Generate Markdown",
    description = MARKDOWN_TEMPLATE
)
async def generate_markdown(
    body: GenerateMarkdownRequest
):
    """Generates a Markdown document using a provided Python script."""
    logger.info("Received request to generate Markdown document")
    try:
        request = {"headers": get_http_headers()}
        return _generate_markdown(body.python_script, body.file_name, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)
    except Exception as e:
        logger.error(f"Error generating Markdown document: {e}")
        return dumps({"error": "An error occurred while generating the Markdown document."}, ensure_ascii=False)

@mcp.tool(
    name = "generate_word",
    title = "Generate Word",
    description = WORD_TEMPLATE
)
async def generate_word(
    body: DocxBodyElements
):
    """Generates a Word document using provided metadata and body elements."""
    logger.info("Received request to generate Word document")
    try:
        # Collect all elements (flatten nested dicts)
        all_elements = []
        raw_elements = []
        raw_elements.extend(body.document_elements)
        for e in raw_elements:

            aux_dict = {}

            if e.paragraph is not None:
                aux_dict['text'] = e.paragraph.text
                aux_dict['type'] = "ParagraphBody"
            if e.header is not None:
                aux_dict['text'] = e.header.text
                aux_dict['level'] = e.header.level
                aux_dict['type'] = "ParagraphHeader"
            if e.list_item is not None:
                aux_dict['list_style'] = e.list_item.list_style
                aux_dict['items'] = e.list_item.items
                aux_dict['type'] = "ParagraphListItem"
            if e.table is not None:
                aux_dict['table_headers'] = e.table.table_headers
                aux_dict['table_rows'] = e.table.table_rows
                aux_dict['caption'] = e.table.caption
                aux_dict['type'] = "Table"
            if e.image is not None:
                aux_dict['id'] = e.image.id
                aux_dict['caption'] = e.image.caption
                aux_dict['type'] = "Image"
            if e.equation is not None:
                aux_dict['latex'] = e.equation.latex
                aux_dict['caption'] = e.equation.caption
                aux_dict['type'] = "Equation"
            all_elements.append(aux_dict)

        # headers
        request = {"headers": get_http_headers()}
        return _generate_word_from_template(body.document_cover, body.columns_body, all_elements, body.file_name, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)
    except Exception as e:
        logger.error(f"Error generating Word document: {e}")
        return dumps({"error": "An error occurred while generating the Word document."}, ensure_ascii=False)

@mcp.tool(
    name = "list_docx_elements",
    title = "List DOCX Elements",
    description = "Return the DOCX structure with each element's index, style, and text to help identify target sections before adding comments with the review_docx tool."
)
async def full_context_docx(
    body: FullContextDocxRequest
):
    """Returns the structure of a DOCX document, including index, style, and text of each element."""
    logger.info("Received request to list DOCX document elements")
    try:
        # headers
        request = {"headers": get_http_headers()}
        return _full_context_docx(body.file_id, body.file_name, request, OWUI_URL)
    except Exception as e:
        logger.error(f"Error listing DOCX document elements: {e}")
        return dumps({"error": "An error occurred while listing the DOCX document elements."}, ensure_ascii=False)

@mcp.tool(
    name = "review_docx",
    title = "Review DOCX Document",
    description = "Review an existing DOCX document and add targeted comments on selected sections to improve spelling, grammar, style, and clarity."
)
async def review_docx(
    body: ReviewDocxRequest
):
    """Reviews an existing DOCX document and adds comments to specific elements."""
    logger.info("Received request to review DOCX document")
    try:
        # headers
        request = {"headers": get_http_headers()}
        return _review_docx(body.file_id, body.file_name, body.review_comments, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE, REVIEWER_AI_ASSISTANT_NAME)
    except Exception as e:
        logger.error(f"Error reviewing DOCX document: {e}")
        return dumps({"error": "An error occurred while reviewing the DOCX document."}, ensure_ascii=False)

# --- Main ---
if __name__ == "__main__":
    logger.info(SERVER_BANNER)
    mcp.run(transport="streamable-http", host='0.0.0.0', port=PORT, show_banner=False)

    