# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BOE-MCP is an MCP (Model Context Protocol) server that provides LLMs access to the Spanish Official State Gazette (BOE) API. It enables querying consolidated legislation, BOE/BORME summaries, and legal reference data.

## Development Commands

```bash
# Install dependencies (uses uv package manager)
uv sync
uv sync --dev  # includes dev dependencies

# Run the MCP server locally
uv run boe_mcp

# Linting and formatting (ruff)
uv run ruff check src/
uv run ruff format src/

# Type checking
uv run mypy src/

# Run tests
uv run pytest
uv run pytest -v  # verbose
uv run pytest tests/test_file.py::test_name  # single test
```

## Architecture

The codebase is a single-module MCP server using FastMCP:

- `src/boe_mcp/server.py` - Main server implementation with all MCP tools
- `main.py` - Entry point that imports and runs the server

### MCP Tools Exposed

1. **search_laws_list** - Advanced search of consolidated legislation with filters (date range, jurisdiction, validity, text queries)
2. **get_law_section** - Retrieve specific parts of a consolidated law (metadata, full text, index, blocks)
3. **get_boe_summary** - Get BOE daily summary for a specific date (YYYYMMDD format)
4. **get_borme_summary** - Get BORME (business gazette) daily summary
5. **get_auxiliary_table** - Query reference tables (materias, ambitos, estados-consolidacion, departamentos, rangos, relaciones-anteriores, relaciones-posteriores)

### BOE API Integration

All tools communicate with `https://www.boe.es/datosabiertos/api/` endpoints. The server uses:
- `make_boe_request()` - JSON responses
- `make_boe_raw_request()` - XML/raw responses

## Key Technical Details

- Python 3.10+ required
- Uses `httpx` for async HTTP requests
- Uses `mcp[cli]>=1.8.1` with FastMCP for the MCP server implementation
- Transport: stdio (standard input/output)
- Line length: 100 characters (ruff config)
