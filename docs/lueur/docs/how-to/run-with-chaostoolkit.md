# Run fault as a Chaos Toolkit Action

This guide will walk you through running fault as a [Chaos Toolkit][ctk] action
in your Chaos Engineering experiments.

[ctk]: https://chaostoolkit.org/
[exp]: https://chaostoolkit.org/reference/api/experiment/
[pypa]: https://packaging.python.org/en/latest/tutorials/installing-packages/
[ctkfault]: https://github.com/chaostoolkit-incubator/chaostoolkit-fault

??? abstract "Prerequisites"

    -   [X] Install fault

        If you haven’t installed fault yet, follow the
        [installation instructions](../../install.md).

    -   [X] Install Chaos Toolkit

        If you haven’t installed Chaos Toolkit yet, follow the
        [installation instructions](https://chaostoolkit.org/reference/usage/install/).

## Run with the Chaos Toolkit fault Extension

-   [X] Install the {==chaostoolkit-fault==} extension

    ??? note

        Chaos Toolkit extensions are Python libraries that must be found by the
        `chaos` process when it runs. Usually, this requires you install these
        extensions as part of your [Python environment][pypa]. There are many
        ways to get a Python environment, so we'll assume you are running one.

    Install the [chaostoolkit-fault][ctkfault] extension:

    === "pip"

        ```bash
        pip install chaostoolkit-fault
        ```

    === "uv"

        ```bash
        uv tool install chaostoolkit-fault
        ```

-   [X] Add an action to run the proxy

    You can now add the following to one of your experiment:

    === "json"

        ```json
        {
            "type": "action",
            "name": "run fault proxy with a normal distribution latency",
            "provider": {
                "type": "python",
                "module": "chaosfault.actions",
                "func": "run_proxy",
                "arguments": {
                    "proxy_args": "--with-latency --latency-mean 300 --latency-stddev 50 --upstream '*'"
                }
            },
            "background": true
        }
        ```

    === "yaml"

        ```yaml
        ---
        type: action
        name: run fault proxy with a normal distribution latency
        provider:
            type: python
            module: chaosfault.actions
            func: run_proxy
            arguments:
                proxy_args: "--with-latency --latency-mean 300 --latency-stddev 50 --upstream '*'"
        background: true
        ```

    You mostly likely want to run the proxy as a background task of the
    experiment.

    The `proxy_args` argument takes the full list of supported values from the
    [cli run command](../reference/cli-commands.md#run-command-options)

-   [X] Add an action to stop the proxy

    You can now add the following action once your experiment is done with
    the proxy.

    === "json"

        ```json
        {
            "type": "action",
            "name": "stop latency proxy injector",
            "provider": {
                "type": "python",
                "module": "chaosfault.actions",
                "func": "stop_proxy"
            }
        }
        ```

    === "yaml"

        ```yaml
        ---
        type: action
        name: stop latency proxy injector
        provider:
            type: python
            module: chaosfault.actions
            func: stop_proxy
        ```

    !!! tip

        You can do without this action if you set the `duration` argument when
        you start the proxy. In which case, the proxy will terminate on its
        own after the duration is up.

## Next Steps

- Explore how you can use the [Reliably Platform](run-with-reliably.md) to
  orchestrate and schedule your experiment on a variety of targets.