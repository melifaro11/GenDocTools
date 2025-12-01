# Native libraries
from json import dumps
from os import getenv
from typing import Annotated, Literal, List, Tuple
from enum import Enum
from pathlib import Path
from io import BytesIO
import logging
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger("GenFilesMCP")

# Third-party libraries
from pydantic import Field, BaseModel
from requests import post, get
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
from docx import Document

# Utilities
from utils.load_md_templates import load_md_templates
from utils.upload_file import upload_file
from utils.download_file import download_file
from utils.knowledge import create_knowledge

# Parameters
URL = getenv('OWUI_URL',)
PORT = int(getenv('PORT'))
POWERPOINT_TEMPLATE, EXCEL_TEMPLATE, WORD_TEMPLATE,MARKDOWN_TEMPLATE, MCP_INSTRUCTIONS = load_md_templates()
# Enable or disable automatic creation of knowledge collections after upload
# Defaults to true to preserve existing behavior. Set to 'false' to disable.
ENABLE_CREATE_KNOWLEDGE = getenv('ENABLE_CREATE_KNOWLEDGE', 'true').lower() == 'true'

# Pydantic model for review comments
class ReviewComment(BaseModel):
    index: int
    comment: str

# Initialize FastMCP server
mcp = FastMCP(
    name = "GenFilesMCP",
    instructions = MCP_INSTRUCTIONS,   
    port = PORT,
    host = "0.0.0.0"
)

@mcp.tool(
    name = "generate_powerpoint",
    title = "Generate PowerPoint presentation",
    description = POWERPOINT_TEMPLATE
)
async def generate_powerpoint(
    python_script: Annotated[
        str, 
        Field(description="Complete Python script that generates the PowerPoint presentation using the provided template.")
    ],
    file_name: Annotated[
        str, 
        Field(description="Desired name for the generated PowerPoint file without the extension.")
    ],
    user_id: Annotated[
        str,
        Field(description="User ID to associate the knowledge base with the correct user.")
    ],
    ctx: Context[ServerSession, None]
) -> dict:
    """
    Generate a PowerPoint file using a Python script.

    Returns:
        dict: Contains 'file_path_download' with a markdown hyperlink for downloading the generated PowerPoint file.
              Format: "[Download {filename}.pptx](/api/v1/files/{id}/content)"
    """
    try:
        # Create a buffer for the PowerPoint file
        buffer = BytesIO()
        buffer.name = f'{file_name}.pptx'
        context = {"pptx_buffer": buffer}
        exec(python_script, context)

        # Reset buffer position to start
        buffer.seek(0)

        # Retrieve authorization header from the request context
        try:
            bearer_token = ctx.request_context.request.headers.get("authorization")
            logger.info(f"Received authorization header!")
        except:
            logger.error(f"Error retrieving authorization header")

        # Upload the generated PowerPoint file
        response, request_data = upload_file(
            url=URL, 
            token=bearer_token, 
            file_data=buffer,
            filename=file_name,
            file_type="pptx"
        )

        # If upload is successful, add to knowledge base
        if "file_path_download" in response and ENABLE_CREATE_KNOWLEDGE:
            # create knowledge base if not exists
            create_knowledge_status = create_knowledge(
                url=URL, 
                token=bearer_token,
                file_id=request_data['id'],
                user_id=user_id
            )
            if create_knowledge_status:
                logger.info("Knowledge base updated successfully.")
            else:
                logger.error(f"Error creating or updating knowledge base")
        elif "error" in response:
            logger.error(f"Error uploading the file.")
        else:
            logger.info("Skipping knowledge creation because ENABLE_CREATE_KNOWLEDGE is false")

        return response 
    
    except Exception as e:
        return dumps(
            {
                "error": {
                    "message": str(e)
                }
            }, 
            indent=4, 
            ensure_ascii=False
        )

