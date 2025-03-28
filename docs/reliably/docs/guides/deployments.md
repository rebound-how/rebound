# Runtime Deployments

This guide goes into the details of creating and using Reliably deployments
to execute your Reliably Plans.

## The Basics

### Create a Deployment

To create a deployment, go to the {==New deployment==} page and start filling
out the form as needed.

Provide a name that you can easily recall what it covers later on. Then pick up
a deployment target.

### Delete a Deployment

You can delete deployments at will but only when all Reliably Plan that use them
have also been deleted first. This prevents mistakes where a Plan tries to run
and cannot find its Deployment.

## Supported Deployment Targets

This section will introduce Reliably's supported Deployment targets.

### Reliably CLI Manual Mode

The most basic deployment is {==Reliably CLI==} in {==manual mode==}.
This deployment relies on running the [Reliably CLI](../tutorials/install/cli.md)
by your own means. This is useful when you want to control the execution's
orchestration from Reliably.

<p align=center><img src="/assets/images/guides/setup-deployments/cli-manual.png" alt="A screenshot of the Reliably CLI deployment form." width="655" /></p>

In manual, mode, you are responsible to execute the CLI from wherever your
environment requires. For instance:

```bash
reliably service plan execute bde0c9ce-4a91-492a-8e7c-19060e19232e  # (1)!
```

1. The UUID is the plan identifier found on Reliably.

When running the CLI, you need to set the following environment variables:

* `RELIABLY_SERVICE_HOST`: the http address of the platform
* `RELIABLY_SERVICE_TOKEN`: the access token to authenticate with the platform
* `RELIABLY_ORGANIZATION_ID`: the UUID of the organization where the plan lives

### Reliably CLI Managed Mode

!!! info "Install `uv`"

    To benefit from the managed mode, you must install
    [uv](https://docs.astral.sh/uv/) on the machine.

The {==managed mode==} of the {==Reliably CLI==} leaves the responsability to
the Reliably platform to run Reliably Plans on the same machine where the server
runs, as a subprocess.

<p align=center><img src="/assets/images/guides/setup-deployments/cli-managed.png" alt="A screenshot of the Reliably CLI deployment form." width="655" /></p>


| Parameter            | Value |
| -------------------- | ----- |
| Execution Directory  | A directory accessible by the user running Reliably. Leave empty for a temporary directory to be set by Reliably instead |
| Python Environment   | The Python to use to run the Reliably CLI. If not present, it will be downloaded and installed on the machine via `uv` |
| Python Dependencies  | The content of [requirements.txt](https://pip.pypa.io/en/stable/reference/requirements-file-format/#) file to be installed on the fly |

### Docker

The {==Docker==} deployment target runs Reliably Plans locally to the
platform's server inside Docker containers.

<p align=center><img src="/assets/images/guides/setup-deployments/docker.png" alt="A screenshot of the Docker deployment form." width="655" /></p>

| Parameter            | Value |
| -------------------- | ----- |
| Docker Image  | The name of a container image that exposes the Reliably CLI as its entry point |

The image's entrypoint must be the Reliably CLI. We provide an
[image](https://github.com/rebound-how/rebound/pkgs/container/reliably-job) with
most common dependencies:

```bash
docker pull ghcr.io/rebound-how/reliably-job:latest
```

If you need to adjust the image, please use this
[Dockerfile](https://github.com/rebound-how/rebound/blob/main/deploy/docker/job/Dockerfile)
as a baseline.

### Kubernetes

The {==Kubernetes==} deployment target runs Reliably Plans in the cluster of
your choice as a [Kubernetes Job](https://kubernetes.io/docs/concepts/workloads/controllers/job/).

<p align=center><img src="/assets/images/guides/setup-deployments/k8s.png" alt="A screenshot of the Kubernetes deployment form." width="655" /></p>

| Parameter            | Value |
| -------------------- | ----- |
| Namespace  | The namespace where to deploy the Job |
| Image  | The name of a container image that exposes the Reliably CLI as its entry point |
| Default Manifest  | Reliably has its own manifest when deploying the job. You can use this flag to pass your own manifest instead |
| In-cluster Credentials  | Kubernetes client credentials as a YAML document. If you flip this flag, Reliably will use the mounted credentials for the job |

We provide an
[image](https://github.com/rebound-how/rebound/pkgs/container/reliably-job) with
most common dependencies.

??? note "A few things to note"

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
          of the Kubernetes credentials

You must create a Service Account in the target namespace. This service
account will be attached to the Kubernetes Pod running the Plan

```yaml  title="reliably-service-account.yaml"
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

```bash
kubectl apply -f reliably-service-account.yaml
```

Make sure to bind the roles matching the expected operations carried by
the Experiment.

For instance, say your Experiment requires to delete a pod, here is what
such a role binding could look like:

```yaml  title="reliably-rbac.yaml"
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: reliably
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["list", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: reliably-binding
  namespace: default
subjects:
- kind: ServiceAccount
  name: reliably-job
  namespace: default
roleRef:
  kind: Role
  name: reliably
  apiGroup: rbac.authorization.k8s.io
```



### GitHub

The {==GitHub==} deployment target runs Reliably Plans in a
[Github Workflow](https://docs.github.com/en/actions/writing-workflows).

<p align=center><img src="/assets/images/guides/setup-deployments/github.png" alt="A screenshot of the Github deployment form." width="655" /></p>

| Parameter            | Value |
| -------------------- | ----- |
| Repository  | The repository full URL, for instance `https://github.com/myorg-myrepo` |
| Branch  | The name of the branch to workflow the changes to |
| Username  | Username to perform the commit |
| Token  | A personal token to perform the commit |

The token must be set with the following [permissions](https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens?apiVersion=2022-11-28):

* Workflows: Repository permissions (read/write)
* Actions: Repository permissions (read/write)
* Contents: Repository permissions (read/write)

Reliably will create a GithUb workflow on the fly and commit it to the
given branch as a file named `.github/workflows/reliably-plan-[PLAN_ID].yaml`
where the `[PLAN_ID]` is the UUID of the plan to executed. The template
for that workflow is as follows:

```yaml
name: Execute a Reliably Plan

on:

jobs:
  execute-reliably-plan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: rebound-how/actions/reliably@main
```

If you need to perform operations before or after Reliably, you may use your
own template by having a workflow file `.github/workflows/reliably-plan.yaml`
in the repository. If found by Reliably in that branch it will be used instead
of the default template.

Use the official [Github action](https://github.com/rebound-how/actions) to run
the plan.
