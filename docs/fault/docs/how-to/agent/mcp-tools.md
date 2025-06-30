# Explore <span class="f">fault</span> MCP Agent Tools

This guide will take you through the
[MCP tools](https://modelcontextprotocol.io/introduction) supported by
<span class="f">fault</span> agent.


!!! abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span>

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../install.md).

    -   [X] Get an OpenAI Key

        For the purpose of the guide, we will be using OpenAI models. You
        need to create an API key. Then make sure the key is available for
        <span class="f">fault</span>:

        ```bash
        export OPENAI_API_KEY=sk-...
        ```

        The agent works fine with [Gemini](https://ai.google.dev/),
        [ollama](./llm-configuration.md#ollama) and
        [OpenRouter](./llm-configuration.md#openrouter) so you may switch to
        either. You want to have a look at an [example below](#tool-full-file-code-changes-recommendations).

    -   [X] Install a local qdrant database

        <span class="f">fault</span> uses [qdrant](https://qdrant.tech/) for its vector database. You
        can install a [local](https://qdrant.tech/documentation/quickstart/),
        free, qdrant using docker:

        ```bash
        docker run -p 6333:6333 -p 6334:6334 -v "$(pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant
        ```

        While not used by every tools, we suggest you start one up to explore
        all of them.
    
    -   [X] Install the Python FastMCP library

        <span class="f">fault</span> does not need this library to work but
        to demonstrate the tools we support, we will be using
        [FastMCP](https://github.com/jlowin/fastmcp).

!!! example "fault with Cursor"

    Below is an example of using <span class="f">fault</span> AI tools in
    [Cursor](https://www.cursor.com/) to help it make the generated code more
    production ready.

    <div style="text-align: center;">
    <iframe width="100%" height="800" src="https://www.youtube.com/embed/DFw1vsCySYU?si=SA0uG47Qx1vHE_sh" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>

## Overview

The <span class="f">fault</span> AI agent is called as follows:

```bash
fault agent tool
```

It supports the [MCP](https://modelcontextprotocol.io/) specification.

!!! example "Get a demo application"

    For the purpose of demonstration, we suggest you run the following server
    with a single endpoint:

    ```python title="app/app.py"
    import os

    import httpx
    from fastapi import FastAPI

    UPSTREAM_URL = os.getenv("UPSTREAM_URL", "https://jsonplaceholder.typicode.com")

    app = FastAPI()


    @app.get("/")
    def index():
        return httpx.get(f"{UPSTREAM_URL}/todos/1", headers={
            "Host": "jsonplaceholder.typicode.com"
        }).json()
    ```

    Install dependencies as follows:


    === "pip"

        ```bash
        pip install fastapi[standard] httpx
        ```

    === "uv"

        ```bash
        uv tool install fastapi[standard] httpx
        ```

    Then run it as follows:

    ```bash
    export UPSTREAM_URL=http://localhost:34000  # (1)!
    fastapi dev app/app.py --port 9090
    ```

    1. This will ensure the remote call made from the endpoint goes through `fault`. 

        !!! example

            For instance, you try without the agent first:

            ```bash
            fault run --with-latency --latency-mean 300 --proxy "34000=https://jsonplaceholder.typicode.com"
            ```

            If you now connect to the endpoint, it will go through `fault` and
            apply the latency on the remote call.


## Tool: Source Code Indexing

In order to get the best feedback from <span class="f">fault</span> AI agent,
it is a good to index locally your source code so it. When performing certain
operations, <span class="f">fault</span> will search it for the right
documents to contextualize the query it performs.

-   [X] Index your source code

    **Tool** `#!python "fault_index_source_code"`

    **Payload**
    ```json
    {
        "source_dir": "",
        "lang": "python"
    }
    ```

    The `source_dir` argument is an absolute path to the top-level directory
    containing code files. The `lang` argument hints which files to process.

    **Returns**

    The string `"done"` when complete. Any MCP error with a hint of what
    went wrong otherwise.

    **Requirements**

    - A qdrant URL
    - The LLM of your choice, in this example we use OpenAI so you need to
      set the `OPENAI_API_KEY` environment variable

    Here is a full working example to calling this tool:

    ```python hl_lines="37-42"
    import asyncio
    import os
    import shutil
    from pathlib import Path
    from tempfile import gettempdir

    from fastmcp import Client
    from fastmcp.utilities.logging import configure_logging

    async def main(source_dir: str, verbose: bool) -> None:
        fault_path = shutil.which("fault") # (1)!
        if not fault_path:
            print("fault: command not found")
            return

        args = []
        if verbose:
            configure_logging("DEBUG")
            args = ["--log-file", str(Path(gettempdir()) / "fault.log"), "--log-level", "debug"]
        
        args.append("agent")
        args.append("tool")

        config = {  # (2)!
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

        async with Client(config) as client:   # (3)!
            p = await client.call_tool(   # (4)!
                "fault_index_source_code", {
                    "source_dir": source_dir,   # (5)!
                    "lang": "python"   # (6)!
                })
            
            print(p)

    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--verbose",action='store_true')
        parser.add_argument("source_dir")
        args = parser.parse_args()

        asyncio.run(main(args.source_dir, args.verbose))
    ```

    1. Locate the `fault` binary
    2. Prepare a stdio configuration to call the tool
    3. Setup a client that handles agent initialization
    4. Call the `source.index` tool from <span class="f">fault</span>
    5. Pass the absolute directory to the source code
    6. Hint of the language to index: `python`, `go`, `rust`, `javascript`...

!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```


## Tool: List function names from a file

Context is everything! Being able to focus on a given function helps making
the right decisions.

-   [X] List function names

    **Tool** `#!python "fault_list_function_names"`

    **Payload**
    ```json
    {
        "file": "",
    }
    ```

    The `file` argument is an absolute path a source code file.

    **Returns**

    An array with any found function names.

    **Requirements**

    none

    Here is a full working example to calling this tool:

    ```python hl_lines="34-37"
    import asyncio
    import os
    import shutil
    from pathlib import Path
    from tempfile import gettempdir

    from fastmcp import Client
    from fastmcp.utilities.logging import configure_logging

    async def main(code_file: str, verbose: bool) -> None:
        fault_path = shutil.which("fault") # (1)!
        if not fault_path:
            print("fault: command not found")
            return

        args = []
        if verbose:
            configure_logging("DEBUG")
            args = ["--log-file", str(Path(gettempdir()) / "fault.log"), "--log-level", "debug"]
        
        args.append("agent")
        args.append("tool")

        config = {  # (2)!
            "mcpServers": {
                "local": {
                    "command": fault_path,
                    "args": args,
                },
            }
        }

        async with Client(config) as client:   # (3)!
            p = await client.call_tool(   # (4)!
                "fault_list_function_names", {
                    "file": code_file,   # (5)!
                })
            
            print(p)

    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--verbose",action='store_true')
        parser.add_argument("source_dir")
        args = parser.parse_args()

        asyncio.run(main(args.source_dir, args.verbose))
    ```

    1. Locate the `fault` binary
    2. Prepare a stdio configuration to call the tool
    3. Setup a client that handles agent initialization
    4. Call the `source.index` tool from <span class="f">fault</span>
    5. Pass the absolute file to the source code


!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```

## Tool: Extract function block

Extract the whole function block including its signatures and, for some
languages, any decorators around the function.

-   [X] Extract function block

    **Tool** `#!python "fault_extract_code_block"`

    **Payload**
    ```json
    {
        "file": "",
        "func": ""
    }
    ```

    The `file` argument is an absolute path a source code file. The `func`
    argument is the name of the function within that module.

    **Returns**

    A JSON payload with two keys:

    * `full`: the complete function block including its signature
    * `body`: the function body without its signature

    **Requirements**

    none

    Here is a full working example to calling this tool:

    ```python hl_lines="34-38"
    import asyncio
    import os
    import shutil
    from pathlib import Path
    from tempfile import gettempdir

    from fastmcp import Client
    from fastmcp.utilities.logging import configure_logging

    async def main(code_file: str, func_name: str, verbose: bool) -> None:
        fault_path = shutil.which("fault") # (1)!
        if not fault_path:
            print("fault: command not found")
            return

        args = []
        if verbose:
            configure_logging("DEBUG")
            args = ["--log-file", str(Path(gettempdir()) / "fault.log"), "--log-level", "debug"]
        
        args.append("agent")
        args.append("tool")

        config = {  # (2)!
            "mcpServers": {
                "local": {
                    "command": fault_path,
                    "args": args,
                },
            }
        }

        async with Client(config) as client:   # (3)!
            p = await client.call_tool(   # (4)!
                "fault_extract_code_block", {
                    "file": code_file,   # (5)!
                    "func": func_name   # (6)!
                })
            
            print(p)

    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--verbose",action='store_true')
        parser.add_argument("source_dir")
        parser.add_argument("func_name")
        args = parser.parse_args()

        asyncio.run(main(args.source_dir, args.verbose))
    ```

    1. Locate the `fault` binary
    2. Prepare a stdio configuration to call the tool
    3. Setup a client that handles agent initialization
    4. Call the `source.index` tool from <span class="f">fault</span>
    5. Pass the absolute file to the source code
    6. The name of the function

!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```

## Tool: Function Performance Scoring

Scoring the performance of a function will help you understand how much
attention requires this function.

-   [X] Evaluate function performance

    **Tool** `#!python "fault_score_performance"`

    **Payload**
    ```json
    {
        "snippet": "",
        "lang": ""
    }
    ```

    The `snippet` argument is the full code of a function or any code snippet.
    The `lang` hints the language of the snippet.

    **Returns**

    A JSON payload with two keys:

    * `explanation`: a short description of the reasonning for the score
    * `score`: the score as a number between `0.0` and `1.0`

    **Requirements**

    - A qdrant URL
    - The LLM of your choice, in this example we use OpenAI so you need to
      set the `OPENAI_API_KEY` environment variable

    Here is a full working example to calling this tool:

    ```python hl_lines="39-51"
    import asyncio
    import json
    import os
    import shutil
    from pathlib import Path
    from tempfile import gettempdir

    from fastmcp import Client
    from fastmcp.utilities.logging import configure_logging


    async def main(code_file: str, func_name: str, lang: str, verbose: bool) -> None:
        fault_path = shutil.which("fault")   # (1)!
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
            p = await client.call_tool(   # (2)!
                "fault_extract_code_block", {
                    "file": code_file,
                    "func": func_name
                })
            
            snippet = json.loads(p[0].text)["full"]   # (3)!

            p = await client.call_tool(
                "fault_score_performance", {
                    "snippet": snippet,
                    "lang": lang
                })
            
            print(p)


    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--verbose",action='store_true')
        parser.add_argument("code_file")
        parser.add_argument("func_name")
        parser.add_argument("lang")
        args = parser.parse_args()

        asyncio.run(main(args.code_file, args.func_name, args.lang, args.verbose))
    ```

    1. Locate the `fault` binary
    2. Extract the function block
    3. Take the snippet from the tool's response

!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```

## Tool: Function Reliability Scoring

Scoring the reliability of a function will help you understand how much
attention requires this function.

-   [X] Evaluate function reliability

    **Tool** `#!python "fault_score_reliability"`

    **Payload**
    ```json
    {
        "snippet": "",
        "lang": ""
    }
    ```

    The `snippet` argument is the full code of a function or any code snippet.
    The `lang` hints the language of the snippet.

    **Returns**

    A JSON payload with two keys:

    * `explanation`: a short description of the reasonning for the score
    * `score`: the score as a number between `0.0` and `1.0`

    **Requirements**

    - A qdrant URL
    - The LLM of your choice, in this example we use OpenAI so you need to
      set the `OPENAI_API_KEY` environment variable

    Here is a full working example to calling this tool:

    ```python hl_lines="39-51"
    import asyncio
    import json
    import os
    import shutil
    from pathlib import Path
    from tempfile import gettempdir

    from fastmcp import Client
    from fastmcp.utilities.logging import configure_logging


    async def main(code_file: str, func_name: str, lang: str, verbose: bool) -> None:
        fault_path = shutil.which("fault")   # (1)!
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
            p = await client.call_tool(   # (2)!
                "fault_extract_code_block", {
                    "file": code_file,
                    "func": func_name
                })
            
            snippet = json.loads(p[0].text)["full"]   # (3)!

            p = await client.call_tool(
                "fault_score_reliability", {
                    "snippet": snippet,
                    "lang": lang
                })
            
            print(p)


    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--verbose",action='store_true')
        parser.add_argument("code_file")
        parser.add_argument("func_name")
        parser.add_argument("lang")
        args = parser.parse_args()

        asyncio.run(main(args.code_file, args.func_name, args.lang, args.verbose))
    ```

    1. Locate the `fault` binary
    2. Extract the function block
    3. Take the snippet from the tool's response

!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```

## Tool: Function performance improvements suggestions

Scoring the performance of a **single function** will help you understand how
much attention it requires.

-   [X] Evaluate function reliability

    **Tool** `#!python "fault_suggest_better_function_performance"`

    **Payload**
    ```json
    {
        "snippet": "",
        "lang": "",
        "score": 0.3,
        "target_score": 0.8
    }
    ```

    The `snippet` argument is the full code of a function or any code snippet.
    The `lang` hints the language of the snippet. The `score` is the current
    scoring of the snippet. This can be extracted using the `score.performance`
    tool or set arbitrarily. The `target_score` is where you want to code to
    be.

    **Returns**

    A unified diff markdown code-block containing potential changes.

    **Requirements**

    - A qdrant URL
    - The LLM of your choice, in this example we use OpenAI so you need to
      set the `OPENAI_API_KEY` environment variable

    Here is a full working example to calling this tool:

    ```python hl_lines="39-61"
    import asyncio
    import json
    import os
    import shutil
    from pathlib import Path
    from tempfile import gettempdir

    from fastmcp import Client
    from fastmcp.utilities.logging import configure_logging


    async def main(code_file: str, func_name: str, lang: str, target_score: float, verbose: bool) -> None:
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
                "fault_extract_code_block", {
                    "file": code_file,
                    "func": func_name
                })
            
            snippet = json.loads(p[0].text)["full"]  # (1)!

            p = await client.call_tool(
                "fault_score_performance", {
                    "snippet": snippet,
                    "lang": lang
                })

            score = json.loads(p[0].text)["score"]  # (2)!

            p = await client.call_tool(
                "fault_suggest_better_function_performance", {
                    "snippet": snippet,
                    "lang": lang,
                    "score": score,
                    "target_score": target_score
                })
            
            print(p)


    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--verbose",action='store_true')
        parser.add_argument("code_file")
        parser.add_argument("func_name")
        parser.add_argument("lang")
        parser.add_argument("target_score", type=float)
        args = parser.parse_args()

        asyncio.run(main(args.code_file, args.func_name, args.lang, args.target_score, args.verbose))
    ```

    1. Retrieve the snippet from the agent's response
    2. Retrieve the score from the agent's response

!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```


## Tool: Function reliability improvements suggestions

Scoring the reliability of a **single function** will help you understand how
much attention it requires.

-   [X] Evaluate function reliability

    **Tool** `#!python "fault_suggest_better_function_reliability"`

    **Payload**
    ```json
    {
        "snippet": "",
        "lang": "",
        "score": 0.3,
        "target_score": 0.8
    }
    ```

    The `snippet` argument is the full code of a function or any code snippet.
    The `lang` hints the language of the snippet. The `score` is the current
    scoring of the snippet. This can be extracted using the `score.performance`
    tool or set arbitrarily. The `target_score` is where you want to code to
    be.

    **Returns**

    A unified diff markdown code-block containing potential changes.

    **Requirements**

    - A qdrant URL
    - The LLM of your choice, in this example we use OpenAI so you need to
      set the `OPENAI_API_KEY` environment variable

    Here is a full working example to calling this tool:

    ```python hl_lines="39-61"
    import asyncio
    import json
    import os
    import shutil
    from pathlib import Path
    from tempfile import gettempdir

    from fastmcp import Client
    from fastmcp.utilities.logging import configure_logging


    async def main(code_file: str, func_name: str, lang: str, target_score: float, verbose: bool) -> None:
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
                "fault_extract_code_block", {
                    "file": code_file,
                    "func": func_name
                })
            
            snippet = json.loads(p[0].text)["full"]

            p = await client.call_tool(
                "fault_score_performance", {
                    "snippet": snippet,
                    "lang": lang
                })

            score = json.loads(p[0].text)["score"]

            p = await client.call_tool(
                "fault_suggest_better_function_reliability", {
                    "snippet": snippet,
                    "lang": lang,
                    "score": score,
                    "target_score": target_score
                })
            
            print(p)


    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--verbose",action='store_true')
        parser.add_argument("code_file")
        parser.add_argument("func_name")
        parser.add_argument("lang")
        parser.add_argument("target_score", type=float)
        args = parser.parse_args()

        asyncio.run(main(args.code_file, args.func_name, args.lang, args.target_score, args.verbose))
    ```

    1. Retrieve the snippet from the agent's response
    2. Retrieve the score from the agent's response

!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```

## Tool: Suggests SLO

Service Level Objects are powerful tools to pilot your user satisfaction.
<span class="f">fault</span> is able to suggest SLO definitions for a function.

-   [X] Evaluate function reliability

    **Tool** `#!python "fault_suggest_service_level_objectives_slo"`

    **Payload**
    ```json
    {
        "snippet": "",
        "lang": "",
    }
    ```

    The `snippet` argument is the full code of a function or any code snippet.
    The `lang` hints the language of the snippet.

    **Returns**

    A JSON array of SLO objects. Each object is made of the following properties:

    * `type`: the kind of SLO
    * `title`: a human readable title for the SLO
    * `objective`: the value in the `[0, 100[` range
    * `threshold`: a value appropriate for the type of objective
    * `unit`: the unit for the threshold
    * `window`: the window for the objective
    * `sli`: an object made of two keys you can use to configure your platform

    **Requirements**

    - A qdrant URL
    - The LLM of your choice, in this example we use OpenAI so you need to
      set the `OPENAI_API_KEY` environment variable

    !!! example "Output Example"

        Here is a full working example to calling this tool:

        ```json
        [
            {
                "type": "latency",
                "title": "95th percentile latency",
                "objective": 95.0,
                "explanation": "95th percentile request latency under threshold ensures responsive service",
                "threshold": 0.3,
                "unit": "s",
                "window": "300s",
                "sli": {
                    "prometheus": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{handler=\"index\"}[5m])) by (le))",
                    "gcp/cloudrun": {
                        "displayName": "95th percentile latency - 5min",
                        "goal": 0.95,
                        "calendarPeriod": "NONE",
                        "serviceLevelIndicator": {
                        "windowsBased": {
                            "windowPeriod": "300s",
                            "goodTotalRatioThreshold": {
                            "basicSliPerformance": {
                                "latency": {
                                "threshold": "0.3s"
                                }
                            },
                            "threshold": 0.95
                            }
                        }
                        }
                    }
                }
            },
            {
                "type": "availability",
                "title": "Successful request ratio",
                "objective": 99.9,
                "explanation": "Percentage of successful (2xx) responses to ensure uptime",
                "threshold": 99.9,
                "unit": "%",
                "window": "300s",
                "sli": {
                    "prometheus": "sum(rate(http_requests_total{handler=\"index\",status=~\"2..\"}[5m]))/sum(rate(http_requests_total{handler=\"index\"}[5m]))*100",
                    "gcp/cloudrun": {
                        "displayName": "99.9% availability - 5min",
                        "goal": 0.999,
                        "calendarPeriod": "NONE",
                        "serviceLevelIndicator": {
                        "windowsBased": {
                            "windowPeriod": "300s",
                            "goodTotalRatioThreshold": {
                            "threshold": 0.999
                            }
                        }
                        }
                    }
                }
            },
            {
                "type": "error",
                "title": "Error rate",
                "objective": 99.0,
                "explanation": "Ensure error responses remain below 1% to detect upstream issues",
                "threshold": 1.0,
                "unit": "%",
                "window": "300s",
                "sli": {
                    "prometheus": "sum(rate(http_requests_total{handler=\"index\",status!~\"2..\"}[5m]))/sum(rate(http_requests_total{handler=\"index\"}[5m]))*100",
                    "gcp/cloudrun": {
                        "displayName": "99% error rate - 5min",
                        "goal": 0.99,
                        "calendarPeriod": "NONE",
                        "serviceLevelIndicator": {
                        "windowsBased": {
                            "windowPeriod": "300s",
                            "goodTotalRatioThreshold": {
                            "threshold": 0.99
                            }
                        }
                        }
                    }
                }
            }
        ]
        ```

    ```python hl_lines="39-51"
    import asyncio
    import json
    import os
    import shutil
    from pathlib import Path
    from tempfile import gettempdir

    from fastmcp import Client
    from fastmcp.utilities.logging import configure_logging


    async def main(code_file: str, func_name: str, lang: str, verbose: bool) -> None:
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
                "fault_extract_code_block", {
                    "file": code_file,
                    "func": func_name
                })
            
            snippet = json.loads(p[0].text)["full"]  # (1)!

            p = await client.call_tool(
                "fault_suggest_service_level_objectives_slo", {
                    "snippet": snippet,
                    "lang": lang
                })
            
            print(p)


    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--verbose",action='store_true')
        parser.add_argument("code_file")
        parser.add_argument("func_name")
        parser.add_argument("lang")
        args = parser.parse_args()

        asyncio.run(main(args.code_file, args.func_name, args.lang, args.verbose))
    ```

    1. Retrieve the snippet from the agent's response

!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```

## Tool: Full file code changes recommendations

<span class="f">fault</span> may generate a unified diff of changed to apply
to a **full file** in order to improve its performance and reliability.

-   [X] Evaluate function reliability

    **Tool** `#!python "fault_make_reliability_and_perf_changes"`

    **Payload**
    ```json
    {
        "file": "",
    }
    ```

    The `file` argument is the absolute path to a file to seek changes for.

    **Returns**

    A JSON object with the following properties:

    * `score`: a number between 0.0 (very unreliable) and 1.0 (very reliable) of the file.
    * `explanation`: a short summary of the main threats you found and suggested changes.
    * `old`: always the full content of the original file as-is.
    * `new`: the new file content.
    * `dependencies`: an array of dependencies that may be needed.
    * `diff`: the unified diff between the two file versions.

    **Requirements**

    - A qdrant URL
    - The LLM of your choice, in this example we use OpenAI so you need to
      set the `OPENAI_API_KEY` environment variable

    !!! example "Output Example"

        The output returns a score of `0.2` for the existing code and the
        following explanation for the changes:

        > The original code used a blocking HTTP call without timeouts, retries,
        error handling, or client reuse. It could hang indefinitely, overwhelm
        resources, and surface unhandled exceptions to clients. The new version
        uses an async shared HTTPX client with connection limits and timeouts,
        adds retry logic with exponential backoff (via tenacity), maps errors to
        proper HTTP responses, and ensures the client is closed on shutdown.

        Next is a snippet of the generated diff:

        ```diff
        --- app.py
        +++ app.py
        @@ -1,15 +1,67 @@
        import os
        +import logging
        +from functools import lru_cache
        +import httpx
        +from fastapi import FastAPI, HTTPException
        +from fastapi.responses import JSONResponse
        +from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
        
        -import httpx
        -from fastapi import FastAPI
        +# Initialize logger
        +logger = logging.getLogger(__name__)
        +logging.basicConfig(level=logging.INFO)
        
        UPSTREAM_URL = os.getenv("UPSTREAM_URL", "https://jsonplaceholder.typicode.com")
        
        app = FastAPI()
        
        +@lru_cache()
        +def get_http_client() -> httpx.AsyncClient:
        +    """
        +    Create a shared Async HTTP client with connection limits and timeouts.
        +    """
        +    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
        +    timeout = httpx.Timeout(5.0, connect=2.0)
        +    return httpx.AsyncClient(limits=limits, timeout=timeout)
        +
        +@retry(
        +    retry=retry_if_exception_type(httpx.HTTPError),
        +    stop=stop_after_attempt(3),
        +    wait=wait_exponential(multiplier=1, min=1, max=10)
        +)
        +async def fetch_todo() -> dict:
        +    """
        +    Fetch the todo item with retry logic for transient errors.
        +    Raises HTTPStatusError or RequestError on failure.
        +    """
        +    client = get_http_client()
        +    url = f"{UPSTREAM_URL}/todos/1"
        +    headers = {"Host": "jsonplaceholder.typicode.com"}
        +    response = await client.get(url, headers=headers)
        +    response.raise_for_status()
        +    return response.json()
        +
        +@app.on_event("shutdown")
        +async def shutdown_event():
        +    """
        +    Close the HTTP client on application shutdown.
        +    """
        +    client = get_http_client()
        +    await client.aclose()
        
        @app.get("/")
        -def index():
        -    return httpx.get(f"{UPSTREAM_URL}/todos/1", headers={
        -        "Host": "jsonplaceholder.typicode.com"
        -    }).json()
        +async def index():
        +    """
        +    Endpoint to retrieve a todo item. Implements retries, timeouts, and error handling.
        +    """
        +    try:
        +        data = await fetch_todo()
        +        return JSONResponse(content=data)
        +    except httpx.HTTPStatusError as exc:
        +        logger.error("Upstream returned error %s: %s", exc.response.status_code, exc)
        +        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
        +    except httpx.RequestError as exc:
        +        logger.error("Network error while fetching todo: %s", exc)
        +        raise HTTPException(status_code=502, detail="Bad Gateway")
        +    except Exception as exc:
        +        logger.exception("Unexpected error: %s", exc)
        +        raise HTTPException(status_code=500, detail="Internal Server Error")
        ```

    ```python hl_lines="70-72"  title="e2e.py"
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
        parser.add_argument("--llm", choices=["openai", "openrouter", "ollama"])
        parser.add_argument("--verbose",action='store_true')
        args = parser.parse_args()

        asyncio.run(main(args.llm, args.verbose))

    ```

!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```

## Tool: Evaluate Blackhole Impact

-   [X] Evaluate function reliability during a blackhole event

    **Tool** `#!python "fault_run_blackhole_impact_scenario"`

    **Payload**
    ```json
    {
        "url": "",
        "method": "",
        "body": "",
        "direction": "",
        "side": "",
        "duration": "",
        "num_clients": "",
        "rps": "",
        "timeout": 10,
        "proxies": [],
    }
    ```

    The `url` argument is the absolute address of the endpoint to send traffic
    to. The `direction` and `side` on which to apply the blackhole. We suggest,
    `"egress"` and `"server"`. The `duration` indicates how long to run this
    scenario for and the `num_clients`/`rps` declare traffic parameters such
    as how many clients and requests per second. Finally, the `proxies`
    argument is an array of [TCP proxies](../proxy/protocols/tcp.md) if you
    want to apply the blackhole a remote call made by your endpoint rather than
    directly on your endpoint. The `timeout` argument, in seconds, is used by
    the client when communicating with the application.

    **Returns**

    A markdown [report](../scenarios/reporting.md) of the scenario.

    **Requirements**

    - A qdrant URL
    - The LLM of your choice, in this example we use OpenAI so you need to
      set the `OPENAI_API_KEY` environment variable

    ```python hl_lines="38-52" title="inject-blackhole.py"
    import asyncio
    import os
    import shutil
    from pathlib import Path
    from tempfile import gettempdir

    from fastmcp import Client
    from fastmcp.utilities.logging import configure_logging


    async def main(url: str, upstream: str, verbose: bool) -> None:
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
                "fault_run_blackhole_impact_scenario", {
                    "url": url,
                    "method": "GET",
                    "body": "",
                    "duration": "10s",
                    "direction": "egress",
                    "side": "server",
                    "num_clients": 1,
                    "rps": 3,
                    "timeout": 5,
                    "proxies": [
                        f"34000={upstream}:443" # (1)!
                    ]
                })

            print(p[0].text)


    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--verbose",action='store_true')
        parser.add_argument("url")
        parser.add_argument("upstream")
        args = parser.parse_args()

        asyncio.run(main(args.url, args.upstream, args.verbose))
    ```

    1. Mapping the proxy address `0.0.0.0:34000` to forward traffic to the
       real upstream server on port 443.

In the case of our application above this would be called as follows:

```bash
python inject-blackhole.py http://localhost:9090 https://jsonplaceholder.typicode.com
```

The blackhole event will take place on the response coming back from the
upstream server (`https://jsonplaceholder.typicode.com`).

!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```

## Tool: Evaluate Latency Impact

-   [X] Evaluate function reliability during a latency event

    **Tool** `#!python "fault_run_latency_impact_scenario"`

    **Payload**
    ```json
    {
        "url": "",
        "method": "",
        "body": "",
        "latency": 0,
        "deviation": 0,
        "per_read_write_op": false,
        "direction": "",
        "side": "",
        "duration": "",
        "num_clients": "",
        "rps": "",
        "timeout": 10,
        "proxies": [],
    }
    ```

    The `url` argument is the absolute address of the endpoint to send traffic
    to. The `direction` and `side` on which to apply the latency. 
    The `duration` indicates how long to run this
    scenario for and the `num_clients`/`rps` declare traffic parameters such
    as how many clients and requests per second. Finally, the `proxies`
    argument is an array of [TCP proxies](../proxy/protocols/tcp.md) if you
    want to apply the latency a remote call made by your endpoint rather than
    directly on your endpoint. The `timeout` argument, in seconds, is used by
    the client when communicating with the application.

    **Returns**

    A markdown [report](../scenarios/reporting.md) of the scenario.

    **Requirements**

    - A qdrant URL
    - The LLM of your choice, in this example we use OpenAI so you need to
      set the `OPENAI_API_KEY` environment variable

    ```python hl_lines="38-55" title="inject-latency.py"
    import asyncio
    import os
    import shutil
    from pathlib import Path
    from tempfile import gettempdir

    from fastmcp import Client
    from fastmcp.utilities.logging import configure_logging


    async def main(url: str, upstream: str, latency: float, verbose: bool) -> None:
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
                "fault_run_latency_impact_scenario", {
                    "url": url,
                    "method": "GET",
                    "body": "",
                    "duration": "10s",
                    "latency": latency,
                    "per_read_write_op": False,
                    "deviation": 0,
                    "direction": "ingress",
                    "side": "server",
                    "num_clients": 1,
                    "rps": 3,
                    "timeout": 10,
                    "proxies": [
                        f"34000={upstream}:443" # (1)!
                    ]
                })

            print(p[0].text)


    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--verbose",action='store_true')
        parser.add_argument("url")
        parser.add_argument("upstream")
        parser.add_argument("latency", type=float)
        args = parser.parse_args()

        asyncio.run(main(args.url, args.upstream, args.latency, args.verbose))

    ```

    1. Mapping the proxy address `0.0.0.0:34000` to forward traffic to the
       real upstream server on port 443.

In the case of our application above this would be called as follows:

```bash
python inject-latency.py http://localhost:9090 https://jsonplaceholder.typicode.com 300
```

!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```

## Tool: Evaluate Packet Loss Impact

-   [X] Evaluate function reliability during a packet loss event

    **Tool** `#!python "fault_run_packet_loss_impact_scenario"`

    **Payload**
    ```json
    {
        "url": "",
        "method": "",
        "body": "",
        "direction": "",
        "side": "",
        "duration": "",
        "num_clients": "",
        "rps": "",
        "timeout": 10,
        "proxies": [],
    }
    ```

    The `url` argument is the absolute address of the endpoint to send traffic
    to. The `direction` and `side` on which to apply the packet loss. 
    The `duration` indicates how long to run this
    scenario for and the `num_clients`/`rps` declare traffic parameters such
    as how many clients and requests per second. Finally, the `proxies`
    argument is an array of [TCP proxies](../proxy/protocols/tcp.md) if you
    want to apply the packet loss a remote call made by your endpoint rather than
    directly on your endpoint. The `timeout` argument, in seconds, is used by
    the client when communicating with the application.

    **Returns**

    A markdown [report](../scenarios/reporting.md) of the scenario.

    **Requirements**

    - A qdrant URL
    - The LLM of your choice, in this example we use OpenAI so you need to
      set the `OPENAI_API_KEY` environment variable

    ```python hl_lines="38-52" title="inject-packet-loss.py"
    import asyncio
    import os
    import shutil
    from pathlib import Path
    from tempfile import gettempdir

    from fastmcp import Client
    from fastmcp.utilities.logging import configure_logging


    async def main(url: str, upstream: str, verbose: bool) -> None:
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
                "fault_run_packet_loss_impact_scenario", {
                    "url": url,
                    "method": "GET",
                    "body": "",
                    "duration": "10s",
                    "direction": "egress",
                    "side": "server",
                    "num_clients": 1,
                    "timeout": 10,
                    "rps": 3,
                    "proxies": [
                        f"34000={upstream}:443" # (1)!
                    ]
                })

            print(p[0].text)


    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--verbose",action='store_true')
        parser.add_argument("url")
        parser.add_argument("upstream")
        args = parser.parse_args()

        asyncio.run(main(args.url, args.upstream, args.verbose))
    ```

    1. Mapping the proxy address `0.0.0.0:34000` to forward traffic to the
       real upstream server on port 443.

In the case of our application above this would be called as follows:

```bash
python inject-packet-loss.py http://localhost:9090 https://jsonplaceholder.typicode.com
```

!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```

## Tool: Evaluate Bandwidth Impact

-   [X] Evaluate function reliability during a bandwidth event

    **Tool** `#!python "fault_run_bandwidth_impact_scenario"`

    **Payload**
    ```json
    {
        "url": "",
        "method": "",
        "body": "",
        "direction": "",
        "rate": 0,
        "unit": "bps",
        "side": "",
        "duration": "",
        "num_clients": "",
        "rps": "",
        "timeout": 10,
        "proxies": [],
    }
    ```

    The `url` argument is the absolute address of the endpoint to send traffic
    to. The `direction` and `side` on which to apply the bandwidth.
    The `duration` indicates how long to run this
    scenario for and the `num_clients`/`rps` declare traffic parameters such
    as how many clients and requests per second. Finally, the `proxies`
    argument is an array of [TCP proxies](../proxy/protocols/tcp.md) if you
    want to apply the bandwidth a remote call made by your endpoint rather than
    directly on your endpoint. The `timeout` argument, in seconds, is used by
    the client when communicating with the application.

    **Returns**

    A markdown [report](../scenarios/reporting.md) of the scenario.

    **Requirements**

    - A qdrant URL
    - The LLM of your choice, in this example we use OpenAI so you need to
      set the `OPENAI_API_KEY` environment variable

    ```python hl_lines="38-54" title="inject-bandwidth.py"
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
                        f"34000={upstream}:443" # (1)!
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
    ```

    1. Mapping the proxy address `0.0.0.0:34000` to forward traffic to the
       real upstream server on port 443.

In the case of our application above this would be called as follows (reduced to 1024 bytes per second):

```bash
python inject-bandwidth.py http://localhost:9090 https://jsonplaceholder.typicode.com 1024
```

!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```

## Tool: Evaluate Jitter Impact

-   [X] Evaluate function reliability during a jitter event

    **Tool** `#!python "fault_run_jitter_impact_scenario"`

    **Payload**
    ```json
    {
        "url": "",
        "method": "",
        "body": "",
        "direction": "",
        "rate": 0,
        "unit": "bps",
        "side": "",
        "duration": "",
        "num_clients": "",
        "rps": "",
        "timeout": 10,
        "proxies": [],
    }
    ```

    The `url` argument is the absolute address of the endpoint to send traffic
    to. The `direction` and `side` on which to apply the bandwidth.
    The `duration` indicates how long to run this
    scenario for and the `num_clients`/`rps` declare traffic parameters such
    as how many clients and requests per second. Finally, the `proxies`
    argument is an array of [TCP proxies](../proxy/protocols/tcp.md) if you
    want to apply the jitter a remote call made by your endpoint rather than
    directly on your endpoint. The `timeout` argument, in seconds, is used by
    the client when communicating with the application.

    **Returns**

    A markdown [report](../scenarios/reporting.md) of the scenario.

    **Requirements**

    - A qdrant URL
    - The LLM of your choice, in this example we use OpenAI so you need to
      set the `OPENAI_API_KEY` environment variable

    !!! example "Output Example"

        Here is an report sample:

        # Scenarios Report

        Start: 2025-06-27 14:14:36.689011165 UTC

        End: 2025-06-27 14:14:47.020905358 UTC

        ## Scenario: Evaluating runtime performance of http://localhost:9090  (items: 1)

        ### 🎯 `GET` http://localhost:9090 | Passed

        **Call**:

        - Method: `GET`
        - Timeout: 10000ms
        - Headers: -
        - Body?: No

        **Strategy**: load for 10s with 1 clients @ 3 RPS

        **Faults Applied**:

        | Type | Timeline | Description |
        |------|----------|-------------|
        | jitter | 0% `xxxxxxxxxx` 100% | Jitter: ➡️🖧Amplitude: 150.00ms, Frequence 5.00Hz |


        **Run Overview**:

        | Num. Requests | Num. Errors | Min. Response Time | Max Response Time | Mean Latency (ms) | Expectation Failures | Total Time |
        |-----------|---------|--------------------|-------------------|-------------------|----------------------|------------|
        | 31 | 0 (0.0%) | 83.65 | 272.49 | 199.92 | 0 | 10 seconds and 329 ms |

        | Latency Percentile | Latency (ms) | Num. Requests (% of total) |
        |------------|--------------|-----------|
        | p25 | 133.61 | 8 (25.8%) |
        | p50 | 199.92 | 16 (51.6%) |
        | p75 | 235.69 | 24 (77.4%) |
        | p95 | 269.28 | 31 (100.0%) |
        | p99 | 272.49 | 31 (100.0%) |

        | SLO       | Pass? | Objective | Margin | Num. Requests Over Threshold (% of total) |
        |-----------|-------|-----------|--------|--------------------------|
        | 99% @ 350ms | ✅ | 99% < 350ms | Below by 77.5ms | 0 (0.0%) |
        | 95% @ 200ms | ❌ | 95% < 200ms | Above by 69.3ms | 15 (48.4%) |


        ---


    ```python hl_lines="38-54" title="inject-jitter.py"
    import asyncio
    import os
    import shutil
    from pathlib import Path
    from tempfile import gettempdir

    from fastmcp import Client
    from fastmcp.utilities.logging import configure_logging


    async def main(url: str, upstream: str, amplitude: float, frequency: float, verbose: bool) -> None:
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
                "fault_run_jitter_impact_scenario", {
                    "url": url,
                    "method": "GET",
                    "body": "",
                    "duration": "10s",
                    "amplitude": amplitude,
                    "frequency": frequency,
                    "direction": "ingress",
                    "side": "server",
                    "num_clients": 1,
                    "rps": 3,
                    "timeout": 10,
                    "proxies": [
                        f"34000={upstream}:443" # (1)!
                    ]
                })

            print(p[0].text)


    if __name__ == "__main__":
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--verbose",action='store_true')
        parser.add_argument("url")
        parser.add_argument("upstream")
        parser.add_argument("amplitude", type=float)
        parser.add_argument("frequency", type=float)
        args = parser.parse_args()

        asyncio.run(main(args.url, args.upstream, args.amplitude, args.frequency))

    ```

    1. Mapping the proxy address `0.0.0.0:34000` to forward traffic to the
       real upstream server on port 443.

In the case of our application above this would be called as follows:

```bash
python inject-jitter.py http://localhost:9090 https://jsonplaceholder.typicode.com 50 3
```

!!! tip

    You may see the logs from the `fault` call by setting ` --verbose`:

    ```bash
    tail -f /tmp/fault.log
    ```
