# Execute Scenarios From GitHub Action

This guide will walk you through integrating <span class="f">fault</span> into your GitHub pipeline.

## What You'll Achieve

You will learn how to run a <span class="f">fault</span> scenario as part of your GitHub workflow
and use the result to fail a GitHub job.

!!! example "Start your application first"

    The guides below do not show how to run the target service from within
    your workflow. For instance, you could run a step like this first:

    ```yaml
      - name: Run application under test in the background
        shell: bash
        run: RUNNER_TRACKING_ID="" && (nohup ./my-app &)
    ```

## Run <span class="f">fault</span>'s scenario

The basic approach to run <span class="f">fault</span> scenarios in your GitHub workflows is to
use the dedicated [action](https://github.com/rebound-how/actions).

-   [X] Run <span class="f">fault</span>'s scenario

    ```yaml title=".github/workflows/reliability.yaml"
    name: Run fault scenarios

    on:
      workflow_dispatch:

    jobs:
      run-reliability-scenarios:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4

          - uses: rebound-how/actions/fault@main  # (1)!
            with:
              scenario: scenario.yaml  # (2)!
    ```

    1. Add the fault [action](https://github.com/rebound-how/actions)
    2. Path to a [scenario file](../../tutorials/create-scenario.md) or a directory containing scenario files

## Create an issue when at least one test failed

-   [X] Run <span class="f">fault</span>'s scenario

    ```yaml title=".github/workflows/reliability.yaml"
    name: Run fault scenarios

    on:
      workflow_dispatch:

    jobs:
      run-reliability-scenarios:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4

          - uses: rebound-how/actions/fault@main  # (1)!
            with:
              scenario: scenario.yaml  # (2)!
              report: report.md  # (3)!
              create-issue-on-failure: "true"  # (4)!
              github-token: ${{ secrets.GITHUB_TOKEN }}  # (5)!
    ```

    1. Add the <span class="f">fault</span> [action](https://github.com/rebound-how/actions)
    2. Path to a [scenario file](../../tutorials/create-scenario.md) or a directory containing scenario files
    3. Export the report as a markdown document as it will be used as the body of the issue
    4. Tell the action to create the issue if at least one test failed
    5. Provide the github token so the operation is authenticaed appropriately. Make sure the token has [write permissions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication#modifying-the-permissions-for-the-github_token)
