"""
Centralized descriptions for tool arguments.
"""

# Centralized argument descriptions for tools

ARGUMENT_DESCRIPTIONS = {
    "common_args": {
        "file_name": "Desired name for the generated file without the extension.",
        "python_script": "Complete Python script that generates the PowerPoint presentation using the provided template."
    },
    "full_context_docx": {
        "file_id": "ID of the existing docx file to analyze (from a previous chat upload).",
        "file_name": "The name of the original docx file"
    },
    "review_docx": {
        "file_id": "ID of the existing docx file to review (from a previous chat upload).",
        "file_name": "The name of the original docx file",
        "review_comments": "List of objects where each object has keys: 'index' (int) and 'comment' (str). Example: [{'index': 0, 'comment': 'Fix typo'}].",
    }
}