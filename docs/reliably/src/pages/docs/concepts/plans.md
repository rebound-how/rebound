---
layout: ~/layouts/DocsLayout.astro
title: Plans
description: Use plans to schedule and run chaos engineering experiments
---

Plans combine all the other elements from Reliably to allow you to run and schedule experiments in a predefined environment.

Plans allow running chaos engineering experiments according to a schedule. They rely on an existing deployment to be granted the rights to **run Chaos Toolkit in a GitHub Action or the Reliably Cloud**.

<p><img src="/images/docs/concepts/plans/reliably-plan.png" alt="A screenshot of the Plan creation form in the Reliably App. The form displays a select field to choose a deployment, a list of checkboxes to pick experiments and a text field to type a schedule in the form of a CRON schedule." width="492" /></p>

## Create a plan

### Deployment

Pick an existing [deployment](/docs/concepts/deployments/) where your plan will run. You can create two types of deployments:

- GitHub deployments: your plan will run as a GitHub Action
- Reliably Cloud deployments: your plan will be entirely handled by Reliably 

### Environment

Select an optional [environment](/docs/concepts/environments/) that stores variables and secrets that will be accessed by your environment and your experiment.

### Experiment

Select the existing [experiment](/docs/concepts/experiments/) that your plan will run. Whether it is one of your imported experiments or one created from a [starter](/docs/concepts/starters/), it will be executed by Chaos Toolkit in your selected deployment.

### Schedule

<p>The 'schedule' text field defines when your plan will run. It expects a <a href="https://www.ibm.com/docs/en/db2oc?topic=task-unix-cron-format" target="_blank" rel="noopener noreferer">CRON schedule <span class="screen-reader-text">External link will open in a new tab</span></a> or the <strong>now</strong> keyword, which will have your plan run once, as soon as possible.</p>

### Integrations

Select one or more [integrations](/docs/concepts/integrations/) that will be used by the experiment to send data to other tools in your stack.