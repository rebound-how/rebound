---
layout: ~/layouts/DocsLayout.astro
title: Get Started In Running From Your Terminal
description: Overview of using Reliably to run from your terminal.
---

This guide goes into the details about using Reliably from a terminal.

While Reliably offers many native options to execute experiments. It is
sometimes necessary to run from locations Reliably does not yet support. To
still get the benefits of the platform features, Reliably provides an approach
via the Reliably CLI.

## Create a Reliably CLI Deployment

The first step is to create a deployment of type "Reliably CLI".

<img src="/images/docs/guides/get-started-with/terminal/create-deployment-reliably-cli.png" width="427" height="382" alt="The Deployment form to create a Reliably CLI deployment" />

## Use the Reliably CLI Deployment from the Plan

Create a new plan and select your new Reliably CLI deployment. This will
instruct Reliably to create the plan resources WITHOUT launching it.

<img src="/images/docs/guides/get-started-with/terminal/new-plan.png" width="427" height="382" alt="Create a plan with the new Deployment" />

## Ensure your Reliably CLI is properly installed and configured

Before you can run the plan yourself, you need to [install](/docs/cli/#install)
and [configure](/docs/cli/#authenticate) it. Essentially, make sure to set the
Reliably organization id and your authentication token so the CLI can
communicate with the platform.

```bash
pip install reliably-cli
```

## Install the Experiment Dependencies

The Reliably CLI package does not install all the necessary dependencies for
the experiment to run. You need to install them yourself with a Python
package installer such as `pip`.

For instance, you can use the following command to install the most
[common dependencies](https://github.com/reliablyhq/cli/blob/main/pyproject.toml#L49C1-L49C13):

```bash
pip install reliably-cli[chaostoolkit]
```

## Execute the Plan

Once the CLI is installed and configured, you can now run your plan with the
command given on the Plan page:

<img src="/images/docs/guides/get-started-with/terminal/reliably-cli-command.png" alt="Reliably CLI command line" />

```bash
reliably service plan execute <PLAN_ID>
```

If your Plan is using an environment, then use it as follows:

```bash
reliably service plan execute --load-environment <PLAN_ID>
```
