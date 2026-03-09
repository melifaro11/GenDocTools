import os
import requests
from datetime import datetime
from pydantic import BaseModel, Field


class Tools:
    def __init__(self):
        pass

    # Add your custom tools using pure Python code here, make sure to add type hints and descriptions

    def chat_context(self, __files__: dict = {}, __metadata__: dict = {}) -> dict:
        """
        Get files metadata and get the user Email and user ID from the user object.
        """
        # id and name of current files
        chat_context = {"files": [], "attached_images": []}

        # files metadata
        if __files__:
            for f in __files__:
                chat_context["files"].append({"id": f["id"], "name": f["name"]})

        # imgs in messages
        parent = __metadata__.get("parent_message", {})
        files = parent.get("files", [])

        for f in files:
            content_type = f.get("content_type", "")
            file_id = f.get("id")
            filename = f.get("name")

            if content_type.startswith("image/"):
                chat_context["attached_images"].append(
                    {"img_id": file_id, "file_name": filename}
                )

        return chat_context
