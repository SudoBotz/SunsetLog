from typing import Any

import httpx

from SunsetLog.models import ChannelListResponse, ChannelsResponse, SearchResponse


class SunsetLogAPIError(Exception):
    """Raised when the API returns an error or unexpected response."""

    def __init__(
        self, message: str, status_code: int | None = None, body: str | None = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class SunsetLogClient:
    """
    Async client for log-api.vmp.ir.
    Use as async context manager or call close() when done.
    """

    def __init__(
        self,
        token: str,
        *,
        base_url: str = "https://log-api.vmp.ir",
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
    ):
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._timeout = timeout
        self._headers = {
            "Accept": "*/*",
            "Authorization": f"Bearer {token}",
            "User-Agent": "SunsetLog/1.0 (httpx)",
            **(headers or {}),
        }
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=self._headers,
                timeout=self._timeout,
            )
        return self._client

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "SunsetLogClient":
        self._get_client()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def get_channels(self, gang: int = 1) -> ChannelsResponse:
        """
        Fetch latest message id/ts per channel for a gang.
        GET /channels/latest?gang={gang}
        """
        client = self._get_client()
        r = await client.get("/channels/latest", params={"gang": gang})
        if r.status_code != 200:
            raise SunsetLogAPIError(
                f"channels/latest failed: {r.status_code}",
                status_code=r.status_code,
                body=r.text,
            )
        data = r.json()
        if not isinstance(data, dict):
            raise SunsetLogAPIError("channels/latest returned non-object", body=r.text)
        return data

    async def get_channel_list(
        self, gang: int = 1, job: int = 1
    ) -> ChannelListResponse:
        """
        Fetch the available channels for a gang/job.
        GET /user/getChannels?gang={gang}&job={job}
        """
        client = self._get_client()
        r = await client.get("/user/getChannels", params={"gang": gang, "job": job})
        if r.status_code != 200:
            raise SunsetLogAPIError(
                f"user/getChannels failed: {r.status_code}",
                status_code=r.status_code,
                body=r.text,
            )
        data = r.json()
        if not isinstance(data, dict) or "channels" not in data:
            raise SunsetLogAPIError(
                "user/getChannels returned invalid shape", body=r.text
            )
        return data

    async def search(
        self,
        *,
        channels: str | list[str] | None = None,
        gang: int = 1,
        q: str = "",
        from_offset: int = 0,
        mode: str = "exact",
        operator: str = "and",
    ) -> SearchResponse:
        """
        Search logs. GET /search.
        channels: single channel name or comma-separated list.
        """
        if channels is None:
            channel_list = await self.get_channel_list(gang=gang)
            indexes = [c["index"] for c in channel_list.get("channels", [])]
            channels = ",".join(indexes) if indexes else "gang_glitch_locker1"
        elif isinstance(channels, list):
            channels = ",".join(channels)

        client = self._get_client()
        params: dict[str, Any] = {
            "q": q,
            "from": from_offset,
            "mode": mode,
            "operator": operator,
            "channels": channels,
            "gang": gang,
        }
        r = await client.get("/search", params=params)
        if r.status_code != 200:
            raise SunsetLogAPIError(
                f"search failed: {r.status_code}",
                status_code=r.status_code,
                body=r.text,
            )
        data = r.json()
        if not isinstance(data, dict) or "hits" not in data:
            raise SunsetLogAPIError("search returned invalid shape", body=r.text)
        return data