@mcp.tool(
    name = "generate_excel",
    title = "Generate Excel workbook",
    description = EXCEL_TEMPLATE
)
async def generate_excel(
    python_script: Annotated[
        str, 
        Field(description="Complete Python script that generates the Excel workbook using the provided template.")
    ],
    file_name: Annotated[
        str, 
        Field(description="Desired name for the generated Excel file without the extension.")
    ],
    user_id: Annotated[
        str,
        Field(description="User ID to associate the knowledge base with the correct user.")
    ],
    ctx: Context[ServerSession, None]
) -> dict:
    """
    Generate an Excel file using a Python script.

    Returns:
        dict: Contains 'file_path_download' with a markdown hyperlink for downloading the generated Excel file.
              Format: "[Download {filename}.xlsx](/api/v1/files/{id}/content)"
    """
    try:
        # Create a buffer for the Excel file
        buffer = BytesIO()
        buffer.name = f'{file_name}.xlsx'
        context = {"xlsx_buffer": buffer}
        exec(python_script, context)

        # Reset buffer position to start
        buffer.seek(0)

        # Retrieve authorization header from the request context
        try:
            bearer_token = ctx.request_context.request.headers.get("authorization")
            logger.info(f"Received authorization header!")
        except:
            logger.error(f"Error retrieving authorization header")

        # Upload the generated Excel file
        response, request_data = upload_file(
            url=URL, 
            token=bearer_token, 
            file_data=buffer,
            filename=file_name,
            file_type="xlsx"
        )

        # If upload is successful, add to knowledge base
        if "file_path_download" in response and ENABLE_CREATE_KNOWLEDGE:
            # create knowledge base if not exists
            create_knowledge_status = create_knowledge(
                url=URL, 
                token=bearer_token,
                file_id=request_data['id'],
                user_id=user_id
            )
            if create_knowledge_status:
                logger.info("Knowledge base updated successfully.")
            else:
                logger.error(f"Error creating or updating knowledge base")
        elif "error" in response:
            logger.error(f"Error uploading the file.")
        else:
            logger.info("Skipping knowledge creation because ENABLE_CREATE_KNOWLEDGE is false")

        return response 
    
    except Exception as e:
        return dumps(
            {
                "error": {
                    "message": str(e)
                }
            }, 
            indent=4, 
            ensure_ascii=False
        )

@mcp.tool(
    name = "generate_word",
    title = "Generate Word document",
    description = WORD_TEMPLATE
)
async def generate_word(
    python_script: Annotated[
        str, 
        Field(description="Complete Python script that generates the Word document using the provided template.")
    ],
    file_name: Annotated[
        str, 
        Field(description="Desired name for the generated Word file without the extension.")
    ],
    user_id: Annotated[
        str,
        Field(description="User ID to associate the knowledge base with the correct user.")
    ],
    ctx: Context[ServerSession, None]
) -> dict:
    """
    Generate a Word file using a Python script.

    Returns:
        dict: Contains 'file_path_download' with a markdown hyperlink for downloading the generated Word file.
              Format: "[Download {filename}.docx](/api/v1/files/{id}/content)"
    """
    try:
        # Create a buffer for the Word file
        buffer = BytesIO()
        buffer.name = f'{file_name}.docx'
        context = {"docx_buffer": buffer}
        exec(python_script, context)

        # Reset buffer position to start
        buffer.seek(0)

        # Retrieve authorization header from the request context
        try:
            bearer_token = ctx.request_context.request.headers.get("authorization")
            logger.info(f"Received authorization header!")
        except:
            logger.error(f"Error retrieving authorization header")

        # Upload the generated Word file
        response, request_data = upload_file(
            url=URL, 
            token=bearer_token, 
            file_data=buffer,
            filename=file_name,
            file_type="docx"
        )

        # If upload is successful, add to knowledge base
        if "file_path_download" in response and ENABLE_CREATE_KNOWLEDGE:
            # create knowledge base if not exists
            create_knowledge_status = create_knowledge(
                url=URL, 
                token=bearer_token,
                file_id=request_data['id'],
                user_id=user_id
            )
            if create_knowledge_status:
                logger.info("Knowledge base updated successfully.")
            else:
                logger.error(f"Error creating or updating knowledge base")
        elif "error" in response:
            logger.error(f"Error uploading the file.")
        else:
            logger.info("Skipping knowledge creation because ENABLE_CREATE_KNOWLEDGE is false")

        return response 
    
    except Exception as e:
        return dumps(
            {
                "error": {
                    "message": str(e)
                }
            }, 
            indent=4, 
            ensure_ascii=False
        )

