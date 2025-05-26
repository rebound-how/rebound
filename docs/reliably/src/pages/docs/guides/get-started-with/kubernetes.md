---
layout: ~/layouts/DocsLayout.astro
title: Get Started With Kubernetes
description: Overview of using Reliably to verify Kubernetes.
---

This guide goes into the details about using Reliably in a Kubernetes context.

Reliably can use your Kubernetes ecosystem in two fashions:

1. Target Kubernetes from your experiments. In this case, your use Reliably
   to perform actions against your Kubernetes clusters in a Chaos Engineering
   way.
2. Use Kubernetes to run Reliably Plans. In that case, Reliably schedules
   its plans to run from a Kubernetes cluster. Experiments carried by these
   plans do not necessarily target a Kubernetes cluster itself. Here, Reliably
   orchestrates plans by using your cluster as a distributed workload system.

These two modes can work together, meaning you can run a Reliably experiment
that target the cluster on which the experiment is being executed on.

## Kubernetes as a Target System for Experiments

Reliably offers a
[large set of actions and probes](https://reliably.com/activities/?t=chaosk8s) 
focused on Kubernetes.

Once you have put up together an experiment that you are happy with, you can
run it against your Kubernetes cluster via a Reliably plan. When setting up the
plan, you only need to select an
[Environment](/docs/guides/environments/#kubernetes) that declares environment
variables and secrets allowing Reliably to connect with the Kubernetes API
server.

<p><img src="/images/docs/guides/get-started-with/kubernetes/env.png" alt="A screenshot of the Reliably Kubernetes environment form." width="655" /></p>

When you create the plan to run an experiment targeting a Kubernetes cluster,
make sure to select the correct environment so Reliably knows how to connect
and authenticate with the Kubernetes API server.

<p><img src="/images/docs/guides/get-started-with/kubernetes/plan.png" alt="A screenshot of the Reliably Kubernetes plan form." width="655" /></p>



<div class="markdown-tip">

Make sure to give the service account the right RBAC for the experiment. For
instance, if the experiment needs to delete a pod, make sure the service
account is associated with a role that has that permission.
</div>

## Distribute Reliably Plans on Kubernetes

Running Reliably Plan can occur on your Kubernetes cluster instead of from
Reliably Cloud. To do so, you must create a
[Deployment](/docs/concepts/deployments/#kubernetes) and use it when creating
a Reliably Plan.


<p><img src="/images/docs/guides/get-started-with/kubernetes/deployment.png" alt="A screenshot of the Reliably Kubernetes deployment form." width="655" /></p>

The container image needs to use the [Reliably CLI](/docs/cli/)
as its entrypoint so Reliably can invoke it to execute the plan.

The credentials are passed as a service account which requires the roles to
create [Kubernetes Job](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
and/or
[Kubernetes CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/).

Once created, you can schedule Reliably plans onto that cluster:

<p><img src="/images/docs/guides/get-started-with/kubernetes/deployment-plan.png" alt="A screenshot of the Reliably Kubernetes plan form with a Kubernetes deployment target with a Kubernetes environment." width="655" /></p>

Notice how we also selected the Kubernetes environment from the previous
section. This is only required if the experiment we are scheduling is targeting
itself a Kubernetes cluster. Of course, you can run experiments that target
any platform:


<p><img src="/images/docs/guides/get-started-with/kubernetes/deployment-plan-gcp.png" alt="A screenshot of the Reliably Kubernetes plan form with a Kubernetes deployment target with a GCP environment." width="655" /></p>
