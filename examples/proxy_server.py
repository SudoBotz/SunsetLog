"""
Reverse proxy for log-api.vmp.ir, meant to run ON A SERVER INSIDE IRAN
that already has direct access to the real API. Uses SunsetLogClient
(this library) internally instead of calling the API directly.

An external server (outside Iran, where log-api.vmp.ir is blocked) can then
point SunsetLogClient's base_url at THIS proxy instead of the real API.
No separate proxy key: the caller's own site token (the same one used
against the real API) is forwarded upstream as-is.

Run directly (host/port configurable via env vars, no uvicorn CLI needed):
    pip install fastapi uvicorn
    export PROXY_HOST=0.0.0.0        # your Iran server's bind address
    export PROXY_PORT=8000
    python proxy_server.py

In /docs, click the "Authorize" lock button at the top and paste just the
site token (no "Bearer " prefix needed there) — Swagger adds it for you.
"""

import os
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

UPSTREAM_BASE_URL = "https://log-api.vmp.ir"

app = FastAPI()
bearer_scheme = HTTPBearer()


async def _forward(path: str, params: dict, token: str) -> dict:
    async with httpx.AsyncClient(base_url=UPSTREAM_BASE_URL, timeout=30.0) as client:
        r = await client.get(
            path, params=params, headers={"Authorization": f"Bearer {token}"}
        )
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()


@app.get("/user/getChannels")
async def get_channels(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    gang: int = 1,
    job: int = 1,
):
    return await _forward(
        "/user/getChannels", {"gang": gang, "job": job}, creds.credentials
    )


@app.get("/search")
async def search(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    q: str = "",
    from_offset: int = Query(0, alias="from"),
    mode: str = "exact",
    operator: str = "and",
    channels: str = "",
    gang: int = 1,
):
    return await _forward(
        "/search",
        {
            "q": q,
            "from": from_offset,
            "mode": mode,
            "operator": operator,
            "channels": channels,
            "gang": gang,
        },
        creds.credentials,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.environ.get("PROXY_HOST", "0.0.0.0"),
        port=int(os.environ.get("PROXY_PORT", "8000")),
    )