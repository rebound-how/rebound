# A Tour Of Reliably

Reliably has mission: make team have an healthier relationship with their
operations and reduce the anxiety related to on-calls or incidents. By being
proactive, teams learn how they react and are allowed to think about how they
can get better at handling future failures in the system.

We care about your teams and we believe practicing with Reliably is one of the
approaches that teams can look after themselves as well.

Reliably is packed with features that support you and your teams in engineering
your resilience!

## Designing and building Experiments

At the core of your journey into Reliably is the concept of an experiment. The
idea originates in the
[Chaos Engineering principles](https://principlesofchaos.org/) of
experimenting to verify how your system copes with a sudden change. 

To help you build your own experiment, you can use the Reliably builder by
clicking on the `Builder` menu.


<p><img src="/assets/images/guides/tour/menu-builder.png" alt="A screenshot of the Reliably main menu with the Builder item selected." width="655" /></p>

Reliably then shows you a list of starters to initialize your experiment with.

<p><img src="/assets/images/guides/tour/builder-starters.png" alt="A screenshot of the Reliably starters list." width="655" /></p>

When you select one starter among this list, Reliably takes you into the
Builder view.


<p><img src="/assets/images/guides/tour/builder-full.png" alt="A screenshot of the Reliably full builder." width="655" /></p>

The builder allows you to design your experiment by ading more activities
from the starters. They can either impact the system even more or collect
information state as the execution takes place. Once saved, you have now
a new experiment under your belt. Congratulations!

<p><img src="/assets/images/guides/tour/experiment-new.png" alt="A screenshot of the Reliably experiment." width="655" /></p>

In this particular experiment, we want to verify if our operations are
correctly wired up for a potential failure in one of our services. As the
team operating the service, we have put in place an alarm in AWS that, when
triggered, automatically creates an
[incident in the AWS OpsCenter](https://docs.aws.amazon.com/incident-manager/latest/userguide/what-is-incident-manager.html).
That incident must have the `"High"` impact and be in an `"OPEN"` state. Along
the way our experiment collects the logs of the pods running our application, as
well as alarm states so we can review both.

## Planning and running Experiments

Reliably orchestrates your experiments. You can plan and schedule their
executions where and when you need.

To quickly plan the execution of an experiment, simply click on the
`Run experiment` button.

<p><img src="/assets/images/guides/tour/run-experiments-buttons.png" alt="A screenshot of the Reliably experiment buttons." width="490" /></p>

This will lead you to the plan creator that allows you to specify where and when
to run the experiment you selected.


<p><img src="/assets/images/guides/tour/plan-new.png" alt="A screenshot of the Reliably new plan form." width="490" /></p>

In a nutshell, the [Deployment](/docs/concepts/deployments) indicates where
to run the experiment from. Here we select Reliably Cloud itself so the
execution is carried by Reliably itself.

The [Environment](/docs/concepts/environments) provides all the needed context
to run the experiment. More specifically, all environment variables and secrets
that the experiment requires.

The schedule defines when to run the experiment: once or in a repeated fashion.

Finally, integrations let you send data back to your world. In our example,
we have enabled sending notifications to [Slack](https://slack.com) as the
experiment runs. We also let the Reliably Assistant converse with 
[OpenAI](https://openai.com/) to asks questions that are relevant to the
experiment (without sending any sensitive data).

Once you have planned, an experiment for execution, you will be able to
navigate to its execution.

<p><img src="/assets/images/guides/tour/plan-running.png" alt="A screenshot of the Reliably plan page when it is running." width="655" /></p>


## Analyzing Experiment Executions

Reliably aims to help you go through the experiment execution timeline with
a fresh and intuitive user experience.

<p><img src="/assets/images/guides/tour/execution-list.png" alt="A screenshot of Reliably showing all executions." width="655" /></p>

Selecting the failed execution, we can see that the expected incident was not
created on AWS.

<p><img src="/assets/images/guides/tour/execution-deviated-ssh.png" alt="A screenshot of Reliably showing deviation." width="490" /></p>

Let's digg a little bit deeper. We can see a pod was indeed deleted and
therefore restarted by Kubernetes.

<p><img src="/assets/images/guides/tour/execution-read-pod-logs.png" alt="A screenshot of the Reliably execution page showing what pod was targeted." width="490" /></p>

We can also see that traffic was impacted.

<p><img src="/assets/images/guides/tour/execution-traffic.png" alt="A screenshot of the Reliably execution page showing traffic loaded into application." width="490" /></p>

<p><img src="/assets/images/guides/tour/execution-traffic-impact.png" alt="A screenshot of the Reliably execution page showing traffic loaded into application." width="490" /></p>

Yet, no alarm was kicked off.

<p><img src="/assets/images/guides/tour/execution-no-alarm.png" alt="A screenshot of the Reliably execution page showing no alarms were raised." width="490" /></p>

As no alarms were triggered, no incidents were opened.

At this stage, we could add more probes into the experiment to narrow down the
issue.

Additionnaly, as you enabled integrations such as Slack, your team will have
received notification of the execution as it took place.

<p><img src="/assets/images/guides/tour/integration-slack.png" alt="A screenshot of the Slack messages of an execution." width="655" /></p>

## Scoring Your Resilience Engineering Efforts

By running a variety of experiments, your teams will start
bubbling the effort poured into engineering for resilience in the organization.

Reliably recommends focusing on team efforts not on particular individuals.
Resilience engineering is a team and organization effort.


<p><img src="/assets/images/guides/tour/experiment-score.png" alt="A screenshot of the Reliably score board." width="490" /></p>

Reliably offers two scores. One, from `A` to `D` which indicates the trend of
execution states for the past ten executions. The other score is freshness of
that trend, from `0` to `100`. The longer you have run the experiment, the
lower the freshness and therefore the less impactful is your knowledge of that
experiment.

That information is aggregated on two other places of Reliably. First on the
dasboard where the freshness/score is plotted for each experiment.

<p><img src="/assets/images/guides/tour/dashboard-score.png" alt="A screenshot of the Reliably dashboard score board." width="490" /></p>


Second, on the experiment list page.


<p><img src="/assets/images/guides/tour/experiment-list.png" alt="A screenshot of the Reliably experiment list." width="655" /></p>

## Reviewing Your Efforts At A Glance

Reliably brings all the data that allows you review your efforts at once on its
dashboard.

<p><img src="/assets/images/guides/tour/dashboard-main.png" alt="A screenshot of the Reliably dashboard." width="655" /></p>

## Digging Deeper With the Assistant

Reliably brings you the power   of its Assistant so that you can explore new
facets of your resilience.

When building a new experiment, Reliably may suggest specific additional
activities to rapidly prototype the right scenario.

<p><img src="/assets/images/guides/tour/builder-assistant.png" alt="A screenshot of the Reliably builder assistant." width="490" /></p>

Additionally, when you enable the OPanAI integration, the Reliably Assistant
will issue questions to either GPT-3.5 or GPT-4 and will integrate the answers
right back into the execution for greater context.

<p><img src="/assets/images/guides/tour/execution-assistant.png" alt="A screenshot of the Reliably execution assistant." width="655" /></p>

You can add your own questions directly when building the experiment:


<p><img src="/assets/images/guides/tour/builder-assistant-add.png" alt="A screenshot of the Reliably builder assistant form." width="490" /></p>

No sensitive information about your execution or organization is ever sent to
OpenAI.


## Bring Your Own Experiments

The Reliably Builder is a powerful feature. However sometimes, you may need
to add your specific experiments for your team to run. Reliably supports
importing your very own [Chaos Toolkit](https://chaostoolkit.org/) experiments.

<p><img src="/assets/images/guides/tour/experiment-import.png" alt="A screenshot of the Reliably import form." width="655" /></p>

Your may also turn these experiments into templates for an easier re-use of
your experiments.

<p><img src="/assets/images/guides/tour/template-form.png" alt="A screenshot of the Reliably template form." width="655" /></p>

Templates allow you to turn this:

```yaml
---
version: 1.0.0
title: Impact of the service process terminating
description: What is the impact of our service process being terminated? Do we get
  any traces anywhere?
configuration:
  target_service:
    type: env
    key: RELIABLY_PARAM_TARGET_SVC
  container_name:
    type: env
    key: RELIABLY_PARAM_CONTAINER_NAME
method:
- name: exec-in-pod
  type: action
  provider:
    type: python
    module: chaosk8s.pod.actions
    func: exec_in_pods
    arguments:
      label_selector: "${target_service}"
      container_name: "${container_name}"
      cmd: kill -TERM 1
```

Into this:

<p><img src="/assets/images/guides/tour/template-use.png" alt="A screenshot of the Reliably template usage." width="655" /></p>


This is quick tour of the main features from Reliably. Enjoy making your
operations less stressful and more data driven!