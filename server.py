# Native libraries
from json import dumps
from os import getenv
from typing import Annotated, Literal, List, Tuple, Union, Any, Optional
from pydantic import Field

# Third-party libraries
from fastmcp import FastMCP,  Context
from fastmcp.server.dependencies import get_http_headers
import uvicorn

# Utilities
from utils.logger import configure_logging, get_logger
configure_logging()
from utils.load_md_templates import load_md_templates
from utils.register_tools import register_word_tool
from utils.argument_descriptions import SERVER_BANNER, MCP_SERVER_NAME, SERVER_VERSION, ARGUMENT_DESCRIPTIONS
from utils.generate_word_template_body_check import generate_word_template_body_check
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
from tools.docx_tool import generate_word as _generate_word
# Parameters
ENABLE_WORD_ELEMENT_FILLING = getenv('ENABLE_WORD_ELEMENT_FILLING', 'false').lower() == 'true' 
OWUI_URL = getenv('OWUI_URL', 'http://localhost:8080')
PORT = int(getenv('PORT', '8000'))
MCP_TRANSPORT = getenv('MCP_TRANSPORT', 'streamable-http').strip().lower()
OWUI_API_KEY = (getenv('OWUI_API_KEY') or '').strip() or None
REVIEWER_AI_ASSISTANT_NAME = getenv('REVIEWER_AI_ASSISTANT_NAME', 'GenFilesMCP')
POWERPOINT_TEMPLATE, EXCEL_TEMPLATE, WORD_TEMPLATE, MARKDOWN_TEMPLATE, MCP_INSTRUCTIONS = load_md_templates(ENABLE_WORD_ELEMENT_FILLING)
ENABLE_CREATE_KNOWLEDGE = getenv('ENABLE_CREATE_KNOWLEDGE', 'true').lower() == 'true'


# Initialize FastMCP server
mcp = FastMCP(
    name = MCP_SERVER_NAME,
    instructions = MCP_INSTRUCTIONS,   
)

# Configure Logging
logger = get_logger(MCP_SERVER_NAME)


def build_request_context() -> dict[str, dict[str, str] | str]:
    if OWUI_API_KEY:
        return {"headers": f"Bearer {OWUI_API_KEY}"}

    return {"headers": get_http_headers()}

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
        request = build_request_context()
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
        request = build_request_context()
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
        request = build_request_context()
        return _generate_markdown(body.python_script, body.file_name, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)
    except Exception as e:
        logger.error(f"Error generating Markdown document: {e}")
        return dumps({"error": "An error occurred while generating the Markdown document."}, ensure_ascii=False)

async def generate_word_structured(
    body: DocxBodyElements
):
    """Generates a Word document using provided metadata and body elements."""
    logger.info("Received request to generate Word document")
    try:
        # Check the structure of the document body elements
        all_elements = generate_word_template_body_check(body)
        if isinstance(all_elements, dict) and "error" in all_elements:
            return dumps(all_elements, ensure_ascii=False)
       
        # headers
        request = build_request_context()
        return _generate_word_from_template(body.document_cover, body.columns_body, all_elements, body.file_name, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)
    except Exception as e:
        logger.error(f"Error generating Word document: {e}")
        return dumps({"error": "An error occurred while generating the Word document."}, ensure_ascii=False)

async def generate_word(
    python_script: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["python_script"])],
    file_name: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])],
    images_list: Annotated[List[str], Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["images_list"])] = []):
    """
    Generate a Word document using the provided AI-generated Python script. The images_list argument provides a list of 
    image file IDs to be included in the document.
    """
    # headers
    request = build_request_context()
    return _generate_word(python_script, file_name, images_list, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE)


register_word_tool(
    mcp=mcp,
    logger=logger,
    word_template=WORD_TEMPLATE,
    enable_word_element_filling=ENABLE_WORD_ELEMENT_FILLING,
    generate_word_structured=generate_word_structured,
    generate_word=generate_word,
)


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
        request = build_request_context()
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
        request = build_request_context()
        return _review_docx(body.file_id, body.file_name, body.review_comments, request, OWUI_URL, ENABLE_CREATE_KNOWLEDGE, REVIEWER_AI_ASSISTANT_NAME)
    except Exception as e:
        logger.error(f"Error reviewing DOCX document: {e}")
        return dumps({"error": "An error occurred while reviewing the DOCX document."}, ensure_ascii=False)


def main() -> None:
    logger.info(SERVER_BANNER)

    if MCP_TRANSPORT == "stdio":
        logger.info("Starting MCP server with stdio transport")
        mcp.run(transport="stdio", show_banner=False)
        return

    if MCP_TRANSPORT == "streamable-http":
        logger.info(f"Starting MCP server with streamable-http transport on 0.0.0.0:{PORT}")
        mcp.run(transport="streamable-http", host='0.0.0.0', port=PORT, show_banner=False)
        return

    raise ValueError(
        "Unsupported MCP_TRANSPORT value "
        f"'{MCP_TRANSPORT}'. Supported values: 'streamable-http', 'stdio'."
    )

# --- Main ---
if __name__ == "__main__":
    main()

    