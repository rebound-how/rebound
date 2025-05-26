---
layout: ~/layouts/DocsLayout.astro
title: From Chaos Toolkit to Reliably
description: Relationship between the Chaos Toolkit and Reliably
---

## Chaos Toolkit

[Chaos Toolkit][ctk] is the Open Source Chaos Engineering framework for
everyone. Its aim is to provide an extensible protocol and interface to create
from the simplest to the richest experiment you could think of.

[ctk]: https://chaostoolkit.org/

Chaos Toolkit focuses on the followings:

* An interface to declare your experiment as a JSON/YAML file
* A runtime to execute experiments from the CLI
* A protocol to extend the experiment with your own dedicated actions, probes
  or controls

However, the Chaos Toolkit does not take into its scope the followings:

* A centralized platform to manage and visualize your fleet of experiments
* Any sort of planning orchestration

This is where Reliably comes into play.

## Reliably

Reliably focuses on the platform aspect of running Chaos Engineering
experiments. It offers centralization & history, planning & orchestrating,
scoring and measuring your efforts running these experiments.

Reliably heavily relies on Chaos Toolkit to perform the low-level runtime
of the experiment and turns the results into a rich platform above it.

In Reliably, an experiment is a Chaos Toolkit experiment. This means you are
never locked into Reliably and can always run your experiments outside of
Reliably. You merely then lose the benefits of the centralized platform.

## Rough Architecture

Through Reliably, users create experiments via the UI. The goal here is to
reduce the complexity of understanding what an experiment is made of and 
focus on its goal. When saved the experiment is serialized to a Chaos Toolkit
experiment. It only contains sufficient information, using the [control][ctrl]
interface of the Chaos Toolkit, to report back to Reliably when running. If
that information is not present, the experiment runs as usual anyway, it will
simply not ping Reliably and therefore will not be part of any history.

When an experiment is planned for execution in Reliably, the experiment
Reliably URL is passed to a runner which fetches it and run it. The runner
entrypoint is the [Reliably CLI][cli] which knows how to fetch the environment
necessary to execute the experiment: Reliably environment variables, Reliably
secrets and Reliably integrations (which are also merely Chaos Toolkit
controls). The Reliably CLI then calls the Chaos Toolkit execution entrypoint
and starts running the experiment, reporting back to Reliably as it unfolds.

Overall, Reliably takes advantage of the Chaos Toolkit ecosystem to offer
a large set of actions and probes but adds a platform flavour on top of it.


[cli]: https://github.com/reliablyhq/cli
[ctrl]: https://chaostoolkit.org/reference/extending/create-control-extension/