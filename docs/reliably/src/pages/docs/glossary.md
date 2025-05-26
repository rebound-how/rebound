---
layout: ~/layouts/DocsLayout.astro
title: Glossary
description: A glossary of the terms used in the Reliably documentation.
---

A list of terms used in the Reliably documentation and their definitions.

<dl>
  <div id="action-experiment">
    <dt>Action (Experiment)</dt>
    <dd>
      <p>
        An action is a particular activity that needs to be enacted on the system under experimentation. For example, it can be terminating Kubernetes pods, or injecting latency in an API call.
      </p>
    </dd>
  </div>

  <div id="activity-experiment">
    <dt>Activity (Experiment)</dt>
    <dd>
      <p>
        An activity, in an experiment context, is an <a href="#action-experiment">action</a> or a <a href="#probe-experiment">probe</a>.
      </p>
    </dd>
  </div>

  <div id="deviation-execution">
    <dt>Deviation (Execution)</dt>
    <dd>
      <p>
        An execution is considered deviated, and its <code>deviated</code> property is set to <code>true</code> if the <a href="#steady-state-hypothesis">steady-state hypothesis</a> was executed after the method, but at least one of its probes failed to match the expected tolerance.
      </p>
      <p>
        Eg. A latency above the threshold, a 500 response code to an API call, etc. 
      </p>
      <p>If an execution is &laquo;deviated&raquo;, we sometimes display its status badge as "Deviated". While this is not a <em>proper</em> status, it tells you what you want to know: the experiment completed, and its <code>deviated</code> property's value is <code>true</code>. On the other hand, if the execution has completed and didn't deviate, its status will be displayed as completed.</p>
    </dd>
  </div>

  <div id="probe-experiment">
    <dt>Probe (Experiment)</dt>
    <dd>
      <p>
        A probe is a way of observing a particular set of conditions in the system that is undergoing experimentation.
      </p>
    </dd>
  </div>

  <div id="rollbacks">
    <dt>Rollbacks</dt>
    <dd>
      <p>
        Rollbacks are a sequence of actions that revert what was undone during the experiment. They're defined in the experiment and run after all other activities.
      </p>
    </dd>
  </div>

  <div id="status-execution">
    <dt>Status (Execution)</dt>
    <dd>
      <p>
        Depending on if it is running or not, and on how it ended, an execution can have one of the following statuses:
      </p>
      <ul>
        <li><strong>running</strong>: Reliably is currently running the experiment;</li>
        <li><strong>pause</strong>: Reliably is running the experiment, and it has been paused, either by a user or because it reached a pause instruction;</li>
        <li><strong>interrupted</strong>: the experiment was interrupted before full completion;</li>
        <li><strong>failed</strong>: one activity reported a failed condition;</li>
        <li><strong>aborted</strong>: the execution broke for unknown reasons;</li>
        <li><strong>completed</strong>: the execution ran entirely and is now completed.</li>
      </ul>
    </dd>
  </div>

  <div id="steady-state-hypothesis">
    <dt>Steady-State Hypothesis</dt>
    <dd>
      <p>
        A Steady State Hypothesis describes “what normal looks like” for your system for the experiment to surface information about weaknesses when compared against the declared “normal” tolerances of what is measured.
      </p>
      <p>
        Reliably experiments use the Steady State Hypothesis for two purposes:
      </p>
      <ul>
        <li>as a check before an experiment is run that the target system is in a recognized normal state;</li>
        <li>as the template for comparison of the state of your system after the experiment has been run, forming the results provided by the experiment’s report.</li>
      </ul>
    </dd>
  </div>

  <div id="verification">
    <dt>Verification</dt>
    <dd>
      <p>A Reliably experiment whose goal is to measure (&laquo;verify&raquo;) that a particular condition in the system meets requirements. It doesn't need to use its method to run chaos-inducing activities.</p>
      <p>Eg. Verify that your database responds in under 200 ms.</p>
    </dd>
  </div>
</dl>