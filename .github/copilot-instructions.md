<!-- .github/copilot-instructions.md - targeted instructions for AI coding agents -->
# Project-specific Copilot instructions

Purpose: help an AI coding assistant be immediately productive in this repository.

Big picture
- **Math MCP example (tool server + client):** see `math/math_server.py` (FastMCP server exposing tools/prompts) and `math/math_clinet.py` (MultiServerMCPClient + LangChain agent). The server registers tools with `@mcp.tool()` and prompts with `@mcp.prompt()`; the client discovers tools and uses `create_react_agent`.
- **Comparables API scaffold:** `comparables_API_deployment_setup.py` contains the project's `requirements.txt`, Docker and `README.md` content. Main API uses FastAPI + Uvicorn (examples in that file).
- **Ray demo job:** `job.py` shows Ray usage with `ray.init(...)`, remote tasks, and `RAY_DEBUG` set for debugging (breakpoints inside remote tasks are present).

How to run & debug (concrete commands)
- Create virtualenv and install deps (Windows `cmd.exe`):
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
- Run the Math MCP server (two options shown in `math/README.md`):
```
# from math/ dir
uvicorn math_server:app --port 3000
# or from repo root
uvicorn iceberg_mcp.math.math_server:app --port 3000
```
- Run client (after setting `OPENAI_API_KEY`):
```
# set OpenAI key (Windows cmd)
set OPENAI_API_KEY=sk-...your-key...
python math\math_clinet.py
```
- Run the MCP server in stdio mode (math server internal option): python entrypoint runs `mcp.run(transport="stdio")` — used when the client launches server as a subprocess.
- Run tests: `pytest` (dev deps listed in `comparables_API_deployment_setup.py`).

Key conventions & patterns to preserve
- Tools/prompts: functions decorated with `@mcp.tool()` and `@mcp.prompt()` are the canonical extension points. Keep parameter type hints (Annotated) and simple return types for discoverability.
- Transports: the repo uses **SSE** and **stdio** transports. `math_clinet.py` shows both: SSE via URL `http://localhost:3000/sse`, or stdio when launching server process from the client.
- Logging / stdout: MCP servers print/register via logger and sometimes write to stderr for subprocess diagnostics — prefer using `logging` and keep stderr messages for startup diagnostics (used by clients to detect readiness).
- LLM model usage: client code uses `create_react_agent` or `ChatOpenAI`. Expect model identifiers like `gpt-4.1` or `gpt-3.5-turbo` depending on the example.

Integration points / external deps
- OpenAI API: `OPENAI_API_KEY` environment variable is required for LLM-based clients.
- MCP / FastMCP: implemented via `mcp.server.fastmcp.FastMCP` (see `math/math_server.py`).
- Ray: optional demo in `job.py`. To debug Ray tasks enable `RAY_DEBUG=1`.
- Docker / Deploy: `comparables_API_deployment_setup.py` contains sample `Dockerfile` + `docker-compose` snippets for deploying a FastAPI app on port 8000.

Editing guidance for assistants
- When adding tools: register using `@mcp.tool()` with clear type annotations, add a small async `await asyncio.sleep(0)` if you need to keep signatures async-compatible.
- When changing client-server contracts: update both `math_server.py` and `math_clinet.py` together — the client discovers tools at runtime; breaking changes require client adaptation.
- For small fixes, preserve existing logging calls and error shapes (HTTPException on server errors) so tests and callers behave predictably.

Files to inspect first (high signal)
- `math/math_server.py` — server behavior, `mcp.run(transport="stdio")` and uvicorn usage.
- `math/math_clinet.py` — client patterns (MultiServerMCPClient, create_react_agent).
- `job.py` — Ray task / debugging example.
- `comparables_API_deployment_setup.py` — dependency list, Docker/README snippets, and quickstart commands.
- `requirements.txt` — pinned packages to install.

If anything is unclear or you want more automation (CI, test commands, or a small helper script to start the math server + client), tell me which area to expand and I will update this doc.
