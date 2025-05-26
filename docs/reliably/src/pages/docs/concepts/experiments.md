---
layout: ~/layouts/DocsLayout.astro
title: Experiments
description: Experiments are a versatile way to describe the actions you want Reliably to apply to your system, such as verifications or full-fledged chaos engineering experiments.
---

Experiments are a versatile way to describe the actions you want Reliably to apply to your system, such as verifications or full-fledged chaos engineering experiments.

<p>Under the hood, <strong>Reliably uses the <a href="https://chaostoolkit.org" rel="noreferer noopener" target="_blank">open-source Chaos Toolkit <span class="screen-reader-text">External link will open in a new tab</span></a> to run experiments.</strong></p>

## Definition

Experiments are described as a single JSON file, and contain the following elements :

- a `title`
- a `description`
- a `method` that contains activities:
  - `probes`, a way of observing your system's conditions
  - `actions`, activities that are enacted on your system (such as fault injection or any kind of turbulence)
- `steady-state hypothesizes`, which describes what *normal* looks like:  
  - before the experiment, to check the system is in a normal state
  - after the experiment, to compare its initial and current states
- `rollbacks`, a set of actions that revert what was done during the experiment

Additionally, `controls`, `configurations`, and `secrets` can be provided to actions or probes as operational elements.

An experiment doesn't necessarily contain all of these elements: if you decide to use Reliably to run a simple verification (an experiment that only measures certain values of your system, such as the latency of a service), you won't need any method activities or rollbacks and can use the steady-state hypothesis object to run your probes.

<p>For a complete overview of experiments, you can refer to the <a href="https://chaostoolkit.org/reference/api/experiment/" taget="_blank" rel="noopener noreferer">Chaos Toolkit API reference <span class="screen-reader-text">External link will open in a new tab</span></a>.</p>

## Creating experiments

Before you can use an experiment in a [plan](/docs/concepts/plans/), you need to create it within Reliably. This can be done by either importing an existing experiment (as a JSON file) or using a starter (an experiment template where you only need to provide some information).

### Starters

Starters are experiment templates. They can either be [provided by Reliably](/docs/concepts/starters) or [specific to your organization](/docs/concepts/custom-templates). In both cases, a starter presents itself as a form requesting you to fill in values that are requested for the experiment to run.

<img src="/images/docs/starters/reliably-terminate-pods.png" alt="A screenshot of the form to create and run an experiment to terminate Kubernetes pods. It features a text field expecting a list of label selectors for the pods that will be terminated." width="492" />

This form allows you to create an experiment that will [terminate Kubernetes pods](/docs/starters/terminate-kubernetes-pods). It can be used to simulate the failure of a service.

Once the starter form has been filled, clicking the "Create" button will make it available to your plans, while the "Create and run" button will open the page to create a new plan, with the experiment already selected.

### Import

You can import existing or custom experiments by providing Reliably with the experiment definition as a JSON file (or by pasting the content of the file).

<img src="/images/docs/concepts/experiments/reliably-import-experiment.png" alt="A screenshot of the page to create a new experiment. It features a field to select a file from your computer, and another of to paste the content of a JSON file." width="1323" />

Once your experiment is imported, it will be available to your plans.

Pasting or selecting a file will process a quick conformity check of your experiment. While it can detect an experiment that is not properly formed, **it cannot guarantee that the experiment will run, or that it will perform the expected actions**. Consider it as a linter, not as a validation of your experiment's outcome.

## Executions

Your experiment is now ready to be used by a [plan](/docs/concepts/plans/). Each time your experiment is run as part of a plan, a new [execution](/docs/concepts/executions/) will be generated, and display the execution's result and journal.