# CrossRef MCP Server

MCP server for validating and formatting academic references using the CrossRef API.

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Add to Claude Desktop configuration (`%APPDATA%\Claude\claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "crossref": {
         "command": "python",
         "args": ["C:/Users/sihvonj2/Downloads/claude/crossref-mcp/crossref_mcp.py"]
       }
     }
   }
   ```

3. Restart Claude Desktop.

## Tools

- **validate_references**: Validates batches of references
- **format_reference**: Formats single references or DOIs

## Usage

Ask Claude to validate references:
- "Please validate: Bharadwaj 2000 MIS Quarterly"
- "Format DOI 10.2307/3250983 in APA style"

## Features

- APA and Harvard citation styles
- Markdown and plain text output
- Direct DOI lookup
- Batch processing
