"""
Main module for the GenFilesMCP server.

This module initializes the FastMCP server and defines tools for generating
Excel, Word, PowerPoint, and Markdown files using AI-generated Python scripts.
It also includes tools for analyzing and reviewing existing documents.
"""

# Native libraries
from json import dumps
from os import getenv
from datetime import datetime
from typing import Annotated, Literal, List, Tuple, Optional, Union, Any
from enum import Enum
from pathlib import Path
from io import BytesIO
import logging
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger("GenDocsServer")

# Third-party libraries
from pydantic import Field, BaseModel, field_validator, model_validator
from requests import post, get
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
from mcp.types import ToolAnnotations
from docx import Document

# Utilities
from utils.load_md_templates import load_md_templates
from utils.upload_file import upload_file
from utils.download_file import download_file
from utils.knowledge import create_knowledge
from utils.argument_descriptions import ARGUMENT_DESCRIPTIONS

# Import tools from the tools directory
from tools.powerpoint_tool import generate_powerpoint as _generate_powerpoint
from tools.excel_tool import generate_excel as _generate_excel
from tools.docx_tool import generate_word as _generate_word
from tools.markdown_tool import generate_markdown as _generate_markdown
from tools.docx_tool import full_context_docx as _full_context_docx, review_docx as _review_docx, generate_word_from_template as _generate_word_from_template

# Parameters
URL = getenv('OWUI_URL', '')
PORT = int(getenv('PORT', '8000'))
# Control transport: if HTTP_TRANSPORT is 'true' (default) use 'streamable-http', else use 'stdio'
HTTP_TRANSPORT = getenv('HTTP_TRANSPORT', 'true').lower() == 'true'
POWERPOINT_TEMPLATE, EXCEL_TEMPLATE, WORD_TEMPLATE, MARKDOWN_TEMPLATE, MCP_INSTRUCTIONS = load_md_templates()
# Enable or disable automatic creation of knowledge collections after upload
# Defaults to true to preserve existing behavior. Set to 'false' to disable.
ENABLE_CREATE_KNOWLEDGE = getenv('ENABLE_CREATE_KNOWLEDGE', 'true').lower() == 'true' 

# Pydantic model for review comments
class ReviewComment(BaseModel):
    index: int
    comment: str

class ImagesList(BaseModel):
    images: str

# General Cover 
class Cover(BaseModel):
    title: str
    subtitle: str
    description: str
    author: str
    month: str
    year: str
    page_break: bool = False

# class Paragraph(BaseModel):
#     text: str = ""
#     bold: bool = False
#     italic: bool = False
#     alignment: str = "justify"

class ListItem(BaseModel):
    style: Literal['List Number', 'List Bullet'] = "List Bullet"  # e.g., "bullet" or "number"
    items: List[str] = ["Item 1", "Item 2", "Item 3"]
    # alignment: Optional[str] = None

class Table(BaseModel):
    headers: List[str] = ["Header 1", "Header 2", "Header 3"]
    rows: List[List[str]] = [["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"]]
    caption: Optional[str] = "Table 1 Caption"

class Image(BaseModel):
    id: str = None
    # width: float = 4.0
    # height: float = 3.0
    # alignment: Optional[str] = None
    caption: Optional[str] = "Fig. 1. Caption"

    # @model_validator(mode='before')
    # @classmethod
    # def check_file_id(cls, data: Any) -> Any:
    #     if isinstance(data, dict):
    #         if 'file_id' in data and 'id' not in data:
    #             data['id'] = data['file_id']
    #     return data

class Equation(BaseModel):
    latex: str
    caption: Optional[str] = "Equation 1 Caption"

# class Section(BaseModel):
#     title: str = ""
#     level: Literal[1,2,3,4,5,6] = 2
#     alignment: str = "center"
#     columns: int = None
#     paragraph: Paragraph
#     list: ListItem = None
#     table: Table = None
#     image: Image = None
#     equation: Equation = None

class ParagraphHeader(BaseModel):
    title: str = "Example Header"
    level: Literal[1,2,3,4,5,6] = 2
    alignment: str = "center"

class ParagraphBody(BaseModel):
    text: str = ""
    # bold: bool = False
    # italic: bool = False
    alignment: str = "justify"

class WordsWithBoldOrItalic(BaseModel):
    text: str = ""
    bold: bool = False
    italic: bool = False
    alignment: str = "justify"


# class DocumentDict(BaseModel):
#     font: str = "Times New Roman"
#     section: Section

# Initialize FastMCP server
mcp = FastMCP(
    name = "GenDocsServer",
    instructions = MCP_INSTRUCTIONS,
    port = PORT,
    host = "0.0.0.0"
)

# Mcp tool definitions
@mcp.tool(
    name="generate_powerpoint",
    title="Generate PowerPoint presentation",
    description=POWERPOINT_TEMPLATE,
    annotations=ToolAnnotations(destructiveHint=False)
)
async def generate_powerpoint(
    ctx: Context[ServerSession, None],
    python_script: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["python_script"])],
    file_name: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])]):
    """
    Generate a PowerPoint presentation using the provided AI-generated Python script.
    """
    return _generate_powerpoint(python_script, file_name, ctx, URL, ENABLE_CREATE_KNOWLEDGE)

