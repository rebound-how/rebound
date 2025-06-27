# Configure <span class="f">fault</span> Your MCP Agent Servers

This guide will take you through configuring the <span class="f">fault</span>
[MCP server](https://modelcontextprotocol.io/specification/2025-06-18/server).

!!! abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span>

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../install.md).

        Make sure the `fault` binary can be found in your `PATH`.

!!! tip

    <span class="f">fault</span> respects the [MCP Server](https://modelcontextprotocol.io/specification/2025-06-18/server)
    interface. Currently it relies on the [stdio transport](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#stdio). It should be supported by any MCP
    client aware clients.

## Cursor

-   [X] Configure the MCP settings for [Cursor](https://www.cursor.com/)

    Add the following section to your global {==~/.cursor/mcp.json==} file:

    ```json
    {
        "mcpServers": {
            "fault": {
                "type": "stdio",
                "command": "fault",
                "disabled": false,
                "args": [
                    "agent",
                    "tool"
                ],
                "env": {
                    "OPENAI_API_KEY": "..."
                }
            }
        }
    }
    ```

    !!! tip

        We are using the default OpenAI API and therefore expect the
        `OPENAI_API_KEY`. If you switch to ollama or Open Router, these
        settings may differ. Do not commit this file if you copy your key.
        Or you may also use the 

    You may also want to enable a log file for the `fault` MCP server:

    ```json
    {
        "mcpServers": {
            "fault": {
                "type": "stdio",
                "command": "fault",
                "disabled": false,
                "args": [
                    "--log-file",
                    "/tmp/fault.log",
                    "--log-level",
                    "debug",
                    "agent",
                    "tool"
                ],
                "env": {
                    "OPENAI_API_KEY": "..."
                }
            }
        }
    }
    ```

    You may want to explore the [Cursor](https://docs.cursor.com/context/model-context-protocol) documentation for more
    information.

## Kilo Code

-   [X] Configure the MCP settings for [Kilo Code](https://kilocode.ai/)

    Add the following section to the {==.kilocode/mcp.json==} file at the
    root directory of any project:

    ```json
    {
        "mcpServers": {
            "fault": {
                "type": "stdio",
                "command": "fault",
                "disabled": false,
                "args": [
                    "agent",
                    "tool"
                ],
                "env": {
                    "OPENAI_API_KEY": "..."
                }
            }
        }
    }
    ```

    !!! tip

        We are using the default OpenAI API and therefore expect the
        `OPENAI_API_KEY`. If you switch to ollama or Open Router, these
        settings may differ. Do not commit this file if you copy your key.
        Or you may also use the 

    You may also want to enable a log file for the `fault` MCP server:

    ```json
    {
        "mcpServers": {
            "fault": {
                "type": "stdio",
                "command": "fault",
                "disabled": false,
                "args": [
                    "--log-file",
                    "/tmp/fault.log",
                    "--log-level",
                    "debug",
                    "agent",
                    "tool"
                ],
                "env": {
                    "OPENAI_API_KEY": "..."
                }
            }
        }
    }
    ```

    You may want to explore the [Kilo Code](https://kilocode.ai/docs/features/mcp/using-mcp-in-kilo-code#configuring-mcp-servers) documentation for more
    information.


    !!! tip

        You may need to restart the Visual Studio Code instance for the changes
        to take effect.

## Zed

-   [X] Configure the MCP settings for [Zed](https://zed.dev/)

    Add the following section to your project {==~/.zed/settings.json==} settings file:

    ```json
    {
        "context_servers": {
            "fault": {
                "source": "custom",
                "command": {
                    "path": "fault",
                    "args": ["agent", "tool"],
                    "env": {
                        "OPENAI_API_KEY": "..."
                    }
                },
                "settings": {}
            }
        }
    }
    ```

    !!! tip

        We are using the default OpenAI API and therefore expect the
        `OPENAI_API_KEY`. If you switch to ollama or Open Router, these
        settings may differ. Do not commit this file if you copy your key.
        Or you may also use the 

    You may also want to enable a log file for the `fault` MCP server:

    ```json
    {
        "context_servers": {
            "fault": {
                "source": "custom",
                "command": {
                    "path": "fault",
                    "args": [
                        "--log-file",
                        "/tmp/fault.log",
                        "--log-level",
                        "debug",
                        "agent",
                        "tool"
                    ],
                    "env": {
                        "OPENAI_API_KEY": "..."
                    }
                },
                "settings": {}
            }
        }
    }
    ```

    You may want to explore the [Zed](https://zed.dev/docs/ai/mcp) documentation for more
    information.

## Next Steps

You've successfully deployed <span class="f">fault</span> MCP server in your
favourite AI code editor.

- **Explore our [MCP tools](./mcp-tools.md)** to learn how to first use the agent.
