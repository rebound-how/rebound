# Reliably CLI

!!! Question "Is the CLI mandatory?"

    The __Reliably CLI is not a required step__ to enjoy Reliably. Indeed, you
    can perform all activities through the Reliably Platform directly.

    The CLI is useful when your environment is terminal-based, such as a CI
    platform.

    In a nutshell, if you are only getting started, you can safely skip this
    guide.




## Install

This guide explains the streamlined process of installing the Reliably CLI and
taking the first steps to incorporate reliability feedback loop into your
current workflow.

!!! warning

    To use the Reliably CLI, you will need to first
    [create an account](../../account.md) with your Reliably Platform.

### As a Python Package

The Reliably CLI is installed as a regular Python package. It requires
Python 3.10+

=== "Using `uv`"

    ```bash
    uv tool install --python python3.12 reliably-cli
    ```

    This will install the `reliably` binary in your `$HOME/.local/bin` directory.

=== "Using your system `pip`"

    ```bash
    python3 -m pip install --user reliably-cli
    ```

    This will install the `reliably` binary in your `$HOME/.local/bin` directory.

To ensure that everything is working, you can use `reliably version` in a new
terminal window:

```bash
reliably version
```

```text
Reliably CLI version x.x.x
```

Now you're all set to [configure](#configure) your CLI.

## Configure

The Reliably CLI can be configured via a file, environment variables or a mix
of both. In that case, environment variables override any configuration file
entry.

### Initialize new Configuration

You can initialize a configuration file as follows:

```bash
reliably config init
```

This will prompt for a valid {==token==}
and will list {==organizations==}
you belong to.

### View current Configuration

You can view the current configuration:

```bash
reliably config view
```

You can obtain the path to the configuration file with:

```bash
reliably config path
```

## Authenticate

<div class="markdown-tip">

You do not need to set the following variables if you have initialized the
configuration via `reliably config init`.
</div>

When running the CLI requires to be authenticated with the `[service] token`
configuration entry or `RELIABLY_SERVICE_TOKEN` environment variable.

Using the environment variable overriddes the token stored into the
configuration file.

```bash
export RELIABLY_SERVICE_TOKEN=6ccfdxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

You can create or retrieve a token from the {==settings==} page.

You can also override the Reliably organization via the
`RELIABLY_ORGANIZATION_ID` environment variable.

```bash
export RELIABLY_ORGANIZATION_ID=<UUID>
```

The organization id can be found on your {==profile page==}.

## What's next?

- [Execute a plan from your Terminal](../../guides/get-started-with/terminal.md)
