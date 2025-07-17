# CrossRef MCP Server

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io/)
[![Smithery](https://img.shields.io/badge/Smithery-Hosted-purple)](https://smithery.ai/)

A Model Context Protocol (MCP) server that validates and formats academic references using the CrossRef API.

## Features

- Validate academic references against the CrossRef database
- Format citations in APA or Harvard styles
- Direct DOI lookup and formatting
- Batch processing of multiple references
- Markdown and plain text output formats

## Installation

### Smithery (Recommended)

1. Install the server:
   ```bash
   npx -y @smithery/cli@latest install @jusi-aalto/crossref-mcp --client claude
   ```

2. Add the provided configuration to your Claude Desktop config file:

   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

   ```json
   {
     "mcpServers": {
       "crossref-mcp": {
         "command": "npx",
         "args": [
           "-y",
           "@smithery/cli@latest",
           "run",
           "@jusi-aalto/crossref-mcp",
           "--key",
           "YOUR_SMITHERY_KEY"
         ]
       }
     }
   }
   ```

3. Restart Claude Desktop

### Local Installation

1. Clone and install:
   ```bash
   git clone https://github.com/jusi-aalto/crossref-mcp.git
   cd crossref-mcp
   pip install -r requirements.txt
   ```

2. Add to Claude Desktop config:
   ```json
   {
     "mcpServers": {
       "crossref": {
         "command": "python",
         "args": ["path/to/crossref-mcp/crossref_mcp.py"]
       }
     }
   }
   ```

## Usage

### Available Tools

**validate_references** - Validates multiple references
- `references`: Array of reference strings
- `style`: Citation style (`apa` or `harvard`)
- `format_type`: Output format (`markdown` or `text`)

**format_reference** - Formats a single reference or DOI
- `reference`: Reference string or title (optional)
- `doi`: DOI to format directly (optional)
- `style`: Citation style (`apa` or `harvard`)
- `format_type`: Output format (`markdown` or `text`)

### Examples

**Validate a reference:**
> "Please validate: Bharadwaj 2000 MIS Quarterly"

**Format a DOI:**
> "Format DOI 10.2307/3250983 in APA style"

**Batch processing:**
> "Validate these references: Porter 1985 competitive advantage, Barney 1991 firm resources"

## Citation Styles

**APA:** Author, A. B. (Year). Title. *Journal*, *volume*(issue), pages. https://doi.org/...

**Harvard:** Author, A.B. (Year) 'Title', *Journal*, vol. volume, no. issue, pp. pages, doi: ...

## Requirements

- **Smithery:** No local requirements
- **Local:** Python 3.8+, CrossRef API (free, no key required)

## License

MIT

## Links

- [Repository](https://github.com/jusi-aalto/crossref-mcp)
- [Smithery](https://smithery.ai/servers/@jusi-aalto/crossref-mcp)
- [CrossRef API](https://api.crossref.org/)
