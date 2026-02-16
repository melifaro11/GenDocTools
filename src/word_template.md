This tool generates a Word document for reports or academic papers.

### Current input model (must follow exactly)

Send a single request body with:

- `document_cover`: cover metadata (`title`, `subtitle`, `description`, `author`, `month`, `year`, `page_break`).
- `columns_body`: number of columns in body (`1` or `2`).
- `document_elements`: ordered list of body elements.
- `file_name`: output file name (without extension).

### Element contract

Each item in `document_elements` must:

1. Include `type` with exactly one value from:
	- `ParagraphBody`
	- `ParagraphHeader`
	- `ParagraphListItem`
	- `Table`
	- `Image`
	- `Equation`
2. Populate only the matching nested field:
	- `type=ParagraphBody` -> use `paragraph`
	- `type=ParagraphHeader` -> use `header`
	- `type=ParagraphListItem` -> use `list_item`
	- `type=Table` -> use `table`
	- `type=Image` -> use `image`
	- `type=Equation` -> use `equation`
3. Leave all non-matching nested fields as `null` or omitted.

### Content requirements

- Paragraph text can use Markdown emphasis: `**bold**`, `*italic*`.
- Keep paragraphs concise (prefer up to 4 lines).
- Use `\n` for line breaks inside a paragraph and `\n\n` to separate paragraphs.
- Captions are required for `Table`, `Image`, and `Equation`.
- For lists, `list_style` must be `List Number` or `List Bullet`.
- Use Unicode characters directly (for example `∑`, not `\\u2211`).