# Mcp tool definitions
@mcp.tool(
    name="generate_excel",
    title="Generate Excel workbook",
    description=EXCEL_TEMPLATE,
    annotations=ToolAnnotations(destructiveHint=False)
)
async def generate_excel(
    ctx: Context[ServerSession, None],
    python_script: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["python_script"])],
    file_name: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])]):
    """
    Generate an Excel workbook using the provided AI-generated Python script.
    """
    return _generate_excel(python_script, file_name, ctx, URL, ENABLE_CREATE_KNOWLEDGE)

# Mcp tool definitions
# @mcp.tool(
#     name="generate_word",
#     title="Generate Word document",
#     description=WORD_TEMPLATE,
#     annotations=ToolAnnotations(destructiveHint=False)
# )
# async def generate_word(
#     ctx: Context[ServerSession, None],
#     python_script: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["python_script"])],
#     file_name: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])],
#     images_list: Annotated[List[str], Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["images_list"])] = []):
#     """
#     Generate a Word document using the provided AI-generated Python script. The images_list argument provides a list of image file IDs to be included in the document.
#     """
#     return _generate_word(python_script, file_name, images_list, ctx, URL, ENABLE_CREATE_KNOWLEDGE)

# Mcp tool definitions
@mcp.tool(
    name="generate_word",
    title="Generate Word document",
    description="Generate a Word document from metadata and a list of document elements including headings, paragraphs, lists, tables, images, and equations.",
    annotations=ToolAnnotations(destructiveHint=False)
)
async def generate_word_from_dict(
    ctx: Context[ServerSession, None],
    doc_metadata: Annotated[Cover, Field(description="Document title, subtitle, description, author, and date.")],
    columns_body: Annotated[int, Field(description="Number of columns for the body sections (1 or 2).")],
    doc_dict: Annotated[List[Union[ParagraphHeader, ParagraphBody, WordsWithBoldOrItalic, ListItem, Table, Image, Equation]], Field(description="List of document elements for the body: headings (section titles), paragraphs (plain text; use '\\n\\n' for paragraph breaks), words (with bold/italic), lists (numbered or bulleted), tables (with headers and rows), images (with captions), equations (in LaTeX).")],
    file_name: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])]):
    """
    Generate a Word document from metadata and a list of document elements.
    """
    return _generate_word_from_template(doc_metadata, columns_body, doc_dict, file_name, ctx, URL, ENABLE_CREATE_KNOWLEDGE)

# Mcp tool definitions
@mcp.tool(
    name="generate_markdown",
    title="Generate Markdown document",
    description=MARKDOWN_TEMPLATE,
    annotations=ToolAnnotations(destructiveHint=False)
)
async def generate_markdown(
    ctx: Context[ServerSession, None],
    python_script: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["python_script"])],
    file_name: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])]) :
    """
    Generate a Markdown document using the provided AI-generated Python script.
    """
    # keep same behaviour: pass ctx (the tool will obtain user_id from token)
    return _generate_markdown(python_script, file_name, ctx, URL, ENABLE_CREATE_KNOWLEDGE)

# Mcp tool definitions
@mcp.tool(
    name="full_context_docx",
    title="Return the structure of a docx document",
    description="""Return the index, style and text of each element in a docx document. This includes paragraphs, headings, tables, images, and other components. The output is a JSON object that provides a detailed representation of the document's structure and content."""
)
async def full_context_docx(
    ctx: Context[ServerSession, None],
    file_id: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["full_context_docx"]["file_id"])],
    file_name: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["full_context_docx"]["file_name"])]):
    """
    Return the full structure and content of a DOCX document as JSON.
    """
    return _full_context_docx(file_id, file_name, ctx, URL)

# Mcp tool definitions
@mcp.tool(
    name="review_docx",
    title="Review and comment on docx document",
    description="""Review an existing docx document, perform corrections (spelling, grammar, style suggestions, idea enhancements), and add comments to cells. Returns a markdown hyperlink for downloading the reviewed file."""
)
async def review_docx(
    ctx: Context[ServerSession, None],
    file_id: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["file_id"])],
    review_comments: Annotated[List[ReviewComment], Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["review_comments"])],
    file_name: Annotated[str, Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["file_name"])]):
    """
    Review a DOCX document and add comments based on the provided review comments.
    """
    return _review_docx(file_id, file_name, review_comments, ctx, URL, ENABLE_CREATE_KNOWLEDGE)

# Initialize and run the server
def main():
    chosen_transport = "streamable-http" if HTTP_TRANSPORT else "stdio"
    logger.info(f"Starting MCP with transport={chosen_transport}")
    mcp.run(
        transport=chosen_transport
    )

# Entry point
if __name__ == "__main__":
    main()