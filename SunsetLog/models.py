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


class ChannelInfo(TypedDict):
    """Single channel entry from /user/getChannels."""

    id: int
    index: str
    label: str
    type: int


class ChannelListResponse(TypedDict):
    """Response of /user/getChannels."""

    channels: list[ChannelInfo]
    categories: list[Any]
    admin: bool
    canViewAllGangs: bool
    canViewAllJobs: bool
