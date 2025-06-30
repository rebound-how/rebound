# Configure <span class="f">fault</span> LLM Provider

This guide will take you through configuring the LLM models for
<span class="f">fault</span>


!!! abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span>

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../install.md).

        Make sure the `fault` binary can be found in your `PATH`.

!!! warning

    This guide requires the [agent feature](../install.md#features-matrix) to
    be enabled.

## Overview

<span class="f">fault</span> lets you configure your agent's models via
command [line parameters](../../reference/cli-commands.md#agent-command-options)
or [environment variables](../../reference/environment-variables.md#agent-command-variables).

The parameters are all set on the `fault agent` command.

If you are not relying on the default setup which uses the OpenAI client, we
suggest that you set the environment variables once and for all. Otherwise,
your command line will get busy very quickly.


## Gemini

<span class="f">fault</span> supports
[Gemini](https://ai.google.dev/).

-   [X] Set an Gemini's API key

    Set the `GEMINI_API_KEY` for the `fault` binary to pick it up.

    ```bash
    export GEMINI_API_KEY=...
    ```

    Make sure the key is allowed to use the models you wich to use as well.

-   [X] Configure the client

    Enable the Gemini client. This can also be
    set via the `FAULT_AGENT_CLIENT` environment variable.

    ```bash
    --llm-client gemini
    ```

-   [X] Configure the model parameters

    The model used for reasoning. This can also be
    set via the `LLM_PROMPT_REASONING_MODEL` environment variable.

    ```bash
    --llm-prompt-reasoning-model gemini-2.5-flash
    ```

    The embedding model, default to `text-embedding-3-small`. This can also be
    set via the `FAULT_AGENT_EMBED_MODEL` environment variable.

    ```bash
    --llm-embed-model gemini-embedding-exp-03-07
    ```

    !!! warning "Embedding model not yet supported"

        Currently, the embedding model is ignored and
        <span class="f">fault</span> uses
        [fastembed](https://github.com/qdrant/fastembed) instead. A future
        release will support Google's model.

    The embedding model dimension, default to `384`. This can also be
    set via the `FAULT_AGENT_EMBED_MODEL_DIMENSION` environment variable.

    ```bash
    --llm-embed-model-dim 384
    ```

## OpenAI

<span class="f">fault</span> supports
[OpenAI](https://platform.openai.com/docs/models) and is configured by
default to use it. So you, if you intend on using OpenAI, you only need to set
the `OPENAI_API_KEY` environment variable.

-   [X] Set an OpenAI's API key

    Set the `OPENAI_API_KEY` for the `fault` binary to pick it up.

    ```bash
    export OPENAI_API_KEY=sk-...
    ```

    Make sure the key is allowed to use the models you wich to use as well.

-   [X] Configure the client

    Enable the OpenAI client (which is the default). This can also be
    set via the `FAULT_AGENT_CLIENT` environment variable.

    ```bash
    --llm-client open-ai
    ```

-   [X] Configure the model parameters

    The model used for reasoning, default to `o4-mini`). This can also be
    set via the `LLM_PROMPT_REASONING_MODEL` environment variable.

    ```bash
    --llm-prompt-reasoning-model o4-mini
    ```

    The embedding model, default to `text-embedding-3-small`. This can also be
    set via the `FAULT_AGENT_EMBED_MODEL` environment variable.

    ```bash
    --llm-embed-model text-embedding-3-small
    ```

    The embedding model dimension, default to `1536`. This can also be
    set via the `FAULT_AGENT_EMBED_MODEL_DIMENSION` environment variable.

    ```bash
    --llm-embed-model-dim 1536
    ```

## Ollama

<span class="f">fault</span> supports
[ollama](https://ollama.com/). This is great if you need to keep data
privacy under control and/or if you have a specific home made model.

-   [X] Configure the client

    Enable the OpenAI client (which is the default). This can also be
    set via the `FAULT_AGENT_CLIENT` environment variable.

    ```bash
    --llm-client ollama
    ```

-   [X] Configure the model parameters

    You may specify which [model](https://ollama.com/search)
    you want to use via the following parameters:

    The model used for reasoning. This can also be
    set via the `LLM_PROMPT_REASONING_MODEL` environment variable.

    ```bash
    --llm-prompt-reasoning-model gemma3:4b
    ```

    The embedding model. This can also be
    set via the `FAULT_AGENT_EMBED_MODEL` environment variable.

    ```bash
    --llm-embed-model mxbai-embed-large
    ```

    The embedding model dimension. This can also be
    set via the `FAULT_AGENT_EMBED_MODEL_DIMENSION` environment variable.

    ```bash
    --llm-embed-model-dim 1024
    ```

## OpenRouter

<span class="f">fault</span> supports
[OpenRouter](https://openrouter.ai/). This is great if you want to try
many models and find the most appropriate for your needs.

-   [X] Set an OpenRouter's API key

    Set the `OPENROUTER_API_KEY` for the `fault` binary to pick it up.

    ```bash
    export OPENROUTER_API_KEY=sk-...
    ```

-   [X] Configure the client

    Enable the OpenRouter client. This can also be
    set via the `FAULT_AGENT_CLIENT` environment variable.

    ```bash
    --llm-client open-router
    ```

-   [X] Configure the model parameters

    You may specify which [model](https://openrouter.ai/models)
    you want to use via the following parameters:

    The model used for reasoning. This can also be
    set via the `LLM_PROMPT_REASONING_MODEL` environment variable.

    ```bash
    --llm-prompt-reasoning-model google/gemma-3-27b-it
    ```

    The embedding model dimension. This can also be
    set via the `FAULT_AGENT_EMBED_MODEL_DIMENSION` environment variable.

    ```bash
    --llm-embed-model-dim 384
    ```

    !!! warning "No explicit embedding model"

        OpenRouter doesn't have embedding models and thus the
        `--llm-embed-model` parameter is ignored. However, we set the 
        the `--llm-embed-model-dim` parameter because we use
        [FastEmbed](https://github.com/qdrant/fastembed)
        to workaround this issue.
