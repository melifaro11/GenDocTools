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
    ReviewComment,
    DocumentElement
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
    # document_paragraphs: List[ParagraphBody | None] = Field(description="List of paragraph body elements. Each element must have a unique `index_element` (starting from 1, like 1, 2, 3, etc.) that determines its position in the document. All `index_element` values across all document elements (paragraphs, headers, lists, tables, images, equations) must be unique, as the document is built by sorting all elements by their `index_element` in ascending order, defining the logical order of the document body. Avoid more than 3 consecutive index_element values in this list to prevent monotonous sections; generating consecutive indices without mixing with other elements' indices could result in pages with only paragraphs.")
    # document_headers: List[ParagraphHeader | None] = Field(description="List of header elements. Each element must have a unique `index_element` (starting from 1, like 1, 2, 3, etc.) that determines its position in the document. All `index_element` values across all document elements (paragraphs, headers, lists, tables, images, equations) must be unique, as the document is built by sorting all elements by their `index_element` in ascending order, defining the logical order of the document body. Avoid more than 3 consecutive index_element values in this list to prevent monotonous sections; generating consecutive indices without mixing with other elements' indices could result in pages with only headers.")
    # document_lists: List[ParagraphListItem | None] = Field(default=[], description="List of list elements. Each element must have a unique `index_element` (starting from 1, like 1, 2, 3, etc.) that determines its position in the document. All `index_element` values across all document elements (paragraphs, headers, lists, tables, images, equations) must be unique, as the document is built by sorting all elements by their `index_element` in ascending order, defining the logical order of the document body. Avoid more than 3 consecutive index_element values in this list to prevent monotonous sections; generating consecutive indices without mixing with other elements' indices could result in pages with only lists.")
    # document_tables: List[Table | None] = Field(default=[], description="List of table elements. Each element must have a unique `index_element` (starting from 1, like 1, 2, 3, etc.) that determines its position in the document. All `index_element` values across all document elements (paragraphs, headers, lists, tables, images, equations) must be unique, as the document is built by sorting all elements by their `index_element` in ascending order, defining the logical order of the document body. Avoid more than 3 consecutive index_element values in this list to prevent monotonous sections; generating consecutive indices without mixing with other elements' indices could result in pages with only tables.")
    # document_images: List[Image | None] = Field(default=[], description="List of image elements. Each element must have a unique `index_element` (starting from 1, like 1, 2, 3, etc.) that determines its position in the document. All `index_element` values across all document elements (paragraphs, headers, lists, tables, images, equations) must be unique, as the document is built by sorting all elements by their `index_element` in ascending order, defining the logical order of the document body. Avoid more than 3 consecutive index_element values in this list to prevent monotonous sections; generating consecutive indices without mixing with other elements' indices could result in pages with only images.")
    # document_equations: List[Equation | None] = Field(default=[], description="List of equation elements. Each element must have a unique `index_element` (starting from 1, like 1, 2, 3, etc.) that determines its position in the document. All `index_element` values across all document elements (paragraphs, headers, lists, tables, images, equations) must be unique, as the document is built by sorting all elements by their `index_element` in ascending order, defining the logical order of the document body. Avoid more than 3 consecutive index_element values in this list to prevent monotonous sections; generating consecutive indices without mixing with other elements' indices could result in pages with only equations.")
    document_elements: List[DocumentElement] = Field(description="This argument is a list of all document elements (paragraphs, headers, lists, tables, images, equations) combined together. Each element in this list must have a unique `index_element` (starting from 1, like 1, 2, 3, etc.) that determines its position in the document. The backend will sort all elements in this list by their `index_element` in ascending order to build the document body in a logical order. This field is used for validation to ensure that all elements across the different categories have unique indices and to check for long consecutive runs of indices within each category to prevent monotonous sections.")
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["common_args"]["file_name"])

class FullContextDocxRequest(BaseModel):
    file_id: str = Field(description=ARGUMENT_DESCRIPTIONS["full_context_docx"]["file_id"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["full_context_docx"]["file_name"])

class ReviewDocxRequest(BaseModel):
    file_id: str = Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["file_id"])
    review_comments: List[ReviewComment] = Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["review_comments"])
    file_name: str = Field(description=ARGUMENT_DESCRIPTIONS["review_docx"]["file_name"])