@mcp.tool(
    name = "generate_markdown",
    title = "Generate Markdown document",
    description = MARKDOWN_TEMPLATE
) 
async def generate_markdown(
    python_script: Annotated[
        str, 
        Field(description="Complete Python script that generates the Markdown document using the provided template.")
    ],
    file_name: Annotated[
        str, 
        Field(description="Desired name for the generated Markdown file without the extension.")
    ],
    user_id: Annotated[
        str,
        Field(description="User ID to associate the knowledge base with the correct user.")
    ],
    ctx: Context[ServerSession, None]
) -> dict:
    """
    Generate a Markdown file using a Python script.

    Returns:
        dict: Contains 'file_path_download' with a markdown hyperlink for downloading the generated Markdown file.
              Format: "[Download {filename}.md](/api/v1/files/{id}/content)"
    """
    try:
        # Create a buffer for the Markdown file
        buffer = BytesIO()
        buffer.name = f'{file_name}.md'
        context = {"md_buffer": buffer}
        exec(python_script, context)

        # Reset buffer position to start
        buffer.seek(0)

        # Retrieve authorization header from the request context
        try:
            bearer_token = ctx.request_context.request.headers.get("authorization")
            logger.info(f"Received authorization header!")
        except:
            logger.error(f"Error retrieving authorization header")

        # Upload the generated Markdown file
        response, request_data = upload_file(
            url=URL, 
            token=bearer_token, 
            file_data=buffer,
            filename=file_name,
            file_type="md"
        )

        # If upload is successful, add to knowledge base
        if "file_path_download" in response and ENABLE_CREATE_KNOWLEDGE:
            # create knowledge base if not exists
            create_knowledge_status = create_knowledge(
                url=URL, 
                token=bearer_token,
                file_id=request_data['id'],
                user_id=user_id
            )
            if create_knowledge_status:
                logger.info("Knowledge base updated successfully.")
            else:
                logger.error(f"Error creating or updating knowledge base")
        elif "error" in response:
            logger.error(f"Error uploading the file.")
        else:
            logger.info("Skipping knowledge creation because ENABLE_CREATE_KNOWLEDGE is false")

        return response 
    
    except Exception as e:
        return dumps(
            {
                "error": {
                    "message": str(e)
                }
            }, 
            indent=4, 
            ensure_ascii=False
        )
    
@mcp.tool(
    name="full_context_docx",
    title="Return the structure of a docx document",
    description="""Return the index, style and text of each element in a docx document. This includes paragraphs, headings, tables, images, and other components. The output is a JSON object that provides a detailed representation of the document's structure and content.
    The Agent will use this tool to understand the content and structure of the document before perform corrections (spelling, grammar, style suggestions, idea enhancements). Agent have to identify the index of each element to be able to add comments in the review_docx tool."""
)
async def full_context_docx(
    file_id: Annotated[
        str, 
        Field(description="ID of the existing docx file to analyze (from a previous chat upload).")
    ],
    file_name: Annotated[
        str, 
        Field(description="The name of the original docx file")
    ],
    ctx: Context[ServerSession, None]
) -> dict:
    """
    Return the structure of a docx document including index, style, and text of each element.
    Returns:
        dict: A JSON object with the structure of the document.
    """
    # Retrieve authorization header from the request context
    try:
        bearer_token = ctx.request_context.request.headers.get("authorization")
        logger.info(f"Received authorization header!")
    except:
        logger.error(f"Error retrieving authorization header")

    try:
        # Download in memory the docx file using the download_file helper
        docx_file = download_file(
            url=URL, 
            token=bearer_token, 
            file_id=file_id
        )

        if isinstance(docx_file, dict) and "error" in docx_file:
            return dumps(
                docx_file,
                indent=4,
                ensure_ascii=False
            )
        else:
            # Instantiate a Document object from the in-memory file
            doc = Document(docx_file)
            
            # Structure to return
            text_body = {
                "file_name": file_name,
                "file_id": file_id,
                "body": []
            }

            # list to store different parts of the document
            parts = []

            for idx, parts in enumerate(doc.paragraphs):
                # text of the paragraph
                text = parts.text.strip()

                if not text:
                    # skip empty paragraphs
                    continue  

                # style of the paragraph
                style = parts.style.name  
                text_body["body"].append({
                    "index": idx,
                    "style": style ,  # style.name
                    "text": text  # text
                })

            return dumps(
                text_body,
                indent=4,
                ensure_ascii=False
            )
    except Exception as e:
        return dumps(
            {
                "error": {
                    "message": str(e)
                }
            }, 
            indent=4, 
            ensure_ascii=False
        )

