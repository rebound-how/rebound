---
layout: ~/layouts/DocsLayout.astro
title: Your First Reliably Plan
description: An introduction to Reliably, to understand its concepts and get it into action in a few minutes only.
---

This guide will take you through your first journey using Reliably. You do not
need to know anything about Chaos Engineering to get started.

## 2 minutes to get started

1. Select one of Reliably's
   {==starters==}. We suggest you
   start with a simple one like `Verify latency`
2. Fill its form and click the `Create and run` button. Leave the `Contributions and tags` section as it is for now
3. Select the default `[Reliably Cloud] cloud` deployment
4. Set the schedule to the value `now`
5. Click the `Create plan`

That's it! Well done.

Shortly, the plan will start and the experiment's execution
will be visible from the
{==executions list==}.

### Explanation

Reliably's has the goal to help with the adoption of Chaos Engineering and
verification into a team, or organization. To achieve that, its core concepts
are straightforward and relatable.

Reliably uses the Chaos Engineering concept of `Experiment` which is a way to
declare a scenario of verification of your system. A `Reliably Starter` is a
template for common experiments that you can easily put in place in your
environment without having to learn how they are designed.

A `Reliably Plan` orchestrates the execution of an experiment. To perform this
function, a plan requires a `Reliably Deployment`. A deployment merely instructs
where to run the experiment. A plan also needs a `Reliably Schedule` which
tells Reliably if the plan runs now and/or periodically, through a CRON format.

Optionally, a plan may also take a `Reliably Environment` which represents a
bag of environment variables and secrets to pass to the execution at runtime.
The plan can also take `reliably Integrations` which provide additional
behaviors during the execution of the experiment.

As soon as the run starts it can be reviewed via the `Reliably Execution` page.

## Going further

### Run your own Experiment

While Reliably provides ready-to-run starters, it's likely your system
requires bespoke experiments to fully address its unique properties.

Nothing simpler. Let's say you want to run this experiment:

```json
{
  "title": "Losing an AZ in a classic ELB should not impact our users",
  "description": "While EKS helps with our resilience, we need to understand how the failure of an entire AZ at the ELB level may harm our users.",
  "configuration": {
    "aws_region": "eu-central-1"
  },
  "method": [
    {
      "type": "action",
      "name": "Simulate AZ Failure for a classic LB",
      "pauses": {
        "after": 10
      },
      "provider": {
        "type": "python",
        "module": "azchaosaws.elb.actions",
        "func": "fail_az",
        "arguments": {
          "az": "eu-central-1c",
          "dry_run": false,
          "tags": [
            {
              "Key": "kubernetes.io/service-name",
              "Value": "default/frontend-external"
            }
          ]
        }
      }
    }
  ],
  "rollbacks": [
    {
      "type": "action",
      "name": "Recover AZ Failure for CLB",
      "provider": {
        "type": "python",
        "module": "azchaosaws.elb.actions",
        "func": "recover_az"
      }
    }
  ]
}
```

Go to the {==new experiment==} page and
paste it (or load it from your computer). Leave aside the contributions for
now, we will explain them later. Click the `Import` button.

This experiment is now available on the
{==experiments==} page for all users
of this organization.

Select it in the list and click on the `Run experiment` button. Follow then the
same process as with the starter above to trigger the plan.

### Parametrized your Experiment

Quite often, users will reuse a single experiment but change its parameters
at runtime. To achieve this, you can use `Reliably Environments`. They represent
a bag of clear text environment variables and/or encrypted secrets.

In the example above:

```json
{
  "title": "Losing an AZ in a classic ELB should not impact our users",
  "description": "While EKS helps with our resilience, we need to understand how the failure of an entire AZ at the ELB level may harm our users.",
  "configuration": {
    "aws_region": {
        "type": "env",
        "key": "AWS_REGION",
        "default": "eu-central-1"
    },
    "fail_az_tag_key": {
        "type": "env",
        "key": "TAG_KEY_1",
        "default": "kubernetes.io/service-name"
    },
    "fail_az_tag_value": {
        "type": "env",
        "key": "TAG_KEY_2",
        "default": "default/frontend-external"
    },
  },
  "method": [
    {
      "type": "action",
      "name": "Simulate AZ Failure for a classic LB",
      "pauses": {
        "after": 10
      },
      "provider": {
        "type": "python",
        "module": "azchaosaws.elb.actions",
        "func": "fail_az",
        "arguments": {
          "az": "eu-central-1c",
          "dry_run": false,
          "tags": [
            {
              "Key": "${fail_az_tag_key}",
              "Value": "${fail_az_tag_value}"
            }
          ]
        }
      }
    }
  ],
  "rollbacks": [
    {
      "type": "action",
      "name": "Recover AZ Failure for CLB",
      "provider": {
        "type": "python",
        "module": "azchaosaws.elb.actions",
        "func": "recover_az"
      }
    }
  ]
}
```

We modified the experiment to let the values be passed as environment variables
at runtime. To create an environment that contains these values, go to the
{==environments==} page and click
`New environment`.

Give it a meaningful name and add three environment variables:

* `AWS_REGION` with value `eu-central-1`
* `TAG_KEY_1` with value `kubernetes.io/service-name`
* `TAG_KEY_2` with value `default/frontend-external`

Notice that in the experiment, all our entries have default values already.
This means this experiment can still be used without the environment variables
being set. However, when set, they take precedence over the hardcoded defaults.

Next, when creating a plan, you can simply select the right environment to run
this experiment with different conditions.

### Connect Reliably to your World

You have embarked on an extraordinary journey to learn about your system and
how you, as a team, respond to changes brought to it.

With this in mind, you mustn't consider Reliably as the
end of a line, instead, its power lies in the fact it can surface knowledge
into your usual operational stack.

To achieve this, you can bet on `Reliably Integrations`. Reliably comes
with a set of integrations that push data to places where you already are such
as Slack or observability platforms.

Go to the {==integrations==} page and click
on the `New integration` button. Selects one that suits your operations and
configure it.

When creating a plan, you can enable integrations for the plan and let them do
their magic as the experiment runs.

### Investigate during an Execution

Reliably is all about helping you, as a team, nurture a learning capability.
To this extent, Reliably allows you to put an execution on pause so that you
can go and investigate the system's response to the experiment.

Go to a {==running experiment==} and
click the `Pause execution` button. Reliably will do its best to put the
execution on pause right after the current activity. When that happens, you can
wait for the pause to timeout or click the `Resume execution` button.

!!! tip

  A pause can only happen after the current activity. If that activity is very
  long, your pause will not take place immediately. 


## Learn more

- Read the [Reliably reference](../reference/how-it-works.md) to understand
  Reliably's architecture
