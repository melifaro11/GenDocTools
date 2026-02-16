
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
    #type: Literal["ParagraphListItem"] = Field(..., description="Discriminator for the list item element.")
    list_style: Literal['List Number', 'List Bullet'] = Field(..., description="Required. Allowed values: 'List Number' | 'List Bullet'.")
    items: List[str] = Field(..., description="List entries. Provide 1+ non-empty strings, each one a separate item.")
    #index_element: int = Field(..., description="Unique index across all document elements for global ordering in the document. Values must be unique integers starting from 1 or higher, and do not need to be consecutive.")

class Table(BaseModel):
    #type: Literal["Table"] = Field(..., description="Discriminator for the table element.")
    table_headers: List[str] = Field(..., description="Column headers in display order.")
    table_rows: List[List[str]] = Field(..., description="Table rows. Each row must match the number of headers.")
    caption: str = Field(..., description="Required table caption shown under/near the table.")
    #index_element: int = Field(..., description="Unique index across all document elements for global ordering in the document. Values must be unique integers starting from 1 or higher, and do not need to be consecutive.")

class Image(BaseModel):
    #type: Literal["Image"] = Field(..., description="Discriminator for the image element.")
    id: str = Field(..., description="Required image file id from the file storage system.")
    caption: str = Field(...,description="Required figure caption. Keep it short and descriptive.")
    #index_element: int = Field(..., description="Unique index across all document elements for global ordering in the document. Values must be unique integers starting from 1 or higher, and do not need to be consecutive.")

class Equation(BaseModel):
    #type: Literal["Equation"] = Field(..., description="Discriminator for the equation element.")
    latex: str = Field(..., description="Required LaTeX expression, for example: E=mc^2.")
    caption: str = Field(..., description="Required equation caption.")
    #index_element: int = Field(..., description="Unique index across all document elements for global ordering in the document. Values must be unique integers starting from 1 or higher, and do not need to be consecutive.")

class ParagraphHeader(BaseModel):
    #type: Literal["ParagraphHeader"] = Field(..., description="Discriminator for the header element.")
    text: str = Field(..., description="Heading text in plain language.")
    level: Literal[1,2,3,4,5,6] = Field(..., description="Heading level from 1 (main section) to 6 (minor subsection).")
    #index_element: int = Field(..., description="Unique index across all document elements for global ordering in the document. Values must be unique integers starting from 1 or higher, and do not need to be consecutive.")

class ParagraphBody(BaseModel):
    #type: Literal["ParagraphBody"] = Field(..., description="Discriminator for the paragraph element.")
    text: str = Field(..., description="Paragraph content. Markdown emphasis is allowed: **bold** and *italic*.")
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
    type: elements_lit = Field(..., description="Use EXACTLY one of: ParagraphBody|ParagraphHeader|ParagraphListItem|Table|Image|Equation. Do NOT use: header_element, paragraph_element, list_element.")
    
    paragraph: Optional[ParagraphBody] = Field(default=None, description=f"Use only when type='ParagraphBody'. Omit for any other type. {_fields_summary(ParagraphBody)}")
    header: Optional[ParagraphHeader] = Field(default=None, description=f"Use only when type='ParagraphHeader'. Omit for any other type. {_fields_summary(ParagraphHeader)}")
    list_item: Optional[ParagraphListItem] = Field(default=None, description=f"Use only when type='ParagraphListItem'. Omit for any other type. {_fields_summary(ParagraphListItem)}")
    table: Optional[Table] = Field(default=None, description=f"Use only when type='Table'. Omit for any other type. {_fields_summary(Table)}")
    image: Optional[Image] = Field(default=None, description=f"Use only when type='Image'. Omit for any other type. {_fields_summary(Image)}")
    equation: Optional[Equation] = Field(default=None, description=f"Use only when type='Equation'. Omit for any other type. {_fields_summary(Equation)}")

logger.info("=> Pydantic argument models loaded successfully.")


