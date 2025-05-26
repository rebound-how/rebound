---
layout: ~/layouts/DocsLayout.astro
title: Executions
description: Executions are a journal of the results of your experiment run.
---

Executions are a journal of the results of your experiment run. Each time one of your [experiments](/docs/concepts/experiments/) is run as part of a plan, an execution is generated and available in Reliably. It presents the execution's results and allows you to download a complete execution journal.

<img src="/images/docs/concepts/executions/reliably-execution-example.png" alt="A screenshot of an execution page in Reliably." width="1324" />

## Pause / Resume / Stop

If you're viewing a running experiment, action buttons Pause (or Resume) Execution and Stop Executions are available in the top right corner of the page. They will, as their name implies, allow you to Pause, Resume, or Stop the execution.

### Pause Execution

Clicking the Pause Execution button will **send a pause signal** to Reliably. The execution status will immediately change to **Pausing...**

<img src="/images/docs/concepts/executions/reliably-pausing.png" alt="" width="134" />

At this stage, Reliably is waiting for the current <a href="/docs/glossary/#activity-experiment">activity</a> to finish, and it will then prevent the execution from continuing.

At the next update of the execution data, if the execution is effectively paused, its status will change to **Paused**.

Take into consideration that if you are running your execution in the Reliably Cloud you might be subject to an execution duration limit, depending on your pricing plan. The pause will still count toward your execution duration. For example, a free plan has a 10-minutes maximum duration. If you pause an execution after 8 minutes, a 2 minutes pause will cause the execution to be ended.
### Resume Execution

If an execution is paused (or pausing), the Resume Execution button is displayed. Clicking the Resume Execution button will **send a resume signal** to Reliably. This signal will cause the execution to resume *almost* immediately.

### Stop Execution

A running or paused execution can be stopped by clicking the Stop Execution button. When the button is clicked, a modal window will open to confirm your choice and allow you to choose if you want to skip rollbacks.

<img src="/images/docs/concepts/executions/reliably-stop-execution-modal.png" alt="A modal window. The message reads: You are about to stop an execution. This action cannot be undone. You can choose to skip rollbacks, but be aware that even running them might leave your system in an unknown state. A checkbox allows to 'Terminate ungracefully'. Underneath are two buttons to Cancel or Stop Execution." width="486" />

Clicking the Stop Execution button in the modal will **send a stop signal** to Reliably. The execution status will immediately change to **Stopping...**

<img src="/images/docs/concepts/executions/reliably-stopping.png" alt="" width="147" />

At this stage, Reliably is waiting for the current activity to finish, and it will then stop the execution. If the "Terminate ungracefully" box is left unchecked, the <a href="/docs/glossary/#rollbacks">rollbacks</a> will be executed.

At the next update of the execution data, if the execution is effectively stopped, its status will change to **Interrupted**.

## Execution info

At the top of the page is displayed the execution's unique UUID, as well as some general information about the execution:
- its status (here, our experiment deviated, meaning its result was not what was expected),
- when it ran,
- the name of the experiment (here, Latency remains under 200ms, which is one of our [starters](/docs/concepts/starters/)).

## Result

This section displays:

- the execution [status](/docs/glossary/#status-execution),
- if the execution [deviated](/docs/glossary/#deviation-execution),
- when the execution started,
- when the execution ended,
- the execution duration.

It also presents links to:

- the execution journal,
- the execution logs,
- the GitHub workflow page, if it was run as a GitHub Action

## Environment

This section presents information about the environment the Reliably experiment was run in.

- ChaosLib is the version of the Chaos Toolkit Library used,
- Platform is the Operating System that was used,
- Node is the name of the machine the experiment was run on.

## Timeline

This Reliably timeline is a step-by-step breakdown of all the events that took place during an experiment execution.

It displays the main phases of the execution (steady-state hypothesis, method, rollbacks) as well as each activity that took place.

If an activity returns a result, this result is displayed in the event.

<img src="/images/docs/concepts/executions/reliably-execution-timeline-events.png" alt="A screenshot showing two events in a timeline. The first event is the end of a probe activity. The probe is named measure-endpoint-response-time, and we can see it's tolerance was not met. The next event is the end of the steady-state hypothethis. It tells us the steady-state was not met, which is a consequence of the previous probe's tolerance not being met." width="1280" />

Some activities, such as probes, can return more detailed results. If this is the case, a "Details" button reveals those results.

<img src="/images/docs/concepts/executions/reliably-execution-timeline-event-details.png" alt="A screenshot showing the same first event as on the previous screenshot. The details section is opened and reveals the probe was successfully run, but it returned a value of 0.39 seconds, which is above the expected threshold of 200 ms" width="573" />
