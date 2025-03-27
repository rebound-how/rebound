## Reliably Cloud

Reliably can handle the task of running your experiments for you. It's a great way to get started and allows teams with various technical levels to run experiments without having to install anything.

<div class="flowchart flowchart--cols-3 flowchart--rows-5" aria-hidden="true">
  <div class="fcItem fcItem--col-1 fcItem--row-3">Schedule</div>
  <div class="fcItem fcItem--col-1 fcItem--row-4">Integrations</div>

  <div class="fcItem fcItem--col-2 fcItem--row-1 fcItem--colLegend">
    Reliably
  </div>
  <div class="fcItem fcItem--col-2 fcItem--row-2">
    Plan
    <span class="fcRelation fcRelation--toBottom" data-legend="spins"></span>
  </div>
  <div class="fcItem fcItem--col-2 fcItem--row-3">
    Deployment
    <span class="fcRelation fcRelation--toLeft" data-legend="gets info from"></span>
    <span class="fcRelation fcRelation--toRight" data-legend="reads from"></span>
    <span class="fcRelation fcRelation--toBottom" data-legend="runs"></span>
  </div>
  <div class="fcItem fcItem--col-2 fcItem--row-4">
    Experiment
    <span class="fcRelation fcRelation--toBottom" data-legend="generates"></span>
    <span class="fcRelation fcRelation--toRight fcRelation--up-1" data-legend="uses"></span>
    <span class="fcRelation fcRelation--toLeft" data-legend="uses"></span>
  </div>
  <div class="fcItem fcItem--col-2 fcItem--row-5">Execution Results</div>

  <div class="fcItem fcItem--col-3 fcItem--row-3">Environment</div>
</div>

## GitHub Workflows

Use Github Workflows to run experiments without having to set up anything. Reliably will create a GitHub workflow and use it as your execution environment. Additional billing from GitHub might occur depending on your usage.

To run an experiment as a GitHub Workflow, create a GitHub [deployment](/docs/concepts/deployments) and use it in a [plan](/docs/concepts/plans).

<div class="flowchart flowchart--cols-3 flowchart--rows-6" aria-hidden="true">
  <div class="fcItem fcItem--col-1 fcItem--row-1 fcItem--colLegend">
    Reliably
  </div>
  <div class="fcItem fcItem--col-1 fcItem--row-2">
    Plan
    <span class="fcRelation fcRelation--toBottom" data-legend="spins"></span>
  </div>
  <div class="fcItem fcItem--col-1 fcItem--row-3">
    Deployment
    <span class="fcRelation fcRelation--toRight fcRelation--down-1" data-legend="pushes to"></span>
  </div>
  <div class="fcItem fcItem--col-1 fcItem--row-4">
    Experiment
    <span class="fcRelation fcRelation--toBottom" data-legend="uses"></span>
  </div>
  <div class="fcItem fcItem--col-1 fcItem--row-5">Integrations</div>
  <div class="fcItem fcItem--col-1 fcItem--row-6">
    Execution Results
  </div>

  <div class="fcSeparator fcSeparator--col-1" data-legend="HTTPS"></div>

  <div class="fcItem fcItem--col-2 fcItem--row-1 fcItem--colLegend">
    GitHub
  </div>
  <div class="fcItem fcItem--col-2 fcItem--row-4">
    GitHub Workflow
    <span class="fcRelation fcRelation--toLeft fcRelation--down-2" data-legend="sends"></span>
    <span class="fcRelation fcRelation--toRight" data-legend="uses"></span>
    <span class="fcRelation fcRelation--toLeft" data-legend="fetches and runs"></span>
    <span class="fcRelation fcRelation--toRight fcRelation--down-1" data-legend="uses"></span>
  </div>

  <div class="fcItem fcItem--col-3 fcItem--row-4">
    Environment
  </div>
  <div class="fcItem fcItem--col-3 fcItem--row-5">Schedule</div>
</div>

## Kubernetes

Use Kubernetes to run experiments without having to set up anything. Reliably will create a Kubernetes Job and use it as your execution environment.

To run an experiment in a Kubernetes cluster, create a Kubernetes [deployment](/docs/concepts/deployments) and use it in a [plan](/docs/concepts/plans).