@mcp.tool(
    name="review_docx",
    title="Review and comment on docx document",
    description="""Review an existing docx document, perform corrections (spelling, grammar, style suggestions, idea enhancements), and add comments to cells. Returns a markdown hyperlink for downloading the reviewed file."""
)
async def review_docx(
    file_id: Annotated[
        str, 
        Field(description="ID of the existing docx file to review (from a previous chat upload).")
    ],
    file_name: Annotated[
        str, 
        Field(description="The name of the original docx file")
    ],
    review_comments: Annotated[
        List[ReviewComment], 
        Field(description="List of objects where each object has keys: 'index' (int) and 'comment' (str). Example: [{'index': 0, 'comment': 'Fix typo'}].")
    ],
    user_id: Annotated[
        str,
        Field(description="User ID to associate the knowledge base with the correct user.")
    ],
    ctx: Context[ServerSession, None]
) -> dict:
    """
    Review an existing docx document and add comments to specified elements.
    Returns:
        dict: Contains 'file_path_download' with a markdown hyperlink for downloading the reviewed docx file.
              Format: "[Download {filename}.docx](/api/v1/files/{id}/content)"
    """
    # Retrieve authorization header from the request context
    try:
        bearer_token = ctx.request_context.request.headers.get("authorization")
        logger.info(f"Received authorization header!")
    except:
        logger.error(f"Error retrieving authorization header")

    try:
        
        # Download the existing docx file
        docx_file = download_file(URL, bearer_token, file_id)
        if isinstance(docx_file, dict) and "error" in docx_file:
            return dumps(docx_file, indent=4, ensure_ascii=False)

        # Load the document
        doc = Document(docx_file)

        # Add comments to specified paragraphs
        paragraphs = list(doc.paragraphs)  # Get list of paragraphs
        for item in review_comments:
            try:
                index = item.index
                comment_text = item.comment
            except (AttributeError, TypeError):
                # malformed item; skip
                continue

            if index is None or comment_text is None:
                continue

            if 0 <= index < len(paragraphs):
                para = paragraphs[index]
                if para.runs:  # Ensure there are runs to comment on
                    # Add comment to the first run of the paragraph
                    doc.add_comment(
                        runs=[para.runs[0]],
                        text=comment_text,
                        author="AI Reviewer",
                        initials="AI"
                    )

        # Create a buffer for the reviewed file
        buffer = BytesIO()
        buffer.name = f'{Path(file_name).stem}_reviewed.docx'
        doc.save(buffer)
        buffer.seek(0)

        # Upload the reviewed docx file
        response, request_data = upload_file(
            url=URL, 
            token=bearer_token, 
            file_data=buffer,
            filename=f"{Path(file_name).stem}_reviewed",
            file_type="docx"
        )

        # If upload is successful, add to knowledge base
        if "file_path_download" in response and ENABLE_CREATE_KNOWLEDGE:
            # create knowledge base if not exists
            create_knowledge_status = create_knowledge(
                url=URL, 
                token=bearer_token,
                file_id=request_data['id'],
                user_id=user_id,
                knowledge_name="Documents Reviewed by AI"
            )
            if create_knowledge_status:
                logger.info("Knowledge base updated successfully.")
            else:
                logger.error(f"Error creating or updating knowledge base")
        elif "error" in response:
            logger.error(f"Error uploading the file.")
        else:
            logger.info("Skipping knowledge creation because ENABLE_CREATE_KNOWLEDGE is false")

        return response
    
    except Exception as e:
        return dumps(
            {
                "error": {
                    "message": str(e)
                }
            }, 
            indent=4, 
            ensure_ascii=False
        )
    
# Initialize and run the server
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http"
    )

