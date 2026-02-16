from pydantic import BaseModel
from typing import List
from pydantic import Field, BaseModel
from utils.argument_descriptions import ARGUMENT_DESCRIPTIONS
from utils.logger import get_logger
from utils.pydantic_models_arguments import (
    Cover,
    ReviewComment,
    DocumentElement
)

logger = get_logger(__name__)

# --- Request Models for API Endpoints ---
class GeneratePowerPointRequest(BaseModel):
    python_script: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["python_script"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])

class GenerateExcelRequest(BaseModel):
    python_script: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["python_script"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])

class GenerateMarkdownRequest(BaseModel):
    python_script: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["python_script"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])
 
class DocxBodyElements(BaseModel):
    document_cover: Cover = Field(description="This argument defines the cover page of the document. Set page_break to True for generating general reports and False for academic papers. Backend is able to center the cover page content automatically so no need to add extra spaces or new lines.")
    columns_body: int = Field(description="This argument defines the number of columns in the document body. Set to 1 for single column or 2 for double column layout for academic papers.")
    document_elements: List[DocumentElement] = Field(description="Ordered list of document elements used to build the body. The backend preserves this order as-is. Use EXACTLY one valid value for each element type: ParagraphBody|ParagraphHeader|ParagraphListItem|Table|Image|Equation. Do NOT use aliases such as header_element, paragraph_element, list_element. For each element, provide content only in the matching nested field (paragraph, header, list_item, table, image, equation).")
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])

class FullContextDocxRequest(BaseModel):
    file_id: str = Field(description=ARGUMENT_DESCRIPTIONS["full_context_docx"]["file_id"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["full_context_docx"]["file_name"])

class ReviewDocxRequest(BaseModel):
    file_id: str = Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["file_id"])
    review_comments: List[ReviewComment] = Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["review_comments"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["file_name"])

logger.info("=> Pydantic endpoint models loaded successfully.")