<div class="flowchart flowchart--cols-3 flowchart--rows-7" aria-hidden="true">
  <div class="fcItem fcItem--col-1 fcItem--row-1 fcItem--colLegend">
    Reliably
  </div>
  <div class="fcItem fcItem--col-1 fcItem--row-2">
    Plan
    <span class="fcRelation fcRelation--toBottom" data-legend="spins"></span>
  </div>
  <div class="fcItem fcItem--col-1 fcItem--row-3">
    Deployment
    <span class="fcRelation fcRelation--toRight fcRelation--down-1" data-legend="creates"></span>
  </div>
  <div class="fcItem fcItem--col-1 fcItem--row-4">
    Environment
  </div>
  <div class="fcItem fcItem--col-1 fcItem--row-5">
    Experiment
    <span class="fcRelation fcRelation--toBottom" data-legend="uses"></span>
  </div>
  <div class="fcItem fcItem--col-1 fcItem--row-6">Integrations</div>
  <div class="fcItem fcItem--col-1 fcItem--row-7">Execution Results</div>
  <div class="fcSeparator fcSeparator--col-1" data-legend="HTTPS"></div>

  <div class="fcItem fcItem--col-2 fcItem--row-1 fcItem--colLegend">
    Kubernetes
  </div>
  <div class="fcItem fcItem--col-2 fcItem--row-4">
    Job or CronJob
    <span class="fcRelation fcRelation--toBottom" data-legend="creates and manages"></span>
  </div>
  <div class="fcItem fcItem--col-2 fcItem--row-5">
    Pod
    <span class="fcRelation fcRelation--toLeft fcRelation--up-1" data-legend="fetches and uses"></span>
    <span class="fcRelation fcRelation--toLeft fcRelation--down-2" data-legend="sends"></span>
    <span class="fcRelation fcRelation--toLeft" data-legend="fetches and runs"></span>
  </div>
</div>

## Reliably CLI

Reliably relies on Chaos Toolkit to run experiments. It means you can benefit from its versatility and run Reliably pretty much anywhere. Use the Reliably CLI in your environment, as a CI/CD, a container, or a terminal, and it will get everything it needs from your plan and deployment.

To run an experiment with the Reliably CLI, create a Reliably CLI [deployment](/docs/concepts/deployments) and use it in a [plan](/docs/concepts/plans).

<div class="flowchart flowchart--cols-3 flowchart--rows-6" aria-hidden="true">
  <div class="fcItem fcItem--col-1 fcItem--row-1 fcItem--colLegend">
    Reliably
  </div>
  <div class="fcItem fcItem--col-1 fcItem--row-2">
    Plan
    <span class="fcRelation fcRelation--toBottom" data-legend="spins"></span>
  </div>
  <div class="fcItem fcItem--col-1 fcItem--row-3">
    Deployment
  </div>
  <div class="fcItem fcItem--col-1 fcItem--row-4">
    Experiment
    <span class="fcRelation fcRelation--toBottom" data-legend="uses"></span>
  </div>
  <div class="fcItem fcItem--col-1 fcItem--row-5">Integrations</div>
  <div class="fcItem fcItem--col-1 fcItem--row-6">Execution Results</div>

  <div class="fcSeparator fcSeparator--col-1" data-legend="HTTPS"></div>

  <div class="fcItem fcItem--col-2 fcItem--row-1 fcItem--colLegend">
    You
  </div>
  <div class="fcItem fcItem--col-2 fcItem--row-4">
    Reliably CLI
    <span class="fcRelation fcRelation--toLeft fcRelation--up-1" data-legend="pulls"></span>
    <span class="fcRelation fcRelation--toLeft fcRelation--down-2" data-legend="sends"></span>
    <span class="fcRelation fcRelation--toRight" data-legend="uses"></span>
    <span class="fcRelation fcRelation--toLeft" data-legend="fetches and runs"></span>
  </div>

  <div class="fcItem fcItem--col-3 fcItem--row-4">
    Environment
  </div>
</div>

## On-Premises

With an Enterprise Subscription, Reliably can be installed on-premises entirely

In that case, the Reliably Cloud is not available as a deployment target but
other, bespoke deployments targets can be enabled: Docker (in which case you
provide your own image), Kubernetes, etc.

<div class="flowchart flowchart--cols-3 flowchart--rows-5" aria-hidden="true">
  <div class="fcItem fcItem--col-1 fcItem--row-3">Schedule</div>
  <div class="fcItem fcItem--col-1 fcItem--row-4">Integrations</div>

  <div class="fcItem fcItem--col-2 fcItem--row-1 fcItem--colLegend">
    (You) On-Premises
  </div>
  <div class="fcItem fcItem--col-2 fcItem--row-2">
    Plan
    <span class="fcRelation fcRelation--toBottom" data-legend="spins"></span>
  </div>
  <div class="fcItem fcItem--col-2 fcItem--row-3">
    Deployment
    <span class="fcRelation fcRelation--toLeft" data-legend="gets info from"></span>
    <span class="fcRelation fcRelation--toRight" data-legend="reads from"></span>
    <span class="fcRelation fcRelation--toBottom" data-legend="runs"></span>
  </div>
  <div class="fcItem fcItem--col-2 fcItem--row-4">
    Experiment
    <span class="fcRelation fcRelation--toBottom" data-legend="generates"></span>
    <span class="fcRelation fcRelation--toRight fcRelation--up-1" data-legend="uses"></span>
    <span class="fcRelation fcRelation--toLeft" data-legend="uses"></span>
  </div>
  <div class="fcItem fcItem--col-2 fcItem--row-5">Execution Results</div>

  <div class="fcItem fcItem--col-3 fcItem--row-3">Environment</div>
</div>
