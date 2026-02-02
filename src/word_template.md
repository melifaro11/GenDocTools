This tool generates a Word document for reports or academic papers.

### How it works:
- All elements across all lists must have unique `index_element` values (integers starting from 1).
- The backend sorts all elements by `index_element` and builds the document in that order.
- `index_element` by element are not necessarily sequential; gaps are allowed because it depends on the combination of elements used.

### Requirements:

- Use paragraphs of no more than 4 lines. For line breaks within a paragraph, use \n. To separate paragraphs, use double line breaks \n\n. Paragraphs support bold and italic text using **bold text** and *italic text*, respectively. Only document_paragraphs elements can contain bold and italic formatting; other elements do not support text formatting.
- No lists or equations in paragraph text; use separate `document_lists` or `document_equations`.
- Captions required for tables, images, equations.
- Unique `index_element` values.
- Use Unicode characters directly (e.g., ∑, not \\u2211).

### Logic behind the smart ordering and generation of a DOCX file:

If you as an AI assistant, according to the user's request, plan to create a document with the following sequence of elements:

1. Header: "Introduction"
2. Paragraph: "This is the first paragraph of the document..."
3. Table: "Table 1: Sample Data"
4. Header: "Background"
5. Paragraph: "This is another paragraph that follows a header."
6. List: Bullet list with three items
7. Image: "Fig. 1: Sample Image"
8. Equation: "Equation 1: Einstein's Mass-Energy Equivalence"
9. Paragraph: "This is an example with **bold** and *italic* text."

You have to set up the elements with the following `index_element` values:

- document_headers = [1, 4]
- document_paragraphs = [2, 5, 9]
- document_tables = [3]
- document_lists = [6]
- document_images = [7]
- document_equations = [8]

In this example, the backend will create the DOCX file by ordering all elements based on their `index_element` values from 1 to 9. This document will have a logical order, easily readable for humans.

