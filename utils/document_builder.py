from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import math2docx
import os
import numpy as np
from utils.download_file import download_file
from utils.authorization import _get_bearer_token

def vertical_center(metadata_dict: dict, doc: Document) -> int:
    # Constantes
    EMU_INCH = 914400
    CHAR_WIDTH_FACTOR = 0.7  # Ancho promedio de cada carácter como fracción del tamaño de la fuente
    DEFAULT_LINE_HEIGHT = 0.1667  # Altura de línea en pulgadas (12 pt)

    # Tamaños de fuente por clave (en pulgadas)
    font_sizes = {
        'title': 0.5,
        'subtitle': DEFAULT_LINE_HEIGHT,
        'description': DEFAULT_LINE_HEIGHT,
        'author': DEFAULT_LINE_HEIGHT,
        'month': DEFAULT_LINE_HEIGHT,
        'year': DEFAULT_LINE_HEIGHT,
    }

    # Dimensiones de página y márgenes (en pulgadas)
    section = doc.sections[0]
    page_height = section.page_height / EMU_INCH
    page_width = section.page_width / EMU_INCH
    top_margin = section.top_margin / EMU_INCH
    bottom_margin = section.bottom_margin / EMU_INCH
    left_margin = section.left_margin / EMU_INCH
    right_margin = section.right_margin / EMU_INCH

    # Ancho útil de página
    useful_width = page_width - left_margin - right_margin

    # Calcular espacio vertical total usado
    total_vertical_space_used = 0.0
    keys = ['title', 'subtitle', 'description', 'author', 'month', 'year']

    for key in keys:
        text = metadata_dict.get(key, "")
        length = len(text)
        font_size = font_sizes.get(key, DEFAULT_LINE_HEIGHT)
        text_width = length * font_size * CHAR_WIDTH_FACTOR
        lines_used = int(np.ceil(text_width / useful_width)) if useful_width > 0 else 1
        # Espacio vertical: líneas * altura de línea + interlineado extra
        space_used = lines_used * font_size + max(0, lines_used - 1) * font_size
        total_vertical_space_used += space_used

    # Espacio restante y líneas vacías
    useful_height = page_height - top_margin - bottom_margin
    remaining_space = (useful_height - total_vertical_space_used) / 2
    empty_lines = np.ceil(remaining_space / (2 * DEFAULT_LINE_HEIGHT))  # Manteniendo la lógica original

    return int(empty_lines) + 1

