"""
Tool for generating Markdown files using user-provided Python scripts.
"""

from io import BytesIO
from utils.upload_file import upload_file
from utils.knowledge import create_knowledge
from utils.get_user_id import get_user_id
from utils.authorization import _get_bearer_token
from json import dumps
import logging

logger = logging.getLogger("GenFilesMCP")

def generate_markdown(python_script, file_name, ctx, URL, ENABLE_CREATE_KNOWLEDGE):
    """
    Generate a Markdown file using an AI-generated Python script.

    Returns:
        dict: Contains 'file_path_download' with a markdown hyperlink for downloading the generated Markdown file.
    """
    try:
        buffer = BytesIO()
        buffer.name = f'{file_name}.md'
        context = {"md_buffer": buffer}
        try:
            exec(python_script, context)
        except Exception as exec_e:
            return {"error": {"message": f"Error executing script: {str(exec_e)}"}}

        buffer.seek(0)

        try:
            bearer_token = _get_bearer_token(ctx)
            logger.info("Received authorization header!")
        except:
            logger.error("Error retrieving authorization header")

        user_id = get_user_id(URL, bearer_token)
        if not user_id:
            return dumps({"error": {"message": "Error obtaining user id from token"}}, indent=4, ensure_ascii=False)

        response, request_data = upload_file(
            url=URL, 
            token=bearer_token, 
            file_data=buffer,
            filename=file_name,
            file_type="md"
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