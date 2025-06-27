# Platform Analysis

This guide will show you how to analyze your platform resources, from an
angle of resilience and reliability, using LLM.

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

    -   [X] Install a local qdrant database

        <span class="f">fault</span> uses [qdrant](https://qdrant.tech/) for its vector database. You
        can install a [local](https://qdrant.tech/documentation/quickstart/),
        free, qdrant using docker:

        ```bash
        docker run -p 6333:6333 -p 6334:6334 -v "$(pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant
        ```

!!! danger "Windows not supported"

    Unfortunately, the {==agent==} feature is not supported on Windows because
    the framework used by fault to interact with LLM does not support that
    platform.

!!! info "Experimental feature"

    This feature is still experimental and is subject to change. Dealing with
    LLM requires accepting a level of fuzzyness and adjustments. Engineering
    is still very much a human endeavour!

## Review a Kubernetes Cluster



-   [X] Source code of the application
