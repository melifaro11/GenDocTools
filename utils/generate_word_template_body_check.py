
from json import dumps
from utils.logger import get_logger
from utils.pydantic_models_endpoints import DocxBodyElements
from typing import List, Dict, Union

logger = get_logger(__name__)

def generate_word_template_body_check(body: DocxBodyElements) -> Union[List, Dict]:
    """
    Checks the structure of the document elements in the request body for generating a Word document.
    This function ensures that each element in the document body has a clear and unambiguous structure, 
    with only one type defined (paragraph, header, list item, table, image, or equation). If an element has 
    multiple types or an unrecognized structure, it logs an error and returns an appropriate error message.

    Args:
        body (DocxBodyElements): The request body containing the document cover, body elements, and file name.
    Returns:
        A list of dictionaries representing the processed document elements or a dictionary containing an error message.
    """
    try:
    # Collect all elements (flatten nested dicts)
        all_elements = []
        raw_elements = []
        raw_elements.extend(body.document_elements)
        for e in raw_elements:

            aux_dict = {}

            if e.paragraph is not None and e.header is None and e.list_item is None and e.table is None and e.image is None and e.equation is None:
                aux_dict['text'] = e.paragraph.text
                aux_dict['type'] = "ParagraphBody"
            elif e.header is not None and e.paragraph is None and e.list_item is None and e.table is None and e.image is None and e.equation is None:
                aux_dict['text'] = e.header.text
                aux_dict['level'] = e.header.level
                aux_dict['type'] = "ParagraphHeader"
            elif e.list_item is not None and e.paragraph is None and e.header is None and e.table is None and e.image is None and e.equation is None:
                aux_dict['list_style'] = e.list_item.list_style
                aux_dict['items'] = e.list_item.items
                aux_dict['type'] = "ParagraphListItem"
            elif e.table is not None and e.paragraph is None and e.header is None and e.list_item is None and e.image is None and e.equation is None:
                aux_dict['table_headers'] = e.table.table_headers
                aux_dict['table_rows'] = e.table.table_rows
                aux_dict['caption'] = e.table.caption
                aux_dict['type'] = "Table"
            elif e.image is not None and e.paragraph is None and e.header is None and e.list_item is None and e.table is None and e.equation is None:
                aux_dict['id'] = e.image.id
                aux_dict['caption'] = e.image.caption
                aux_dict['type'] = "Image"
            elif e.equation is not None and e.paragraph is None and e.header is None and e.list_item is None and e.table is None and e.image is None:
                aux_dict['latex'] = e.equation.latex
                aux_dict['caption'] = e.equation.caption
                aux_dict['type'] = "Equation"
            else:
                logger.error(f"Element with id {e.id} has an unrecognized structure or multiple types. Stopping generation to avoid errors.")
                return dumps({"error": f"Element with id {e.id} has an unrecognized structure or multiple types. Please ensure each element has only one type defined."}, ensure_ascii=False)
            
            all_elements.append(aux_dict)
        return all_elements
    except Exception as e:
        logger.error(f"Error processing document elements: {e}")
        return {"error": "An error occurred while processing the document elements. Please check the structure of your input."}
