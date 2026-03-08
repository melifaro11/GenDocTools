import json
from pydantic import BaseModel
from typing import List, Literal, Optional, get_args, get_origin
from pydantic import Field, BaseModel, model_validator
from utils.logger import get_logger

logger = get_logger(__name__)

# --- Models for review comments and document elements ---
class ReviewComment(BaseModel):
    index: int
    comment: str

class ImagesList(BaseModel):
    images: str

# --- Models for docx document structure --- 
class Cover(BaseModel):
    title: str = Field(..., description="Cover title. Use a short, specific title.")
    subtitle: str = Field(..., description="Cover subtitle. Use only if it adds context.")
    description: str = Field(..., description="One concise sentence describing the purpose of the document.")
    author: str = Field(..., description="Author name as it should appear on the cover.")
    month: str = Field(..., description="Publication month in plain text, for example: 'January'.")
    year: str = Field(..., description="Publication year in 4 digits, for example: '2024'.")
    page_break: bool = Field(..., description="Set true to start body content on a new page after the cover; false to continue immediately.")

class ParagraphListItem(BaseModel):
    list_style: Literal['List Number', 'List Bullet'] = Field(..., description="When adding a list to a docx document, choose either 'List Number' or 'List Bullet' based on the desired formatting style.")
    items: List[str] = Field(..., description="List entries must include one or more non-empty strings, with each string representing a separate item. This type does not support Markdown formatting for bold or italic text. Do not use this type for equations; use the 'Equation' type instead to ensure proper formatting.")
   
class Table(BaseModel):
    table_headers: List[str] = Field(..., description="Column headers in display order.")
    table_rows: List[List[str]] = Field(..., description="Table rows. Each row must match the number of headers.")
    caption: str = Field(..., description="Caption for the table. Captions should be brief and concise. For example: 'Table 1: Summary of experimental results.'")

class Image(BaseModel):
    id: str = Field(..., description="Unique file ID of the image. Use the `chat_context` tool to retrieve the IDs of images uploaded in the conversation chat. This allows the backend to download the image and include it in the document. Do not modify the ID format, as it must remain a unique string that identifies the uploaded image.")
    caption: str = Field(..., description="Caption for the image. Captions should be brief and concise. For example: 'Figure 1: Diagram of the experimental setup.'")
    
class Equation(BaseModel):
    latex: str = Field(..., description="Required LaTeX expression, for example: E = mc^{2}")
    caption: str = Field(..., description="Caption for the equation. Captions should be brief and concise. For example: 'Equation 1: Einstein's mass-energy equivalence.'")
    
class ParagraphHeader(BaseModel):
    text: str = Field(..., description="Heading text in plain language. Markdown formatting is not allowed")
    level: Literal[1,2,3,4,5,6] = Field(..., description="Heading level from 1 (main section) to 6 (minor subsection).")
    
class ParagraphBody(BaseModel):
    text: str = Field(
        ..., 
        description=(
            "Paragraph content. Markdown emphasis is allowed: **bold** and *italic*. "
            "Paragraphs should have a maximum of 50 words and minimun 38. Line breaks can be created by adding. For consecutive paragraphs, use multiple 'ParagraphBody' elements in the 'DocumentElement' list, as combining multiple paragraphs into a single 'ParagraphBody' will result in poorly formatted output. "
            "Do not include titles in this field; use the type 'ParagraphHeader' for titles, as using 'ParagraphBody' for titles will result in poorly formatted output. "
            "If you need to create lists, use the type 'ParagraphListItem', as using 'ParagraphBody' for list items will result in poorly formatted output. "
            "Similarly, do not use 'ParagraphBody' for equations; use the type 'Equation' instead to ensure proper formatting."
        )
    )
    #index_element: int = Field(..., description="Unique index across all document elements for global ordering in the document. Values must be unique integers starting from 1 or higher, and do not need to be consecutive.")

def _fields_summary(model: type[BaseModel]) -> str:
    required_fields = [name for name, info in model.model_fields.items() if info.is_required()]
    required_text = ", ".join(required_fields) if required_fields else "none"

    field_details = []
    json_example = {}
    for name, info in model.model_fields.items():
        description = info.description or "No description provided."
        annotation = info.annotation
        origin = get_origin(annotation)

        literal_options = get_args(annotation) if origin is Literal else ()
        if literal_options:
            options_text = " | ".join([f"'{opt}'" for opt in literal_options])
            field_details.append(f"{name}: {description} Allowed values: {options_text}.")
            json_example[name] = literal_options[0]
        elif origin is list:
            json_example[name] = ["..."]
            field_details.append(f"{name}: {description}")
        elif annotation in (int, float):
            json_example[name] = 1
            field_details.append(f"{name}: {description}")
        elif annotation is bool:
            json_example[name] = True
            field_details.append(f"{name}: {description}")
        else:
            json_example[name] = "..."
            field_details.append(f"{name}: {description}")

    details_text = " | ".join(field_details) if field_details else "No field details."
    example_text = json.dumps(json_example, ensure_ascii=False)
    return (
        f"All keys inside this object are required. "
        f"Required fields: [{required_text}]. "
        f"Field details: {details_text}. "
        f"JSON shape example: {example_text}."
    )

elements_lit = Literal[
    "ParagraphBody",
    "ParagraphHeader",
    "ParagraphListItem",
    "Table",
    "Image",
    "Equation"
] 
class DocumentElement(BaseModel):
    # index_element: int = Field(..., description="Unique index across all document elements for global ordering in the document. Values must be unique integers starting from 1.")
    type: elements_lit = Field(..., description="Specify exactly one of the following types: ParagraphBody, ParagraphHeader, ParagraphListItem, Table, Image, or Equation. Do not alter these literals, as it will cause backend failures.")
    
    paragraph: Optional[ParagraphBody] = Field(default=None, description=f"Use only when type='ParagraphBody'. Omit for any other type. {_fields_summary(ParagraphBody)}")
    header: Optional[ParagraphHeader] = Field(default=None, description=f"Use only when type='ParagraphHeader'. Omit for any other type. {_fields_summary(ParagraphHeader)}")
    list_item: Optional[ParagraphListItem] = Field(default=None, description=f"Use only when type='ParagraphListItem'. Omit for any other type. {_fields_summary(ParagraphListItem)}")
    table: Optional[Table] = Field(default=None, description=f"Use only when type='Table'. Omit for any other type. {_fields_summary(Table)}")
    image: Optional[Image] = Field(default=None, description=f"Use only when type='Image'. Omit for any other type. {_fields_summary(Image)}")
    equation: Optional[Equation] = Field(default=None, description=f"Use only when type='Equation'. Omit for any other type. {_fields_summary(Equation)}")

logger.info("=> Pydantic argument models loaded successfully.")


