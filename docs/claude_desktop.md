# Connecting slugline-mcp to Claude Desktop

Add slugline-mcp as a local MCP server by editing Claude Desktop's config
file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

## While developing (from a local checkout)

```json
{
  "mcpServers": {
    "slugline-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/slugline-mcp", "python", "-m", "slugline_mcp"]
    }
  }
}
```

Replace `/absolute/path/to/slugline-mcp` with the path to your local
checkout of this repo.

## Once published to PyPI

Once slugline-mcp has a `slugline-mcp` console entry point and is published
(see the packaging and publish phases in `TASKS.md`), the config simplifies
to:

```json
{
  "mcpServers": {
    "slugline-mcp": {
      "command": "uvx",
      "args": ["slugline-mcp"]
    }
  }
}
```

`uvx` downloads and runs the published package on demand -- no local clone
or manual dependency install needed.

## After adding the config

Restart Claude Desktop, then ask something like *"Find me real scenes
similar to this one: [paste a scene]"* -- if Claude calls
`search_similar_scenes` and grounds its answer in retrieved reference
scenes, slugline-mcp is connected correctly.

If Claude can't find the `uv`/`uvx` command, use its absolute path instead
(the output of `which uv` / `which uvx`).
