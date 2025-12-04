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

#### Core Tools (v1.0)
1. **search_laws_list** - Advanced search of consolidated legislation with filters (date range, jurisdiction, validity, text queries)
2. **get_law_section** - Retrieve specific parts of a consolidated law (metadata, full text, index, blocks)
3. **get_boe_summary** - Get BOE daily summary for a specific date (YYYYMMDD format)
4. **get_borme_summary** - Get BORME (business gazette) daily summary
5. **get_auxiliary_table** - Query reference tables (materias, ambitos, estados-consolidacion, departamentos, rangos, relaciones-anteriores, relaciones-posteriores)

#### Smart Navigation Tools (v1.5 - feature/smart-navigation-v2)
6. **get_law_structure** - Get hierarchical structure of a law (titles, chapters, articles)
7. **get_article_info** - Get specific article content from a law
8. **search_within_law** - Search text within a specific law
9. **get_law_metadata_summary** - Get concise metadata of a law
10. **get_boe_summary_metadata** - Get BOE summary metadata (sections, document counts)
11. **get_boe_summary_section** - Get documents from a specific BOE section with pagination
12. **get_boe_document_info** - Get metadata of a specific document from BOE summary

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

## Documentation Index

### Development & Planning
| Document | Description |
|----------|-------------|
| [docs/BOE_MCP_DEVELOPMENT_FRAMEWORK.md](docs/BOE_MCP_DEVELOPMENT_FRAMEWORK.md) | RPVEA development methodology |
| [docs/RPVEA-2.0-BOE-MCP.md](docs/RPVEA-2.0-BOE-MCP.md) | RPVEA 2.0 framework reference |

### Feature Documentation
| Document | Description |
|----------|-------------|
| [docs/PLAN-RPVEA-2.0-smart-navigation-v2.md](docs/PLAN-RPVEA-2.0-smart-navigation-v2.md) | Smart Navigation v2 implementation plan |
| [docs/PLAN-SMART-SUMMARY.md](docs/PLAN-SMART-SUMMARY.md) | Smart Summary tools implementation |
| [docs/CASOS-USO-SMART-NAV-V2.md](docs/CASOS-USO-SMART-NAV-V2.md) | Use cases for Smart Navigation |

### Architecture & Production
| Document | Description |
|----------|-------------|
| [docs/ARQUITECTURA-PRODUCCION-BOE.md](docs/ARQUITECTURA-PRODUCCION-BOE.md) | **Production architecture proposal, token limits research** |
| [docs/LIMITACIONES-CONOCIDAS.md](docs/LIMITACIONES-CONOCIDAS.md) | Known limitations and workarounds |

### User Guides
| Document | Description |
|----------|-------------|
| [docs/GUIA-USO-HERRAMIENTAS.md](docs/GUIA-USO-HERRAMIENTAS.md) | Tool usage guide (Spanish) |
| [docs/INVESTIGACION-MCP-GUIAS-USO.md](docs/INVESTIGACION-MCP-GUIAS-USO.md) | MCP guide integration research |

## Pending Tasks / Roadmap

### v1.5.x (Current - feature/smart-navigation-v2)
- [x] Smart Navigation tools (get_law_structure, get_article_info, etc.)
- [x] Smart Summary tools (get_boe_summary_metadata, etc.)
- [ ] BORME Smart Summary equivalents
- [ ] Reduce default limits (20→10, 100→20)
- [ ] MCP instructions/resources integration for usage guides

### v2.x (Future - Production Architecture)
- [ ] Local database design (Neo4j for relations, Elasticsearch for FTS)
- [ ] BOE Downloader component
- [ ] ETL pipeline
- [ ] MCP Orchestrator
- [ ] Chat client with auth

See [docs/ARQUITECTURA-PRODUCCION-BOE.md](docs/ARQUITECTURA-PRODUCCION-BOE.md) for details.

## Local Testing Setup

For testing with Claude Desktop before publishing:

```bash
# Create local installation
mkdir -p /Users/pepo/mcp-servers/boe-mcp-smart-v1.5.0
cd /Users/pepo/mcp-servers/boe-mcp-smart-v1.5.0
git clone <repo> .
git checkout feature/smart-navigation-v2
uv venv && uv sync
```

Claude Desktop config (`claude_desktop_config.json`):
```json
"boe-mcp-smart-v1.5.0": {
  "command": "/Users/pepo/mcp-servers/boe-mcp-smart-v1.5.0/.venv/bin/python",
  "args": ["-m", "boe_mcp.server"],
  "env": {
    "PYTHONPATH": "/Users/pepo/mcp-servers/boe-mcp-smart-v1.5.0/src"
  }
}
```
