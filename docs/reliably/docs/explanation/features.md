# Reliably Features

## Agnostic

Whether you are a small or large organization, you run multiple systems. In
some cases, these systems require additional capabilities to experiment on
them.

Whether you run a public cloud, a Kubernetes platform, datacenters, Windows,
Linux, etc.

Reliably targets your system natively or can be easily extended to support
your unique requirements.

<p align=center><img src="/assets/images/features/agnostic/list.png" alt="A screenshot of Reliably extensions" width="635" /></p>


### Run on any systems

Reliably is designed so that you can perform experiment execution from its
cloud, from a third-party such as CI or from inside your system directly.

Unlike many other tools, Reliably is agentless and adjusts itself to the
security constraints you have defined.

## AI Assistant

### Bring the World in to help you

Realiably recognizes the power of the knowledge available to engineers and leaders
today. We have created a unique assistant that brings this mass of information
to you

<p align=center><img src="/assets/images/features/assistant/example.png" alt="A screenshot of the Reliably App, displaying the assistant" width="639" /></p>

Leveraging the capabilities of public large language models, such as 
<a href="https://openai.com/" alt="OpenAI website">OpenAI</a> ChatGPT, Reliably
contextualizes your executions with well-targeted conversations.

### Open up to your creativity

The power of the Reliably Assistant resides in its capacity to enable your
creativity by bringing the threads of your execution into a larger context and letting you figure out what to do next from here.

## Smart Builder

### Build an experiment

Navigate to the Environments page to
bring the list of experiment starters provided by Reliably.

<p align=center><img src="/assets/images/features/builder/starters.png" alt="A screenshot of the Reliably Builder starters catalog" width="655" /></p>

Select a starter and use the builder to expand your experiment with more
operations by navigating back to the starters catalog.

<p align=center><img src="/assets/images/features/builder/full.png" alt="A screenshot of the Reliably Builder" width="655" /></p>

## Orchestrator

### Centralize experiments

Reliably experiments are akin to Chaos Engineering experiments and the core
mechanism via which all the data collected by Reliably can be turned into
relevant information for you.

<p align=center><img src="/assets/images/features/orchestrator/experiment.png" alt="A screenshot of an experiment page." width="655" /></p>

### Plan & Schedule experiments

Plan and schedule experiments so they run now or in a repeated fashion so you
can follow their impact trend.

<p align=center><img src="/assets/images/features/orchestrator/new-plan.png" alt="A screenshot of a Reliably new plan form." width="524" /></p>

### Deploy anywhere

Reliably offers a variety of ways for you to execute experiments, such as
in Reliably's Cloud where we manage the infrastructure for you. We also 
support running from your CI or pretty much anywhere you require by using the
Reliably CLI.

<p align=center><img src="/assets/images/features/orchestrator/deploy.png" alt="A screenshot of a Reliably new deployment form." width="521" /></p>

### Pause, Resume, Terminate executions

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

### Lock-in free

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

## Scoring


### Priority and decision making

Reliably Scoring helps you understand and prioritize operational decisions.

With growing complexity in your systems, where do you put the right budget
and effort? When everything is reported as urgent, how do you steer the boat?


<p align=center><img src="/assets/images/features/scoring/base.png" alt="A basic view of reliably scoring." width="495" /></p>

Use Reliably Score to match your system with your operation governance
compliance.

### Innovation or renovation

Reliably Scores help you understand how safe and sound it is to push the envelop
and continue innovating at the risk of a significant failure.

Going from A to D, Reliably offers a finely tuned reading of your operations so
you can make the right next call.

### Data freshness is everything

Reliably Freshness Score helps you evaluate the relevance of a score. The
older the greater the chance the score has become stalled.

## Templating

### Tailored to your requirements

While Reliably brings a set of well-rounded [starters](/docs/concepts/starters),
the strength of the platform is in providing a safe and straightforward
mechanism to let you bring your own templated experiments.

Your system is unique, so should your Reliably experience.

### Paramaterization for everyone

We understand that sometimes you need to be able to tweak a single parameter
to keep on expliring your system. This operation is made easy as Reliably
lets you override configuration however you need.