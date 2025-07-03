import asyncio
import json
import os
import shutil
from pathlib import Path
from tempfile import gettempdir

from fastmcp import Client
from fastmcp.utilities.logging import configure_logging
from rich.console import Console

console = Console()


async def main(llm: str, verbose: bool) -> None:
    fault_path = shutil.which("fault")
    if not fault_path:
        print("fault: command not found")
        return

    env = {}

    args = []
    if verbose:
        configure_logging("DEBUG")
        args = ["--log-file", str(Path(gettempdir()) / "fault.log"), "--log-level", "debug"]
    
    args.append("agent")

    if llm == "openai":
        env["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    elif llm == "gemini":
        args.append("--llm-client")
        args.append("gemini")
        args.append("--llm-prompt-reasoning-model")
        args.append("gemini-2.5-flash")
        #args.append("--llm-embed-model")
        #args.append("gemini-embedding-exp-03-07")
        args.append("--llm-embed-model-dim")
        args.append("384")
        env["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
    elif llm == "openrouter":
        args.append("--llm-client")
        args.append("open-router")
        args.append("--llm-prompt-reasoning-model")
        args.append("google/gemma-3-27b-it")
        args.append("--llm-embed-model-dim")
        args.append("384")
        env["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
    elif llm == "ollama":
        args.append("--llm-client")
        args.append("ollama")
        args.append("--llm-prompt-reasoning-model")
        args.append("gemma3:4b")
        args.append("--llm-embed-model")
        args.append("mxbai-embed-large")
        args.append("--llm-embed-model-dim")
        args.append("1024")

    args.append("tool")

    config = {
        "mcpServers": {
            "local": {
                "command": fault_path,
                "args": args,
                "env": env
            },
        }
    }

    async with Client(config) as client:
        await client.call_tool(
            "fault_index_source_code", {
                "source_dir": str(Path.cwd() / "app"),
                "lang": "python"
            })

        p = await client.call_tool(
            "fault_make_reliability_and_perf_changes", {
                "file": str(Path.cwd() / "app" / "app.py"),
            })

        r = json.loads(p[0].text)

        console.print(f"[purple]Score[/] {r['score']}")
        console.print(f"[purple]Explanation[/] {r['explanation']}")
        console.print(f"[purple]Dependencies[/] {r['dependencies']}")
        console.print(f"[purple]Proposed changes[/]\n{r['diff']}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", choices=["openai", "openrouter", "ollama", "gemini"], default="openai")
    parser.add_argument("--verbose",action='store_true')
    args = parser.parse_args()

    asyncio.run(main(args.llm, args.verbose))
