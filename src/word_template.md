Generates a Word document for reports or academic papers.

This tool requires specifying the file name and the cover page information, such as title, subtitle, description, and author. Additionally, the document layout must be defined as either single-column for general reports or double-column for academic papers.

The document content is constructed by adding elements in sequence. Available elements include section headings for structure and paragraphs for text. Use the dedicated list element for bulleted or numbered lists, the equation element for mathematical formulas, and the specific formatting element for bold or italic text. Do not use Markdown syntax, and avoid attempting to format lists, equations, or styled text manually within paragraphs, as these will not render correctly. Tables and images are also supported as individual elements.

# Arguments

- **file_name**: str - The desired name of the Word file (without extension).

- **document_cover**: A Cover object containing:
  - title: str - The main title of the document.
  - subtitle: str - The subtitle.
  - description: str - A brief description.
  - author: str - The author's name.
  - month: str - The month (e.g., "January").
  - year: str - The year (e.g., "2023").
  - page_break: bool - Whether to add a page break after the cover (default: false). 

- **columns_body**: int - Number of columns for the body sections (1 or 2). 1 is for general reports, 2 is for papers following academic formats.

- **document_body_elements**: A list of document elements, the order of elements defines their sequence in the document. Supported elements include:
  - **type**: "ParagraphHeader", "ParagraphBody", "ParagraphListItem", "Table", "Image", "Equation" or "WordsWithBoldOrItalic"

    - **ParagraphHeader type**: Use this element to create a heading.
      - type: "ParagraphHeader"
      - text: str - The heading text.
      - level: int (1-6) - The heading level (1 for main title, 2 for section, etc.).

    - **ParagraphBody type**: Use this element to create a paragraph of text.
      - type: "ParagraphBody"
      - text: str - The paragraph text. Use '\n\n' for paragraph breaks.
      - **Never use markdown formatting only plain text**.
      - **Never use bold or italic formatting in this element, use WordsWithBoldOrItalic instead**.

    - **WordsWithBoldOrItalic type**: Use this element to add words or phrases with bold or italic formatting within a paragraph.
      - type: "WordsWithBoldOrItalic"
      - text: str - The text content.
      - bold: bool - Whether the text is bold.
      - italic: bool - Whether the text is italic.
      - **Never use markdown formatting only plain text**.

    - **ParagraphListItem type**: Use this element to create a list (bulleted or numbered).
      - type: "ParagraphListItem"
      - list_style: str - "List Number" for numbered list or "List Bullet" for bulleted list.
      - items: List[str] - The list of item texts.

    - **Table type**: Use this element to create a table.
      - type: "Table"
      - headers: List[str] - The table headers.
      - rows: List[List[str]] - The table rows, each as a list of cell values.
      - caption: Optional[str] - An optional caption for the table.

    - **Image type**: Use this element to insert an image.
      - type: "Image"
      - id: str - The image file ID (preloaded by the server).
      - caption: Optional[str] - An optional caption for the image.

    - **Equation type**: Use this element to insert a mathematical equation. 
      - type: "Equation"
      - latex: str - The LaTeX code for the equation.
      - caption: Optional[str] - An optional caption for the equation.