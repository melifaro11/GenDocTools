"""
Utility functions for loading Markdown templates from files.
"""

from pathlib import Path

def load_md_templates() -> tuple[str, str, str, str, str]:
    """
    Load Markdown templates for PowerPoint, Excel, Word, Markdown and MCP instructions.

    Returns:
        tuple[str, str, str, str, str]: A tuple containing the Markdown templates for
                                        PowerPoint, Excel, Word, Markdown and the MCP instructions.
    """

    try:
        # Load Markdown template files
        with open(Path("src","powerpoint.md"), "r", encoding="utf-8") as f:
            POWERPOINT_TEMPLATE = f.read()

        with open(Path("src","excel.md"), "r", encoding="utf-8") as f:
            EXCEL_TEMPLATE = f.read()

        with open(Path("src","word.md"), "r", encoding="utf-8") as f:
            WORD_TEMPLATE = f.read()

        with open(Path("src","markdown.md"), "r", encoding="utf-8") as f:
            MARKDOWN_TEMPLATE = f.read()

        with open(Path("src","mcp_instructions.md"), "r", encoding="utf-8") as f:
            MCP_INSTRUCTIONS = f.read()

        return (
            POWERPOINT_TEMPLATE,
            EXCEL_TEMPLATE,
            WORD_TEMPLATE,
            MARKDOWN_TEMPLATE,
            MCP_INSTRUCTIONS
        )
    
    except Exception as e:

        raise RuntimeError(f"Error loading Markdown templates: {e}")