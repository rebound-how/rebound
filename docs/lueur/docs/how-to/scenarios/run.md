# Run lueur Scenarios

In this guide, you will learn how to run lueur scenarios and read the generated
report.

??? abstract "Prerequisites"

    -   [X] Install lueur

        If you haven’t installed lueur yet, follow the
        [installation instructions](../install.md).

    -   [X] Generate Scenario Files

        If you haven’t created a scenario file, please read this
        [guide](./generate.md).


## Run a Scenario File

We will explore now how to run scenarios generated to verify the resilience of
the lueur demo application itself.

-   [X] Start demo application provided by lueur

    ```bash
    lueur demo run  # (1)!
    ```

    1. The application under test must be started for the scenario to be
       meaningful. Otherwise, the scenarios will all fail.

-   [X] Run a scenario file

    ```bash
    lueur scenario run --scenario scenario.yaml
    ```

## Run Many Scenario Files

We will explore now how to run scenarios generated to verify the resilience of
the lueur demo application itself. In this specific use case, we assume you want
to run many scenario files at once and that they are located in the
same directory.

-   [X] Start demo application provided by lueur

    ```bash
    lueur demo run  # (1)!
    ```

    1. The application under test must be started for the scenario to be
       meaningful. Otherwise, the scenarios will all fail.

-   [X] Run scenario files located in a directory

    ```bash
    lueur scenario run --scenario scenarios/  # (1)!
    ```

    1. lueur will load all YAML files in that directory.

## Next Steps

- Learn how to explore the generated [report](./reporting.md) from running these scenarios.
- Explore the [specification reference](../../reference/scenario-file-format.md)
  for scenarios.
