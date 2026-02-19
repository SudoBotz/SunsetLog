from typing import Any, TypedDict


class ChannelMeta(TypedDict):
    """Latest message meta per channel."""

    id: str
    ts: int


class LogHit(TypedDict, total=False):
    """Single log entry from search."""

    id: str
    index: str
    content: str
    ts: int
    reactions: list[dict[str, Any]]


class SearchResponse(TypedDict):
    """Search API response."""

    hits: list[LogHit]
    total: int


ChannelsResponse = dict[str, ChannelMeta]
