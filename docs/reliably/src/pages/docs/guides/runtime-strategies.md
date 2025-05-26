---
layout: ~/layouts/DocsLayout.astro
title: Runtime Strategies
description: How to control the execution rollbacks and hypothesis.
---

The default behavior of running an experiment goes as follows:

1. Run the verification if defined
2. Run the method if defined
3. Run the verification again if defined
4. Run the rollbacks if defined

That flow is not always appropriate and Reliably allows you to tune this in
two positions: the verification and the rollbacks.

Regarding the verification, you can decide to run it with the following
strategies:

* before and after the method (default behavior)
* before only
* after only
* during the method only
* before, after and during the method. In that case, you can set a frequency
  for how often to run the verification during the method. Additionally, you can
  also set the a flag that fails the execution as soon as the verification is not
  met

Regarding the rollbacks, you can decide to run it with the following
strategies:

* always (default)
* only if the hypothesis deviated
* never

Adjusting these two strategies will allow you to play the experiment in a
flavor that matches your goals.


## Set the Strategies from the Builder

When you construct your experiment via the Builder, you can set these
strategies. 

<p><img src="/images/docs/guides/runtime-strategies/builder-default.png" alt="A screenshot of selecting the hypothesis strategy." width="655" /></p>

You can set the frequency and fail fast flag when choosing the continuous
strategy.

<p><img src="/images/docs/guides/runtime-strategies/builder-continuous.png" alt="A screenshot of selecting the hypothesis continuous strategy." width="655" /></p>

## Set the Strategies from the Experiment

The runtime strategies can also be directly set from the experiment file itself.
Simply add the `runtime` property to your experiment with the following
structure:

```json
"runtime": {
    "hypothesis": {
        "strategy": "default",
        "fail_fast": false,
        "freq": 3.0
    },
    "rollbacks": {
        "strategy": "always"
    }
}
```


The values for the `rollbacks.strategy` property are one of `"default"`,
`"always"`, `"never"` or `"deviated"`.

The values for the `hypothesis.strategy` property are one of `"default"`,
`"skip"`, `"before-method-only"`, `"after-method-only"`, `"during-method-only"`
or `"continuously"`.

When the strategy is either `"during-method-only"` or `"continuously"`, the
`freq` and `fail_fast` are used to determine how often the verification is
performed and if the execution should fail immediatly should the verification is
not met. Otherwise these properties are ignored and can be left out.

