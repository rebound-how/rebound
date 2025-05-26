---
layout: ~/layouts/DocsLayout.astro
title: Deployments
description: Deployments allow you to run Chaos Toolkit chaos engineering experiments in your environment
---

Deployments are your way of telling Reliably how [plans](/docs/concepts/plans/) should be run and declaring required information.

## Deployment types

There are three types of deployment, each one associated with a way of running experiments.

| Deployment type | Usage |
| ----------------|-------|
| GitHub          | Reliably will run your plan as a GitHub Action in a GitHub workflow |
| Reliably CLI Managed   | Reliably will run your plan locally to the server |
| Reliably CLI Manual    | You will use the Reliably CLI to run your plan in your own environment, such as a CI/CD pipeline |
| Docker      | Reliably will run your plan in a local Docker container |
| Kubernetes      | Reliably will run your plan in your Kubernets cluster as a Kubernetes Job/CronJob |

The [How it Works](/docs/how-it-works/) page presents flowcharts for a more detailed view of the differences between running a plan with Reliably Cloud, GitHub, or the Reliably CLI.

## Create a deployment

### Reliably CLI (Managed)

Creating a Reliably CLI (Managed) deployment will allow you to delegate running your plans entirely to Reliably.

<div class="markdown-tip">

Read more about the [architecture reference for Reliably CLI Managed deployment](/docs/how-it-works/#reliably-cli-managed).
</div>

<p><img src="/images/docs/concepts/deployments/reliably-new-deployment-cli-managed.png" with="487" alt="A screenshot of the Reliably App, displaying the form the create a new Reliably CLI Managed deployment." width="490" /></p>

Creating a Reliably CLI Managed deployment requires the following information:

- A deployment name, which must be unique to your Reliably organization.
- The deployment type must be set to 'Reliably CLI'.
- The execution mode must be set to 'Managed'.

Optionally, please provide:

- A directory where to run the plan from. If this directoy exists, it may contain additional dependencies.
- The Python version to use during the run.
- A `requirements.txt` content for dependencies to be installed on-the-fly.

### Reliably CLI (Manual)

Reliably CLI deployments are used to run plans with the Reliably CLI. Using the Reliably CLI allows you to run experiments from anywhere in your system.

<div class="markdown-tip">

Read more about the [architecture reference for Reliably CLI deployment](/docs/how-it-works/#reliably-cli-manual).
</div>

<p><img src="/images/docs/concepts/deployments/reliably-new-deployment-cli.png" with="487" alt="A screenshot of the Reliably App, displaying the form the create a new Reliably CLI deployment." width="490" /></p>

Creating a Reliably CLI deployment requires the following information:

- A deployment name, which must be unique to your Reliably organization.
- The deployment type must be set to 'Reliably CLI'.
- The execution mode must be set to 'Manual'.

<div class="markdown-tip">

A Reliably CLI Manual deployment must be triggered by yourself, or an external
process. A Plan using this deployment type exists but does not automatically
run unless called.

</div>

### Docker

Creating a Docker deployment will allow Reliably to manage Docker containers
on your behalf.

<div class="markdown-tip">

Read more about the [architecture reference for Reliably CLI Managed deployment](/docs/how-it-works/#docker).
</div>

<p><img src="/images/docs/concepts/deployments/reliably-new-deployment-docker.png" with="487" alt="A screenshot of the Reliably App, displaying the form the create a new Docker  deployment." width="490" /></p>

Creating a Reliably Docker deployment requires the following information:

- A deployment name, which must be unique to your Reliably organization.
- The deployment type must be set to 'Docker'.
- The container image which entry point is the Reliably CLI.


### Kubernetes

Kubernetes deployments are used to run plans from any Kubernetes cluster directly.

<div class="markdown-tip">

Read more about the [architecture reference for Reliably Kubernetes deployment](/docs/how-it-works/#kubernetes).
</div>

<p><img src="/images/docs/concepts/deployments/reliably-new-deployment-kubernetes.png" with="487" alt="A screenshot of the Reliably App, displaying the form the create a new Reliably Kubernetes deployment." width="490" /></p>

Creating a Reliably Kubernetes deployment requires the following information:

- A deployment name, which must be unique to your Reliably organization.
- The deployment type must be set to 'Reliably Kubernetes'.
- The namespace where to create the Kubernetes resources.
- The image exposing the [Reliably CLI](/docs/cli) as an entrypoint and no command arguments when using the default manifest.
- Either use a default Kubernetes Pod manifest to run the plan.
  Or, your own Kubernetes Pod manifest. The first container of the manifest must be using the image that will run the Reliably CLI.
- The Kubernetes credentials to connect to the cluster.

A few notes:

- You must create a Service Account in the target namespace. This service
  account will be attached to the Kubernetes Pod running the Plan
  ```yaml
    ---
    kind: ServiceAccount
    apiVersion: v1
    metadata:
        namespace: default
        name: reliably-job
    labels:
        app.kubernetes.io/name: reliably-job
    automountServiceAccountToken: false
    ```
- Make sure to bind the roles matching the expected operations carried by
  the Experiment.
- Reliably will create either Kubernetes Job or a Kubernetes Cron Job
  depending on if the plan uses a CRON schedule or not
- The Kubernetes Job/CronJob will then create the appropriate Kubernetes Pod
  to run the Plan
- The following labels will be set on the Kubernetes Job and Pod:
  * `reliably.com/plan` set to the Reliably Plan identifier
  * `reliably.com/org` set to the Reliably Organization
  * `app.kubernetes.io/managed-by` set to `reliably`
  * `app.kubernetes.io/component` set to `experiment`
  * `app.kubernetes.io/name` set to `plan-<PLAN_ID>`
- For AWS EKS clusters:
  - Reliably supports authenticating with the
[aws-iam-authenticator](https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html).
  - Your credentials configuration must include the `AWS_ACCESS_KEY_ID` and 
    `AWS_SECRET_ACCESS_KEY` properties set in the `users.user.exec.env` section

### GitHub

<p>Creating a GitHub deployment will allow Reliably to create <a href="https://docs.github.com/en/actions" target="_blank" rel="noopener noreferer">GitHub Workflows <span class="screen-reader-text">External link will open in a new tab</span></a> on your behalf. These GitHub Workflows will then be used to install all the dependencies necessary to run the experiments on-demand, according to your <a href="/docs/concepts/plans/">plans</a>.</p>


<div class="markdown-tip">

Read more about the [architecture reference for GitHub deployment](/docs/how-it-works/#github-workflows).
</div>

<p><img src="/images/docs/concepts/deployments/reliably-new-deployment-github.png" with="487" alt="A screenshot of the Reliably App, displaying the form the create a new GitHub deployment." width="490" /></p>

Creating a GitHub deployment requires the following information:

- A deployment name, which must be unique to your Reliably organization.
- The deployment type must be set to 'GitHub'.
- A GitHub repository, in the form of a **full** URL for the repository. _Example: github.com/my-org/my-repo_.
- The name of the GitHub environment for this repository where your secrets are stored. Environements are available in the 'Settings' section of the repository, and only available to repository collaborators with the right permissions.
- A <a href="https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token" target="_blank" rel="noopener noreferer">GitHub Token <span class="screen-reader-text">External link will open in a new tab</span></a> to access the repository.
