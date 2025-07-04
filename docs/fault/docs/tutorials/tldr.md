# tl;dr

## Overview

<span class="f">fault</span> comes with two main capabilities in one CLI.

* Fault Injection: operation oriented features
* AI Agent: LLM-based features

```mermaid
---
config:
  theme: 'forest'
---
mindmap
  root((fault CLI))
    Fault Injection
      Proxy
      Scenario
    AI Agent
      Review
      MCP
```


## Getting started with fault injection

The core of <span class="f">fault</span> is its fault injection engine. It
allows you to:


-   [X] Inject faults into your services

    Run `fault run` to start injecting network failures

-   [X] Automate these failures into YAML files that can be run from your CI

    Run `fault scenario generate` and `fault scenario run` to create
    YAML-based scenarios that can be stored alongside your code and executed
    from your CI.


## Getting started with the AI Agent

If you are keen to get started with the AI-agent, the general steps are as
follows:

-   [X] Pick up your favorite LLM

    <span class="f">fault</span> supports OpenAI, Gemini, OpenRouter and ollama.
    If you use any of the cloud-based LLMs, you will need to generate an API
    key. If you want privacy, go with ollama.

-   [X] Configure your AI-Code editor

    [Setup the editor](../how-to/agent/llm-configuration.md) of your choice so
    it knows how to find fault as a MCP server. Most of the time it's by adding
    a `mcpServers` object somewhere in their settings file.


## Next Steps

* **Start exploring our [tutorials](getting-started.md)** to gently get into using <span class="f">fault</span>.
* **Explore our [How-To guides](../how-to/proxy/faults/configure-latency.md)** to explore <span class="f">fault</span>'s features.
