# About Deployments

Reliably Deployments are at the heart of your experience with Reliably. They
are responsible for executing Reliably Plans.

Reliably provides a variety of approaches to fit your requirements.

## Strategies

Running Reliably experiments should have the following properties:

* Simple
* Customizable
* Secure

These facets create the confidence needed by engineering teams to onboard
tools such as Reliably. Let's see what this means for each deployment
approach provided by Reliably natively.

### GitHub

GitHub deployment is interesting when you want to have more customization
power while also keeping your environment's data secured outside of Reliably.

Regarding security, the idea is that you can store your data (secrets and
environment variables) into GitHub Environment directly. They never have
to be seen or stored in Reliably. You can then apply the best practices
that GitHub suggests for access to these environments.

Reliably offers a strategy for greater customization of your GitHub deployment
as well by letting you declare the GitHub Workflow to be applied when a Reliably
Plan is scheduled.

### Reliably CLI

The Cloud and GitHub deployments focuses mainly on making the experience of
running Reliably Plan as straightforward as possible. Yet, sometimes you might
need full control of the runtime environment and they might not be appropriate.

In that case, you can fallback on the Reliably CLI which can run anywhere from
your system, as long as Python is available.

## Customizing Execution Context

### GitHub

The GitHub Deployment approach is to commit and push a GitHub Workflow into the
repository that you provide. The worflow is configured as follows:

* Scheduled to run either directly on its own push event or on a periodic
schedule using a CRON pattern, as supported by GitHub
* Uses the Reliably GitHub Plan action to install the required dependencies
* Sets the GitHub Environment name to get access to environment variables and
  secrets in that repository
* Sets a variety of Reliably environment variable used for metadata purpose
* Upon completion, the Workflow also commits and pushes the result files from
  the execution into the repository itself under the directory
  `plans/<plan-id>`

You may configure almost the entire context by providing your own GitHub
base workflow that Reliably will load before it amends, commits and pushes it
to the repository. For instance, a basic GitHub Workflow could look like:

```yaml
name: Execute a Reliably Plan

on:

jobs:
  execute-reliably-plan:
    runs-on: ubuntu-22.04
    steps:
    - uses: actions/checkout@v3
    - uses: reliablyhq/actions/plan@main
```

When providing your own GitHub Workflow, make sure to name it
`reliably-plan.yaml` so Reliably finds it in your repository.

You can change anything in such a workflow except for the step
using `reliablyhq/actions/plan` as that step will be extended
by Reliably to add additional metadata as environment variables. None of which
are sensitive.

This therefore allows you to taylor a plan runtime context entirely to your
own unique requirements while retaining the convenience of the single-click
GitHub deployment.

Your workflow is treated as a template by Reliably. It is read and amended by
the changes are committed and pushed as an entire new workflow file into the
repository, unique to a single Reliably Plan run.

The workflow expects a GitHub token with the following permissions:

* Read: Environments
* Read & Write: Actions, Commit Statuses, Contents, Workflows

### Reliably CLI

The Reliably CLI is your friend whenever your requirement prevent you from
using the Reliably Cloud or GitHub deployment strategies.

Essentially, this comes down to running a command such as:

```console
reliably service plan execute <plan-id>
```

The command will collect, from Reliably, the plan and its associated pieces
such as the experiments to run and integrations to enable.

If your experiment requires specific environment variables, just mae sure they
are accessible to the process when it starts.

This makes this solution great to run from CI other than GitHub for instance.
