"""Standalone example: fetch the channel list via /user/getChannels."""

import asyncio
import os

from SunsetLog import SunsetLogAPIError, SunsetLogClient


async def main() -> None:
    token = os.environ["SUNSETLOG_TOKEN"]

    async with SunsetLogClient(token) as client:
        try:
            result = await client.get_channel_list(gang=1, job=1)
        except SunsetLogAPIError as e:
            print(f"Error: {e} (status={e.status_code})")
            return

        for channel in result["channels"]:
            print(f"{channel['id']:>6}  {channel['index']:<30} {channel['label']}")


if __name__ == "__main__":
    asyncio.run(main())
