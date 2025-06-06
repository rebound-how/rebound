# Run <span class="f">fault</span> Scenarios

In this guide, you will learn how to run <span class="f">fault</span> scenarios and read the generated
report.

??? abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span>

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../install.md).

    -   [X] Generate Scenario Files

        If you haven’t created a scenario file, please read this
        [guide](./generate.md).


## Run a Scenario File

We will explore now how to run scenarios generated to verify the resilience of
the <span class="f">fault</span> demo application itself.

-   [X] Start demo application provided by <span class="f">fault</span>

    ```bash
    fault demo run  # (1)!
    ```

    1. The application under test must be started for the scenario to be
       meaningful. Otherwise, the scenarios will all fail.

-   [X] Run a scenario file

    ```bash
    fault scenario run --scenario scenario.yaml
    ```

## Run Many Scenario Files

We will explore now how to run scenarios generated to verify the resilience of
the <span class="f">fault</span> demo application itself. In this specific use case, we assume you want
to run many scenario files at once and that they are located in the
same directory.

-   [X] Start demo application provided by <span class="f">fault</span>

    ```bash
    fault demo run  # (1)!
    ```

    1. The application under test must be started for the scenario to be
       meaningful. Otherwise, the scenarios will all fail.

-   [X] Run scenario files located in a directory

    ```bash
    fault scenario run --scenario scenarios/  # (1)!
    ```

    1. <span class="f">fault</span> will load all YAML files in that directory.

## Run a Scenario on Kubernetes

The default behavior is to execute a scenario locally to where the command
is started. A scenario offers a way to run the proxy [from within a Kubernetes
cluster](../../reference/scenario-file-format.md#running-on-a-platform).

-   [X] Configure the scenario to run on a Kubernetes cluster

    ```yaml
    context:
      runs_on:
        platform: kubernetes
        ns: default  # (1)!
        service: nginx  # (2)!
    ```

    1. The namespace of the target service
    2. The target service which should be part of the test chain

    The scenario will be executed locally but the proxy will be deployed inside
    the cluster directly.

## Next Steps

- **Learn how to explore the generated [report](./reporting.md)** from running these scenarios.
- **Explore the [specification reference](../../reference/scenario-file-format.md)**
  for scenarios.
