import asyncio
import os
import shutil
from pathlib import Path
from tempfile import gettempdir

from fastmcp import Client
from fastmcp.utilities.logging import configure_logging


async def main(source_dir: str, verbose: bool) -> None:
    fault_path = shutil.which("fault")
    if not fault_path:
        print("fault: command not found")
        return

    args = []
    if verbose:
        configure_logging("DEBUG")
        args = ["--log-file", str(Path(gettempdir()) / "fault.log"), "--log-level", "debug"]
    
    args.append("agent")
    args.append("--llm-client")
    args.append("open-router")
    args.append("--llm-prompt-reasoning-model")
    args.append("google/gemma-3-27b-it")
    args.append("--llm-prompt-chat-model")
    args.append("google/gemma-3-27b-it")
    args.append("--llm-embed-model")
    args.append("mxbai-embed-large")
    args.append("--llm-embed-model-dim")
    args.append("384")
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
            "fault_index_source_code", {
                "source_dir": source_dir,
                "lang": "python"
            })
        
        print(p)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose",action='store_true')
    parser.add_argument("source_dir")
    args = parser.parse_args()

    asyncio.run(main(args.source_dir, args.verbose))