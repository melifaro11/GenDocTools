## Table of Contents

- [Features](#features)
- [Status / Compatibility](#status--compatibility)

## Features
- **File Generation**: Creates files in multiple formats (PowerPoint, Excel, Word, Markdown) from user requests.
- **MCP Server**: Exposes tools via the Model Context Protocol for seamless integration with LLMs.
- **MCPO Support**: Can run behind [mcpo](https://github.com/open-webui/mcpo), allowing teams to reuse an existing MCPO deployment instead of running GenFilesMCP as another standalone container or web app.
- **Python Templates**: Uses customizable Python templates to generate files with specific structures.
- **OWUI Integration**: Automatically uploads generated files to Open Web UI's file API (`/api/v1/files/`) and uses the knowledge APIs (`/api/v1/knowledge/search`, `/api/v1/knowledge/create`, `/api/v1/knowledge/{id}/file/add`) when knowledge persistence is enabled.
- **Document Review**: Analyzes existing Word documents and adds structured comments for corrections, grammar suggestions, or idea enhancements.
- **Image Embedding**: Supports embedding images from chat uploads directly into generated Word documents.
- **Knowledge Base Integration**: Generated and reviewed documents can be stored in Open Web UI knowledge collections for later access, download, deletion, and reuse from other chats.
- **Multi-User Support**: Designed for environments with multiple users, supporting per-user or group-oriented document access patterns depending on the selected deployment mode.

## Status / Compatibility

This release is **v0.3.0** and was tested with Open Web UI v0.8.8: [Open Web UI GitHub Repository](https://github.com/open-webui/open-webui)

**Important compatibility note:** native MCP support appeared in **Open Web UI v0.6.31**, and the paginated knowledge API used by this release arrived in **v0.6.42**. Because Open Web UI has changed significantly since then, the recommended minimum for this release is **v0.8.8**. For Open Web UI versions earlier than v0.6.42, use previous GenFiles releases **<= 0.2.2**.

The `ENABLE_CREATE_KNOWLEDGE` variable lets deployments choose whether generated or reviewed files are automatically added to users' knowledge collections. The original behavior (downloading files from chats) remains unchanged for end users.

The base knowledge collection name is controlled by `KNOWLEDGE_COLLECTION_NAME` in both `streamable-http` and `stdio` modes, and generated and reviewed files are stored in that same collection when knowledge persistence is enabled.

`OWUI_API_KEY` is intended only for `stdio` deployments served through MCPO. In `stdio` through MCPO, `ENABLE_CREATE_KNOWLEDGE=true` is **mandatory** because that is the mechanism that makes generated or reviewed files available to end users through group-based knowledge sharing in Open Web UI.