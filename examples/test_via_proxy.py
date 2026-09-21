"""
Run this on the EXTERNAL server (outside Iran) to test that the Iran-side
proxy (see proxy_server.py) is reachable and working.

export PROXY_BASE_URL=http://your-iran-server-ip:8000
export PROXY_ACCESS_KEY=same_secret_set_on_the_proxy
python test_via_proxy.py
"""

import asyncio
import os

from SunsetLog import SunsetLogAPIError, SunsetLogClient


async def main() -> None:
    base_url = os.environ["PROXY_BASE_URL"]
    access_key = os.environ["PROXY_ACCESS_KEY"]

    async with SunsetLogClient(access_key, base_url=base_url) as client:
        try:
            channels = await client.get_channel_list(gang=1, job=1)
            print(f"OK - got {len(channels['channels'])} channels")
            for c in channels["channels"][:5]:
                print(f"  {c['id']:>6}  {c['index']}")
        except SunsetLogAPIError as e:
            print(f"FAILED: {e} (status={e.status_code}, body={e.body})")


if __name__ == "__main__":
    asyncio.run(main())
