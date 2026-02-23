# SunsetLog

Async Python client for [log-api.vmp.ir](https://log-api.vmp.ir): list channels and search logs. The library only returns data; you decide how to store or use it.

---

## Installation

**pip**

```bash
pip install SunsetLog
```

**uv**

```bash
uv add SunsetLog
```

- Python: **3.10+**
- Dependency: **httpx**

---

## Quick start

You need an API **token** (Bearer). Use the client as an async context manager and call `get_channels` or `search`.

```python
import asyncio
from SunsetLog import SunsetLogClient

TOKEN = "your-bearer-token"

async def main():
    async with SunsetLogClient(TOKEN) as client:
        # List channels for a gang (returns dict of channel_name -> {id, ts})
        channels = await client.get_channels(gang=1)
        print(list(channels.keys()))

        # Search logs (all channels if channels=None)
        data = await client.search(gang=1, from_offset=0)
        print(data["total"], len(data["hits"]))
        for hit in data["hits"]:
            print(hit.get("index"), hit.get("content"), hit.get("ts"))

asyncio.run(main())
```

---

## API overview

### `SunsetLogClient(token, *, base_url=..., timeout=30.0, headers=...)`

- **token** (str): Bearer token for the API.
- **base_url**: Default `"https://log-api.vmp.ir"`.
- **timeout**, **headers**: Optional.

Use as `async with SunsetLogClient(TOKEN) as client:` or call `await client.close()` when done.

### `get_channels(gang=1)`

- **Returns:** `dict[str, ChannelMeta]` — channel name → `{"id": str, "ts": int}`.

### `search(*, channels=None, gang=1, q="", from_offset=0, mode="exact", operator="and")`

- **channels:** `None` (all channels for the gang), a single channel name (str), or a list of channel names.
- **gang:** Gang id (default `1`).
- **q:** Search query string.
- **from_offset:** Pagination offset (API returns up to 100 hits per request).
- **Returns:** `{"total": int, "hits": list[LogHit]}`. Each hit has `id`, `index` (channel name), `content`, `ts`, `reactions`.

### `SunsetLogAPIError`

Raised on non-200 or invalid response. Has `.status_code` and `.body` when available.

---

## Pagination

The search API returns at most **100 hits** per request. To fetch all results, request pages by increasing `from_offset` until a page has fewer than 100 hits:

```python
async def fetch_all(client, gang=1):
    all_hits = []
    from_offset = 0
    while True:
        data = await client.search(gang=gang, from_offset=from_offset)
        hits = data.get("hits") or []
        all_hits.extend(hits)
        if len(hits) < 100:
            break
        from_offset += len(hits)
    return all_hits
```

---

## Saving results

The library does **not** write files. You get dicts; you save them (e.g. JSON):

```python
import json
from pathlib import Path

def save_to_file(data: dict, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# usage
data = await client.search(gang=1)
save_to_file(data, "my_logs.json")
```

---

## Exports

From `SunsetLog` you can import:

- `SunsetLogClient`
- `SunsetLogAPIError`
- `SearchResponse`, `ChannelsResponse`, `LogHit`, `ChannelMeta` (types)

---