def build_docx_from_dict(doc_dict, buffer, ctx, URL):
    doc = Document()

    empty_lines = vertical_center(doc_dict["metadata"], doc)

    # Parrafos para centrar verticalmente no están soportados en python-docx/DOCX
    for _ in range(empty_lines):
        doc.add_paragraph("")
    
    # Aplicar metadata como portada centrada horizontalmente
    if "metadata" in doc_dict:
        meta = doc_dict["metadata"]
        if "title" in meta:
            title = doc.add_paragraph(meta["title"])
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title.runs[0].bold = True
            title.runs[0].font.size = Inches(0.5)  # Tamaño grande para título
            title.runs[0].font.name = doc_dict.get("font", "Arial")
        if "subtitle" in meta:
            subtitle = doc.add_paragraph(meta["subtitle"])
            subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
            subtitle.runs[0].italic = True
            subtitle.runs[0].font.size = Inches(0.1667)  # Tamaño mediano para subtítulo
            subtitle.runs[0].font.name = doc_dict.get("font", "Arial")
        if "description" in meta:
            desc = doc.add_paragraph(meta["description"])
            desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
            desc.runs[0].font.size = Inches(0.1667)  
            desc.runs[0].font.name = doc_dict.get("font", "Arial")
        if "author" in meta:
            author = doc.add_paragraph(f"Autor: {meta['author']}")
            author.alignment = WD_ALIGN_PARAGRAPH.CENTER
            author.runs[0].font.size = Inches(0.1667)
            author.runs[0].font.name = doc_dict.get("font", "Arial")
        if "month" in meta and "year" in meta:
            date = doc.add_paragraph(f"{meta['month']} {meta['year']}")
            date.alignment = WD_ALIGN_PARAGRAPH.CENTER
            date.runs[0].font.size = Inches(0.1667)
            date.runs[0].font.name = doc_dict.get("font", "Arial")
        # Nota: La alineación vertical de página no está soportada en python-docx/DOCX
        # Agregar salto de página después de la portada
        doc.add_page_break()
    
    # Contadores para numeración automática de captions
    figure_counter = 1
    table_counter = 1
    equation_counter = 1
    
    # Procesar secciones
    for section in doc_dict.get("sections", []):
        # Agregar título de sección
        heading = doc.add_heading(section["title"], level=section.get("level", 2))
        if section.get("alignment") == "center":
            heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        heading.runs[0].font.name = doc_dict.get("font", "Arial")
        
        # Si la sección tiene columnas, agregar una nueva sección con columnas
        if section.get("columns"):
            new_section = doc.add_section()
            sectPr = new_section._sectPr
            cols = OxmlElement('w:cols')
            cols.set(qn('w:num'), str(section["columns"]))
            sectPr.append(cols)
        
        # Procesar párrafos
        if section.get("paragraphs"):
            for item in section["paragraphs"]:
                p = doc.add_paragraph(item["text"])
                if item.get("bold"):
                    for run in p.runs:
                        run.bold = True
                if item.get("italic"):
                    for run in p.runs:
                        run.italic = True
                for run in p.runs:
                    run.font.size = Inches(12 / 72)
                    run.font.name = doc_dict.get("font", "Arial")
                if item.get("alignment") == "center":
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif item.get("alignment") == "justify":
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        # Procesar listas
        if section.get("lists"):
            for list_item in section["lists"]:
                for item in list_item["items"]:
                    p = doc.add_paragraph(item, style='List Bullet' if list_item.get("style") == "bullet" else 'List Number')
                    p.runs[0].font.name = doc_dict.get("font", "Arial")
        
        # Procesar tablas
        if section.get("tables"):
            for item in section["tables"]:
                # Validación básica
                if not item.get("headers") or not item.get("rows"):
                    raise ValueError("Tabla debe tener headers y rows.")
                # Numeración automática si no hay caption personalizado
                caption_text = item.get("caption", f"Tabla {table_counter}: ")
                if not item.get("caption"):
                    table_counter += 1
                p = doc.add_paragraph(caption_text, style='Caption')
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                table = doc.add_table(rows=1, cols=len(item["headers"]))
                table.style = 'Light List Accent 1'
                hdr_cells = table.rows[0].cells
                for i, hdr in enumerate(item["headers"]):
                    hdr_cells[i].text = hdr
                    for run in hdr_cells[i].paragraphs[0].runs:
                        run.font.name = doc_dict.get("font", "Arial")
                for row_data in item["rows"]:
                    row_cells = table.add_row().cells
                    for i, cell_data in enumerate(row_data):
                        row_cells[i].text = cell_data
                        for run in row_cells[i].paragraphs[0].runs:
                            run.font.name = doc_dict.get("font", "Arial")
        
        # Procesar imágenes
        if section.get("images"):
            for item in section["images"]:
                # Descargar imagen
                bearer_token = _get_bearer_token(ctx)
                image_file = download_file(URL, bearer_token, item["id"])
                if isinstance(image_file, dict) and "error" in image_file:
                    raise ValueError(f"Error downloading image with ID {item['id']}: {image_file['error']['message']}")
                doc.add_picture(image_file, width=Inches(item.get("width", 6.0)), height=Inches(item.get("height", 4.0)))
                # Numeración automática si no hay caption personalizado
                caption_text = item.get("caption", f"Figura {figure_counter}: ")
                if not item.get("caption"):
                    figure_counter += 1
                p = doc.add_paragraph(caption_text, style='Caption')
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Procesar ecuaciones
        if section.get("equations"):
            for eq in section["equations"]:
                p = doc.add_paragraph()
                math2docx.add_math(p, eq["latex"])
                if eq.get("caption"):
                    caption_text = eq.get("caption", f"Ecuación {equation_counter}: ")
                    if not eq.get("caption"):
                        equation_counter += 1
                    p_cap = doc.add_paragraph(caption_text, style='Caption')
                    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    


    doc.save(buffer)
    buffer.seek(0)
    return buffer