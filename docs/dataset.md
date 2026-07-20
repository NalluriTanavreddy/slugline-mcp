# Reference dataset: rohitsaxena/MovieSum

slugline-mcp's reference index is built from
[rohitsaxena/MovieSum](https://huggingface.co/datasets/rohitsaxena/MovieSum),
a public Hugging Face dataset of ~2,200 movie screenplays. Each row has:

| field         | description                                                              |
|---------------|---------------------------------------------------------------------------|
| `movie_name`  | e.g. `"8MM_1999"`                                                          |
| `imdb_id`     | e.g. `"tt0134273"`                                                         |
| `script`      | the full screenplay as XML, pre-structured into `<scene>` elements       |
| `summary`     | a Wikipedia plot summary (not currently used by slugline-mcp)             |

The `script` XML looks like:

```xml
<script>
  <scene>
    <stage_direction>INT. OFFICE -- DAY</stage_direction>
    <scene_description>An old money office ...</scene_description>
    <character>WELLES</character>
    <dialogue>Your son-in-law dealt with ...</dialogue>
    <parenthetical>clears his throat</parenthetical>
    <dialogue>The specifics are in the report ...</dialogue>
  </scene>
  ...
</script>
```

`src/slugline_mcp/indexing/parser.py` parses this into `Scene` objects.

## Downloading it

No Hugging Face account or token is required -- the dataset is public. The
`datasets` library downloads and caches it automatically the first time it's
loaded:

```python
from datasets import load_dataset

dataset = load_dataset("rohitsaxena/MovieSum")
# DatasetDict with "train", "validation", "test" splits, ~2,200 rows total
```

The download is cached under `~/.cache/huggingface/datasets` (or
`$HF_HOME` if set), so it's only fetched once. Unauthenticated requests are
rate-limited by Hugging Face; if you hit rate limits, set the `HF_TOKEN`
environment variable to a (free) Hugging Face access token.

## Building the index

Building the full reference index requires the optional `index` dependency
group (`datasets`), which is **not** installed by default -- end users of the
published MCP server never need it, only whoever builds/refreshes the
prebuilt index does:

```bash
uv sync --extra index
uv run python -m slugline_mcp.indexing.build_index
```

This parses every script, embeds every scene with
`sentence-transformers/all-MiniLM-L6-v2`, and writes the result into a local
Chroma database (default: `~/.slugline-mcp/chroma`). Indexing the full
dataset (~2,200 movies, several hundred scenes each) takes a while on CPU;
use `--limit N` to index only the first N movies while developing:

```bash
uv run python -m slugline_mcp.indexing.build_index --limit 20
```
