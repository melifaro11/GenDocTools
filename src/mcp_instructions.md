This server provides tools specialized in generating `.docx`, `.xlsx`, `.md`, `.pptx` and reviewing `.docx` documents.

# Tools
### `generate_excel`
- Use clear headers, freeze top rows, and enable filters where appropriate.
- Ensure data types are correct (dates, numbers, currency).
- Auto-fit columns and use professional color schemes.
- Use charts to visualize data.

### `generate_word`
- Generate Word documents from a structured dictionary schema validated with Pydantic models, ensuring type safety and schema compliance.
- The dictionary includes metadata (title, subtitle, description, author, date), sections with headings, paragraphs (with bold/italic/alignment), lists (bullet/number), tables (with headers/rows/captions), images (downloaded by ID), and equations (LaTeX-rendered).
- Use proper Heading styles (H1, H2, H3) for document hierarchy based on section levels.
- Include a Table of Contents for documents with multiple sections.
- Use consistent fonts (default Arial), spacing, and bullet points for readability.
- Images are downloaded dynamically and inserted with captions; preserve correct association with content.
- Equations are rendered using LaTeX syntax into Word's equation editor, preserving mathematical notation accurately.
- Documents are generated entirely in memory for efficiency and security, without executing dynamic scripts.

### `generate_powerpoint`
- Limit text per slide. Use bullet points and clear titles.
- Distribute content logically across slides. Use Speaker Notes for detailed explanations.

### `generate_markdown`
- Use standard Markdown syntax.
- Use headers, lists, and code blocks effectively.

### Reviewing Tools Docx Files
- Use `generate_word` to create a fully revised file.
- Use `full_context_docx` to map element indexes.
- Use `review_docx` to attach specific comments to elements `(index, comment)`. 

## Tools response formatting
- Each tool returns a markdown hyperlink to download the generated file or the reviewed docx. This hyperlink allows users to easily access and download the files directly from the chat interface.