This server provides tools specialized in generating `.docx`, `.xlsx`, `.md`, `.pptx` and reviewing `.docx` documents.


# Tools
### `generate_excel`
- Use clear headers, freeze top rows, and enable filters where appropriate.
- Ensure data types are correct (dates, numbers, currency).
- Auto-fit columns and use professional color schemes.
- Use charts to visualize data.

### `generate_word`
- Creates Word documents for academic papers, reports, or regular documents.
- Supports formats like IEEE, set `page_break` to false and `columns_body` to 2 for this style.
- For general reports, set `page_break` to true and `columns_body` to 1.
- Never user markdown syntax for bold or italic text. Use the `bold` and `italic` fields instead.
- For equations, use only LaTeX format. Never use Markdown format.
- Includes elements like:
  - **Headings**: Section titles with levels (1-6).
  - **Paragraphs**: Plain text and alignment options.  
  - **Words with Bold or Italic**: Words or phrases with bold and/or italic formatting. Do not use Markdown syntax like **bold** or *italic*, as it may not render correctly. Set the `bold` and `italic` fields to true or false as needed.
  - **Separate paragraphs**: To create separate paragraphs within the text, use '\n\n' for paragraph breaks.
  - **Lists**: Numbered or bulleted.
  - **Tables**: With headers, rows, and captions.
  - **Images**: With ID and captions.
  - **Equations**: In LaTeX with captions.

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
