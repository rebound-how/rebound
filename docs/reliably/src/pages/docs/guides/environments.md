---
layout: ~/layouts/DocsLayout.astro
title: Use Reliably Environments
description: Overview of creating and using Reliably Environments.
---

This guide goes into the details of creating and using Reliably environments
to inject contexts into your Reliably Plans.

Reliably Experiments describe a set of activities to conduct. These activities
are usually context-dependent. For instance, a given experiment may be designed
to work against Kubernetes. You would expect that such an experiment can target
any Kubernetes cluster that you run, therefore credentials should not be
embedded into the experiment.

This is where Reliably Environments come into play. They allow you to declare
a set of environment variables and secrets that you can attach to a Reliably
Plan for a particular run of an Experiment. Thus providing the context it needs.

## The Basics

### Create an Environment

To create an environment, go to the `New environment` page and start filling out
the form as needed.

Provide a name that you can easily recall what it covers later on. Then set
as many environment variables and secrets, which are encrypted internally,
 as you need.


<div class="markdown-tip">

When creating a secret as a file, the path must start with `/home/svc`.

</div>

### Delete an Environment

You can delete environments at will but only when all Reliably Plan that
use them have also been deleted first. This prevents mistakes where a Plan
tries to run and cannot find its Environment.

## Common Patterns

This section will introduce common Environment patterns that will help you
pass the right context to a variety of experiments.

These patterns apply to any Reliably Deployment type. But you declare these
variables and secrets in Reliably only when using a Reliably Cloud
deployment. Otherwise, these variables and secrets are declared directly
on the platform you use to execute Reliably Plans.

### Kubernetes

Experiments targetting Kubernetes clusters usually require a service account that will define the Kubernetes API server endpoint and credentials to
authenticate to it. The service account should then have the right roles to
perform the experiment's activities, using the least privileges approach.

<p><img src="/images/docs/guides/setup-environments/k8s.png" alt="A screenshot of the Reliably Kubernetes environment form." width="655" /></p>


| Type                 | Name                     | Value |
| -------------------- | ------------------------ | ----- |
| Environment Variable | `KUBECONFIG`             | `/tmp/config` |
| Secret File          | `/tmp/config` | The content of a Kubernetes Service Account file |


<div class="markdown-tip">

Leave the `KUBECONFIG` variable to its default value in most cases.
</div>

<div class="markdown-tip">

If you experiment is targetting a Google Cloud GKE cluster and you run
it from Reliably Cloud, your `kubeconfig` should not use the
`gke-gcloud-auth-plugin` authentication approach as the
`GOOGLE_APPLICATION_CREDENTIALS` environment variable 
cannot be set in Reliably Cloud.

Instead, modify your `kubeconfig` to use a regular `token` approach instead.

For instance:

```
$ kubectl config set-credentials default --token=$(gcloud auth print-access-token)
$ kubectl config set-context <CLUSTER NAME> --user=default
```

If you target a GKE cluster and run from GCP resources (GKE itself, Cloud Run)
you will have to follow that approach until
[this issue](https://github.com/kubernetes/cloud-provider-gcp/issues/654)
is taken into account by upstream. Note that, tokens have a default lifetime
of `3600s` only so you will have to regularly update the credentials.

If you target a GKE cluster but run the experiment from anywhere else, feel free
to keep the `gke-gcloud-auth-plugin` authentication approach as described
in the
[GCP documentation](https://cloud.google.com/kubernetes-engine/docs/how-to/api-server-authentication).
</div>



### AWS

Experiments targeting AWS resources usually require enough information to
authenticate.

<p><img src="/images/docs/guides/setup-environments/aws.png" alt="A screenshot of the Reliably AWS environment form." width="655" /></p>

| Type                 | Name                         | Value |
| -------------------- | ---------------------------- | ----- |
| Environment Variable | `AWS_REGION`                 | A valid AWS region |
| Secret Variable      | `AWS_ACCESS_KEY_ID` | The AWS access key for the AWS account to use |
| Secret Variable      | `AWS_SECRET_ACCESS_KEY` | The AWS secret key for the AWS account to use |

Alternatively, you can only use a secret file as well:

| Type                 | Name                         | Value |
| -------------------- | ---------------------------- | ----- |
| Environment Variable | `AWS_REGION`                 | A valid AWS region |
| Secret File          | `/home/svc/.aws/credentials` | The content of an [shared credentials file](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#shared-credentials-file) |

### Google Cloud Platform

Experiments targetting GCP services usually require a service account, which
should have the right roles to perform the experiment's activities.

<p><img src="/images/docs/guides/setup-environments/gcp.png" alt="A screenshot of the Reliably Google Cloud Platform environment form." width="655" /></p>

| Type                 | Name                             | Value |
| -------------------- | -------------------------------- | ----- |
| Environment Variable | `GOOGLE_APPLICATION_CREDENTIALS` | `/home/svc/gcp.json` |
| Secret File          | `/home/svc/gcp.json`             | The content of a GCP Service Account key file |


### Azure

Experiments targeting Azure services requires a
[set of values](https://learn.microsoft.com/en-us/azure/azure-portal/get-subscription-tenant-id)
to authenticate with the right Azure endpoint and services.

<p><img src="/images/docs/guides/setup-environments/azure.png" alt="A screenshot of the Reliably Azure environment form." width="655" /></p>

| Type                    | Name                             | Value |
| ----------------------- | -------------------------------- | ----- |
| Azure Client ID         | `AZURE_CLIENT_ID`                |       |
| Azure Tenant ID         | `AZURE_TENANT_ID`                |       |
| Azure Subscription ID   | `AZURE_SUBSCRIPTION_ID`          |       |
| Azure Client Secret     | `AZURE_CLIENT_SECRET`            |       |

### GitHub

Experiments targetting GitHub services require a token with the appropriate
permissions for the experiments in the Reliably Plan.

<p><img src="/images/docs/guides/setup-environments/github.png" alt="A screenshot of the Reliably GitHub environment form." width="655" /></p>

| Type                 | Name                             | Value |
| -------------------- | -------------------------------- | ----- |
| Secret Variable      | `GITHUB_TOKEN`                   | The token value |

<div class="markdown-tip">

The token must have enough permissions for the experiment to perform its operations.
</div>

