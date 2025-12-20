"""
Combined DOCX utilities:
- full_context_docx(file_id, file_name, ctx, URL)
- review_docx(file_id, file_name, review_comments, ctx, URL, ENABLE_CREATE_KNOWLEDGE)

This module merges `full_context_docx.py` and `review_docx.py` and centralizes common logic.
"""

from io import BytesIO
from json import dumps
from pathlib import Path
import logging

from docx import Document

from utils.download_file import download_file
from utils.upload_file import upload_file
from utils.knowledge import create_knowledge
from utils.get_user_id import get_user_id
from utils.authorization import _get_bearer_token

logger = logging.getLogger("GenFilesMCP")

def full_context_docx(file_id, file_name, ctx, URL):
    """
    Return the structure of a DOCX document including index, style, and text of each element.

    Returns:
        str: JSON-formatted string with the document structure or an error object.
    """
    bearer_token = _get_bearer_token(ctx)

    try:
        docx_file = download_file(
            url=URL,
            token=bearer_token,
            file_id=file_id
        )

        if isinstance(docx_file, dict) and "error" in docx_file:
            return dumps(docx_file, indent=4, ensure_ascii=False)

        doc = Document(docx_file)
        text_body = {
            "file_name": file_name,
            "file_id": file_id,
            "body": []
        }

        for idx, part in enumerate(doc.paragraphs):
            text = part.text.strip()
            if not text:
                continue  # Skip empty paragraphs

            style = part.style.name
            text_body["body"].append({
                "index": idx,
                "style": style,
                "text": text
            })

        return dumps(text_body, indent=4, ensure_ascii=False)

    except Exception as e:
        return dumps({"error": {"message": str(e)}}, indent=4, ensure_ascii=False)


def generate_word(python_script, file_name, ctx, URL, ENABLE_CREATE_KNOWLEDGE):
    """
    Generate a Word document using an AI-generated Python script.

    Returns:
        dict: Contains 'file_path_download' with a markdown hyperlink for downloading the generated Word file.
    """
    try:
        buffer = BytesIO()
        buffer.name = f'{file_name}.docx'
        context = {"docx_buffer": buffer}
        try:
            exec(python_script, context)
        except Exception as exec_e:
            return {"error": {"message": f"Error executing script: {str(exec_e)}"}}

        buffer.seek(0)

        bearer_token = _get_bearer_token(ctx)
        if bearer_token:
            logger.info("Received authorization header")
        else:
            logger.debug("Authorization header not present")

        user_id = get_user_id(URL, bearer_token)
        if not user_id:
            return dumps({"error": {"message": "Error obtaining user id from token"}}, indent=4, ensure_ascii=False)

        response, request_data = upload_file(
            url=URL, 
            token=bearer_token, 
            file_data=buffer,
            filename=file_name,
            file_type="docx"
        )

        if "file_path_download" in response and ENABLE_CREATE_KNOWLEDGE:
            create_knowledge_status = create_knowledge(
                url=URL,
                token=bearer_token,
                file_id=request_data['id'],
                user_id=user_id
            )
            if create_knowledge_status:
                logger.info("Knowledge base updated successfully.")
            else:
                logger.error("Error creating or updating knowledge base")
        elif "error" in response:
            logger.error("Error uploading the file.")
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


def review_docx(file_id, file_name, review_comments, ctx, URL, ENABLE_CREATE_KNOWLEDGE):
    """
    Review an existing DOCX document and add comments to specified elements.

    Returns:
        dict or str: Upload response dict (with 'file_path_download') or JSON-formatted error string.
    """
    bearer_token = _get_bearer_token(ctx)

    user_id = get_user_id(URL, bearer_token)
    if not user_id:
        return dumps({"error": {"message": "Error obtaining user id from token"}}, indent=4, ensure_ascii=False)

    try:
        docx_file = download_file(URL, bearer_token, file_id)
        if isinstance(docx_file, dict) and "error" in docx_file:
            return dumps(docx_file, indent=4, ensure_ascii=False)

        doc = Document(docx_file)
        paragraphs = list(doc.paragraphs)
        for item in review_comments:
            try:
                index = item.index
                comment_text = item.comment
            except (AttributeError, TypeError):
                continue

            if index is None or comment_text is None:
                continue

            if 0 <= index < len(paragraphs):
                para = paragraphs[index]
                if para.runs:
                    doc.add_comment(
                        runs=[para.runs[0]],
                        text=comment_text,
                        author="AI Reviewer",
                        initials="AI"
                    )

        buffer = BytesIO()
        buffer.name = f'{Path(file_name).stem}_reviewed.docx'
        doc.save(buffer)
        buffer.seek(0)

        response, request_data = upload_file(
            url=URL,
            token=bearer_token,
            file_data=buffer,
            filename=f"{Path(file_name).stem}_reviewed",
            file_type="docx"
        )

        if "file_path_download" in response and ENABLE_CREATE_KNOWLEDGE:
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
                logger.error("Error creating or updating knowledge base")
        elif "error" in response:
            logger.error("Error uploading the file.")
        else:
            logger.info("Skipping knowledge creation because ENABLE_CREATE_KNOWLEDGE is false")

        return response

    except Exception as e:
        return dumps({"error": {"message": str(e)}}, indent=4, ensure_ascii=False)
