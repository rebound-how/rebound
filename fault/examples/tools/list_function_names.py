import asyncio
import shutil

from fastmcp import Client
from fastmcp.utilities.logging import configure_logging


async def main(code_file: str, verbose: bool) -> None:
    fault_path = shutil.which("fault")
    if not fault_path:
        print("fault: command not found")
        return

    args = []
    if verbose:
        configure_logging("DEBUG")
        args = ["--log-stdout", "--log-level", "debug"]
    
    args.append("agent")
    args.append("tool")

    config = {
        "mcpServers": {
            "local": {
                "command": fault_path,
                "args": args,
            },
        }
    }

    async with Client(config) as client:
        p = await client.call_tool(
            "extract.function_names", {
                "file": code_file,
            })
        
        print(p)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose",action='store_true')
    parser.add_argument("code_file")
    args = parser.parse_args()

    asyncio.run(main(args.code_file, args.verbose))