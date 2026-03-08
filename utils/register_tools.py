from collections.abc import Callable
from logging import Logger
from typing import Any

def register_word_tool(
	mcp: Any,
	logger: Logger,
	word_template: str,
	enable_word_element_filling: bool,
	generate_word_structured: Callable[..., Any],
	generate_word: Callable[..., Any],
) -> None:
	if enable_word_element_filling:
		mcp.tool(
			name="generate_word_structured",
			title="Generate Word",
			description=word_template,
		)(generate_word_structured)
		logger.info("Registered Word tool: generate_word_structured")
		return

	mcp.tool(
		name="generate_word",
		title="Generate Word",
		description=word_template,
	)(generate_word)
	logger.info("Registered Word tool: generate_word")
