import logging
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger("Gen Files OpenAPI Tool Server")

from importlib import resources

def load_md_templates() -> tuple[str, str, str, str, str]:
    """
    Load Markdown templates for PowerPoint, Excel, Word, Markdown and MCP instructions.

    Returns:
        tuple[str, str, str, str, str]: A tuple containing the Markdown templates for
                                        PowerPoint, Excel, Word, Markdown and the MCP instructions.
    """

    try:
        # Load Markdown template files using importlib.resources
        with resources.files("src").joinpath("powerpoint.md").open("r", encoding="utf-8") as f:
            POWERPOINT_TEMPLATE = f.read()

        with resources.files("src").joinpath("excel.md").open("r", encoding="utf-8") as f:
            EXCEL_TEMPLATE = f.read()

        with resources.files("src").joinpath("word_template.md").open("r", encoding="utf-8") as f:
            WORD_TEMPLATE = f.read()

        with resources.files("src").joinpath("markdown.md").open("r", encoding="utf-8") as f:
            MARKDOWN_TEMPLATE = f.read()

        with resources.files("src").joinpath("mcp_instructions.md").open("r", encoding="utf-8") as f:
            MCP_INSTRUCTIONS = f.read()

        logger.info("=> Markdown templates loaded successfully.")

        return (
            POWERPOINT_TEMPLATE,
            EXCEL_TEMPLATE,
            WORD_TEMPLATE,
            MARKDOWN_TEMPLATE,
            MCP_INSTRUCTIONS
        )
    
    except Exception as e:

        logger.error(f"=> Error loading Markdown templates")
        raise e