###############################################################################
#
# Induce latency into the call to the upstream server of our application
#
# Start the server:
#
# $ export UPSTREAM_URL=http://localhost:34000
# $ fastapi dev app.py --port 9090
#
# Then run this AI agent tool as follows:
#
# $ export OPENAI_API_KEY=...
# $ python evaluate_latency_impact.py http://localhost:9090 https://jsonplaceholder.typicode.com 512
#
###############################################################################
import asyncio
import os
import shutil
from pathlib import Path
from tempfile import gettempdir

from fastmcp import Client
from fastmcp.utilities.logging import configure_logging


async def main(url: str, upstream: str, bandwidth: int, verbose: bool) -> None:
    fault_path = shutil.which("fault")
    if not fault_path:
        print("fault: command not found")
        return

    args = []
    if verbose:
        configure_logging("DEBUG")
        args = ["--log-file", str(Path(gettempdir()) / "fault.log"), "--log-level", "debug"]
    
    args.append("agent")
    args.append("tool")

    config = {
        "mcpServers": {
            "local": {
                "command": fault_path,
                "args": args,
                "env": {
                    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
                }
            },
        }
    }

    async with Client(config) as client:
        p = await client.call_tool(
            "fault_run_bandwidth_impact_scenario", {
                "url": url,
                "method": "GET",
                "body": "",
                "duration": "10s",
                "rate": bandwidth,
                "unit": "bps",
                "direction": "egress",
                "side": "server",
                "num_clients": 5,
                "rps": 2,
                "timeout": 10,
                "proxies": [
                    f"34000={upstream}:443"
                ]
            })

        print(p[0].text)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose",action='store_true')
    parser.add_argument("url")
    parser.add_argument("upstream")
    parser.add_argument("bandwidth", type=int)
    args = parser.parse_args()

    asyncio.run(main(args.url, args.upstream, args.bandwidth, args.verbose))
