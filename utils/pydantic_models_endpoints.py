from pydantic import BaseModel
from typing import List
from pydantic import Field, BaseModel
from utils.argument_descriptions import ARGUMENT_DESCRIPTIONS
from utils.pydantic_models_arguments import (
    Cover,
    ParagraphListItem,
    Table,
    Image,
    Equation,
    ParagraphHeader,
    ParagraphBody,
    ReviewComment
)

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
    document_paragraphs: List[ParagraphBody] = Field(description="List of paragraph body elements.")
    document_headers: List[ParagraphHeader] = Field(description="List of header elements.")
    document_lists: List[ParagraphListItem] = Field(default=[], description="List of list elements.")
    document_tables: List[Table] = Field(default=[], description="List of table elements.")
    document_images: List[Image] = Field(default=[], description="List of image elements.")
    document_equations: List[Equation] = Field(default=[], description="List of equation elements.")
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])

class FullContextDocxRequest(BaseModel):
    file_id: str = Field(description=ARGUMENT_DESCRIPTIONS["full_context_docx"]["file_id"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["full_context_docx"]["file_name"])

class ReviewDocxRequest(BaseModel):
    file_id: str = Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["file_id"])
    review_comments: List[ReviewComment] = Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["review_comments"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["file_name"])
