---
layout: ~/layouts/DocsLayout.astro
title: Orchestrate
description: Orchestrate plans and experiments.
---

The Reliably orchestrator is at the heart of the platform and your daily
experience with Reliably.

## Centralize experiments

Reliably experiments are akin to Chaos Engineering experiments and the core
mechanism via which all the data collected by Reliably can be turned into
relevant information for you.

<p><img src="/images/docs/features/orchestrator/experiment.png" alt="A screenshot of an experiment page." width="655" /></p>

## Plan & Schedule experiments

Plan and schedule experiments so they run now or in a repeated fashion so you
can follow their impact trend.

<p><img src="/images/docs/features/orchestrator/new-plan.png" alt="A screenshot of a Reliably new plan form." width="524" /></p>

## Deploy anywhere

Reliably offers a variety of ways for you to execute experiments, such as
in Reliably's Cloud where we manage the infrastructure for you. We also 
support running from your CI or pretty much anywhere you require by using the
Reliably CLI.

<p><img src="/images/docs/features/orchestrator/deploy.png" alt="A screenshot of a Reliably new deployment form." width="521" /></p>

## Pause, Resume, Terminate executions

Reliably understands that experiment on a system is not always an automated
activity.

Sometimes you need to let Reliably know that it should delay
continuing the execution by pausing it. This gives the possibility to explore
the system even more thoroughly while under the condition given by the
experiment. Of course, no pause function should exist without its
counterpart to resume the execution.

We also appreciate that you may need to interrupt the execution as soon as
possible and let's you do so manually or via automated safeguards.

Overall, Reliably gives you the control over executions at all times.

## Lock-in free

Reliably core experiments are Chaos Toolkit experiments.

The [Chaos Toolkit](https://chaostoolkit.org/) is the popular open-source Chaos
Engineering tool for everyone. Reliably provides benefits on top of Chaos
Toolkit experiments but does not bring any lock-in features on top of it.


```yaml
version: 1.0.0
title: Latency remains under 200ms
description: Verify that our endpoint responds under a reasonable amount of time
tags:
  - latency
contributions:
  errors: high
  latency: high
  security: none
  availability: low
runtime:
  hypothesis:
    strategy: after-method-only
configuration:
  reliably_url:
    key: RELIABLY_PARAM_URL
    type: env
    default: 'https://reliably.com'
  reliably_latency:
    key: RELIABLY_PARAM_LATENCY
    type: env
    default: 0.2
steady-state-hypothesis:
  title: capture-response-time-and-verify-it
  probes:
    - name: measure-endpoint-response-time
      type: probe
      provider:
        func: measure_response_time
        type: python
        module: chaosreliably.activities.http.probes
        arguments:
          url: '${reliably_url}'
      tolerance:
        name: validate-response-time
        type: probe
        provider:
          func: response_time_must_be_under
          type: python
          module: chaosreliably.activities.http.tolerances
          arguments:
            latency: '${reliably_latency}'
method: []
```