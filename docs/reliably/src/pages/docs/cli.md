---
layout: ~/layouts/DocsLayout.astro
title: CLI
description: Configure your CLI to execute Reliably plans and more.
---

<div class="markdown-tip">
To use the Reliably CLI, you will need to first
<a href="/docs/account">create an account</a>
with Reliably.
</div>

<div class="markdown-tip">

The Reliably CLI is not a mandatory step to enjoy Reliably. Indeed, you
can perform all activities through the Reliably Cloud dashboard directly.

The CLI is useful when your environment prohibits execution from the Reliably
cloud.

In a nutshell, if you are only getting started, you can safely skip this
guide.

</div>

## Install

This guide explains the streamlined process of installing the Reliably CLI and
taking the first steps to incorporate reliability feedback loop into your
current workflow.

### Using `pip`

The Reliably CLI is installed as a regular Python package. It requires
Python 3.10+

Install it as follows:

```bash
python3 -m pip install --user reliably-cli
```

This will install the `reliably` binary in your `$HOME/.local/bin` directory.

To ensure that everything is working, you can use `reliably version` in a new
window:

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

This will prompt for a valid token
and will list organizations
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

You can create or retrieve a token from the `Settings` page.

You can also override the Reliably organization via the
`RELIABLY_ORGANIZATION_ID` environment variable.

```bash
export RELIABLY_ORGANIZATION_ID=<UUID>
```

The organization id can be found on your `Profile page`.

## What's next?

- [Execute a plan from your Terminal](/docs/guides/get-started-with/terminal/)
