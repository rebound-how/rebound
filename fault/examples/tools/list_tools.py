###############################################################################
#
# List fault available MCP tools
#
# $ python list_tools
#
#
###############################################################################
import asyncio
import os
import shutil
from pathlib import Path
from tempfile import gettempdir

from fastmcp import Client
from fastmcp.utilities.logging import configure_logging


async def main(verbose: bool) -> None:
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
        tools = await client.list_tools()

        for tool in tools:
            print(tool.model_dump_json(indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose",action='store_true')
    args = parser.parse_args()

    asyncio.run(main(args.verbose))
