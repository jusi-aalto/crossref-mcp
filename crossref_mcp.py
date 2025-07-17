#!/usr/bin/env python3
"""
CrossRef MCP Server - Validates and formats academic references using CrossRef API
"""

import asyncio
import json
import sys
import requests
from typing import List, Dict, Optional

# Import MCP components correctly
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types

def get_crossref_data(reference: str) -> Optional[Dict]:
    """
    Queries the CrossRef API to find a reference.
    """
    try:
        headers = {
            'User-Agent': 'CrossRef-MCP/1.0 (mailto:sihvonj2@gmail.com)'
        }
        params = {'query': reference, 'rows': 1}
        response = requests.get("https://api.crossref.org/works", params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['message']['items']:
            return data['message']['items'][0]
    except requests.exceptions.RequestException as e:
        print(f"CrossRef API error: {e}", file=sys.stderr)
        return None

def format_citation(item: Dict, style: str = 'apa', format_type: str = 'markdown') -> str:
    """
    Formats a citation from CrossRef metadata.
    """
    try:
        # Extract authors
        authors = item.get('author', [])
        author_str = ""
        if authors:
            author_parts = []
            for author in authors:
                if 'family' in author and 'given' in author:
                    initials = ''.join([n[0] + '.' for n in author['given'].split()])
                    author_parts.append(f"{author['family']}, {initials}")
            author_str = ' & '.join(author_parts)

        # Extract year
        year = ""
        if 'published-print' in item and 'date-parts' in item['published-print']:
            year = item['published-print']['date-parts'][0][0]
        elif 'published-online' in item and 'date-parts' in item['published-online']:
            year = item['published-online']['date-parts'][0][0]

        # Extract other fields
        title = item.get('title', [''])[0]
        journal = item.get('container-title', [''])[0]
        volume = item.get('volume', '')
        issue = item.get('issue', '')
        page = item.get('page', '')

        # Format based on style
        if format_type == 'markdown':
            if style == 'apa':
                citation = f"{author_str} ({year}). {title}. *{journal}*, *{volume}*({issue}), {page}."
            elif style == 'harvard':
                citation = f"{author_str} ({year}) '{title}', *{journal}*, {volume}({issue}), pp. {page}."
        else:  # plain text
            if style == 'apa':
                citation = f"{author_str} ({year}). {title}. {journal}, {volume}({issue}), {page}."
            elif style == 'harvard':
                citation = f"{author_str} ({year}) '{title}', {journal}, {volume}({issue}), pp. {page}."
        
        return citation

    except (KeyError, IndexError) as e:
        print(f"Citation formatting error: {e}", file=sys.stderr)
        return "Failed to parse metadata for formatting."

def validate_reference(reference: str, style: str = 'apa', format_type: str = 'markdown') -> Dict:
    """
    Validates a single reference and returns formatted result.
    """
    data = get_crossref_data(reference)
    
    if data and 'DOI' in data:
        doi = data['DOI']
        formatted_citation = format_citation(data, style, format_type)
        
        return {
            "original": reference,
            "formatted": formatted_citation,
            "doi": f"https://doi.org/{doi}",
            "metadata": {
                "title": data.get('title', [''])[0],
                "authors": [f"{a.get('family', '')}, {a.get('given', '')}" for a in data.get('author', [])],
                "year": data.get('published-print', {}).get('date-parts', [[None]])[0][0] or 
                        data.get('published-online', {}).get('date-parts', [[None]])[0][0],
                "journal": data.get('container-title', [''])[0],
                "volume": data.get('volume', ''),
                "issue": data.get('issue', ''),
                "pages": data.get('page', '')
            }
        }
    else:
        return {
            "original": reference,
            "formatted": "Failed to find a match.",
            "doi": "N/A",
            "metadata": None
        }

# Create the MCP server
server = Server("crossref-mcp")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    """
    return [
        types.Tool(
            name="validate_references",
            description="Validates a batch of references using the CrossRef API",
            inputSchema={
                "type": "object",
                "properties": {
                    "references": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of reference strings to validate"
                    },
                    "style": {
                        "type": "string",
                        "enum": ["apa", "harvard"],
                        "default": "apa",
                        "description": "Citation style"
                    },
                    "format_type": {
                        "type": "string", 
                        "enum": ["markdown", "text"],
                        "default": "markdown",
                        "description": "Output format"
                    }
                },
                "required": ["references"]
            }
        ),
        types.Tool(
            name="format_reference",
            description="Formats a single reference using CrossRef data",
            inputSchema={
                "type": "object",
                "properties": {
                    "reference": {
                        "type": "string",
                        "description": "Reference string or title to format"
                    },
                    "doi": {
                        "type": "string",
                        "description": "Optional DOI to use directly"
                    },
                    "style": {
                        "type": "string",
                        "enum": ["apa", "harvard"],
                        "default": "apa",
                        "description": "Citation style"
                    },
                    "format_type": {
                        "type": "string",
                        "enum": ["markdown", "text"],
                        "default": "markdown",
                        "description": "Output format"
                    }
                },
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    """
    if name == "validate_references":
        references = arguments.get("references", [])
        style = arguments.get("style", "apa")
        format_type = arguments.get("format_type", "markdown")
        
        results = []
        for ref in references:
            if ref.strip():
                result = validate_reference(ref.strip(), style, format_type)
                results.append(result)
        
        output = {
            "results": results,
            "summary": {
                "total": len(results),
                "found": sum(1 for r in results if r["doi"] != "N/A"),
                "not_found": sum(1 for r in results if r["doi"] == "N/A")
            }
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(output, indent=2)
        )]
    
    elif name == "format_reference":
        reference = arguments.get("reference", "")
        doi = arguments.get("doi")
        style = arguments.get("style", "apa")
        format_type = arguments.get("format_type", "markdown")
        
        if doi:
            # Query directly by DOI
            try:
                headers = {'User-Agent': 'CrossRef-MCP/1.0'}
                response = requests.get(f"https://api.crossref.org/works/{doi}", headers=headers)
                response.raise_for_status()
                data = response.json()['message']
                formatted = format_citation(data, style, format_type)
                
                output = {
                    "formatted": formatted,
                    "doi": f"https://doi.org/{doi}"
                }
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(output, indent=2)
                )]
            except Exception as e:
                print(f"DOI lookup error: {e}", file=sys.stderr)
                return [types.TextContent(
                    type="text",
                    text="Failed to retrieve reference by DOI"
                )]
        else:
            # Use regular validation
            result = validate_reference(reference, style, format_type)
            
            output = {
                "formatted": result["formatted"],
                "doi": result["doi"]
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(output, indent=2)
            )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the MCP server"""
    print("Starting CrossRef MCP server...", file=sys.stderr)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="crossref-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
