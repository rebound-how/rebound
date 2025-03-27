# Concepts

Reliably acts as an orchestration and centralization platform of your resilience
operations around the following concepts:


<div class="grid cards" markdown>
- :material-code-json: __[Experiment](#experiments)__ - the description of reliability policies
- :material-timer-play-outline: __[Plan](#plans)__ - the heart of the platform engine
- :material-location-enter: __[Deployment](#deployments)__ - the place where experiments are executed by plans
- :material-clipboard-text-multiple-outline: __[Environment](#environments)__ - the runtime context of an execution
- :fontawesome-solid-arrows-turn-to-dots: __[Integration](#integrations)__ - operational extensions to play during an experiment's execution
- :material-text-box-check-outline: __[Execution](#executions)__ - an artefact of an experiment's run
- :material-view-grid-plus-outline: __[Template](#starters)__ - a custom made experiment ready to be used by anyone
</div>


## Experiments

Experiments are a versatile way to describe the actions you want Reliably to apply to your system, such as verifications or full-fledged chaos engineering experiments.

Under the hood, Reliably uses the [open-source Chaos Toolkit](https://chaostoolkit.org) to run experiments.

### Definition

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

For a complete overview of experiments, you can refer to the [Chaos Toolkit API reference](https://chaostoolkit.org/reference/api/experiment/).

### Creating experiments

Before you can use an experiment in a [plan](#plans), you need to create it within Reliably. This can be done by either importing an existing experiment (as a JSON file) or using a starter (an experiment template where you only need to provide some information).

#### Starter Templates

Starters are experiment templates. They can either be [provided by Reliably](#starters) or [specific to your organization](#custom-templates). In both cases, a starter presents itself as a form requesting you to fill in values that are requested for the experiment to run.

<p align=center><img src="/assets/images/starters/reliably-terminate-pods.png" alt="A screenshot of the form to create and run an experiment to terminate Kubernetes pods. It features a text field expecting a list of label selectors for the pods that will be terminated." width="492" /></p>

This form allows you to create an experiment that will terminate Kubernetes pods. It can be used to simulate the failure of a service.

Once the starter form has been filled, clicking the "Create" button will make it available to your plans, while the "Create and run" button will open the page to create a new plan, with the experiment already selected.

#### Import

You can import existing or custom experiments by providing Reliably with the experiment definition as a JSON file (or by pasting the content of the file).

<p align=center><img src="/assets/images/concepts/experiments/reliably-import-experiment.png" alt="A screenshot of the page to create a new experiment. It features a field to select a file from your computer, and another of to paste the content of a JSON file." width="1323" /></p>

Once your experiment is imported, it will be available to your plans.

Pasting or selecting a file will process a quick conformity check of your experiment. While it can detect an experiment that is not properly formed, **it cannot guarantee that the experiment will run, or that it will perform the expected actions**. Consider it as a linter, not as a validation of your experiment's outcome.

### Experiment Executions

Your experiment is now ready to be used by a [plan](#plans). Each time your experiment is run as part of a plan, a new [execution](#executions) will be generated, and display the execution's result and journal.

## Plans

Plans combine all the other elements from Reliably to allow you to run and schedule experiments in a predefined environment.

Plans allow running chaos engineering experiments according to a pattern schedule.

<p align=center><img src="/assets/images/concepts/plans/reliably-plan.png" alt="A screenshot of the Plan creation form in the Reliably App. The form displays a select field to choose a deployment, a list of checkboxes to pick experiments and a text field to type a schedule in the form of a CRON schedule." width="492" /></p>

### Create a plan

#### Deployment

Pick an existing [deployment](#deployments) where your plan will run. You can the following types of deployments:

- Reliably CLI Managed deployments: your plan will be entirely handled by Reliably
- Reliably CLI Manual deployments: your plan will be triggered by calling the Reliably CLI yourself
- Kubernetes deployments: your plan will run as a [Kubernetes Job](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- Docker deployments: your plan will run locally within a container
- GitHub deployments: your plan will run as a [GitHub Action](https://github.com/features/actions)

#### Environment

Select an optional [environment](#environments) that stores variables and secrets that will be accessed by your environment and your experiment.

#### Experiment

Select the existing [experiment](#experiments) that your plan will run. Whether it is one of your imported experiments or one created from a [starter](#starters), it will be executed by Chaos Toolkit in your selected deployment.

#### Schedule

The 'schedule' text field defines when your plan will run. It expects a [CRON schedule](https://www.ibm.com/docs/en/db2oc?topic=task-unix-cron-format) or the **now** keyword, which will have your plan run once, as soon as possible.

#### Integrations

Select one or more [integrations](../guides/integrations.md) that will be used by the experiment to send data to other tools in your stack.

## Executions

Executions are a journal of the results of your experiment run. Each time one of your [experiments](#experiments) is run as part of a plan, an execution is generated and available in Reliably. It presents the execution's results and allows you to download a complete execution journal.

<p align=center><img src="/assets/images/concepts/executions/reliably-execution-example.png" alt="A screenshot of an execution page in Reliably." width="1324" /></p>

### Pause / Resume / Stop

If you're viewing a running experiment, action buttons Pause (or Resume) Execution and Stop Executions are available in the top right corner of the page. They will, as their name implies, allow you to Pause, Resume, or Stop the execution.

#### Pause Execution

Clicking the Pause Execution button will **send a pause signal** to Reliably. The execution status will immediately change to **Pausing...**

<p align=center><img src="/assets/images/concepts/executions/reliably-pausing.png" alt="" width="134" /></p>

At this stage, Reliably is waiting for the current <a href="/docs/glossary/#activity-experiment">activity</a> to finish, and it will then prevent the execution from continuing.

At the next update of the execution data, if the execution is effectively paused, its status will change to **Paused**.

Take into consideration that if you are running your execution in the Reliably Cloud you might be subject to an execution duration limit, depending on your pricing plan. The pause will still count toward your execution duration. For example, a free plan has a 10-minutes maximum duration. If you pause an execution after 8 minutes, a 2 minutes pause will cause the execution to be ended.

#### Resume Execution

If an execution is paused (or pausing), the Resume Execution button is displayed. Clicking the Resume Execution button will **send a resume signal** to Reliably. This signal will cause the execution to resume *almost* immediately.

#### Stop Execution

A running or paused execution can be stopped by clicking the Stop Execution button. When the button is clicked, a modal window will open to confirm your choice and allow you to choose if you want to skip rollbacks.

<p align=center><img src="/assets/images/concepts/executions/reliably-stop-execution-modal.png" alt="A modal window. The message reads: You are about to stop an execution. This action cannot be undone. You can choose to skip rollbacks, but be aware that even running them might leave your system in an unknown state. A checkbox allows to 'Terminate ungracefully'. Underneath are two buttons to Cancel or Stop Execution." width="486" /></p>

Clicking the Stop Execution button in the modal will **send a stop signal** to Reliably. The execution status will immediately change to **Stopping...**

<p align=center><img src="/assets/images/concepts/executions/reliably-stopping.png" alt="" width="147" /></p>

At this stage, Reliably is waiting for the current activity to finish, and it will then stop the execution. If the "Terminate ungracefully" box is left unchecked, the <a href="./glossary.md#rollbacks">rollbacks</a> will be executed.

At the next update of the execution data, if the execution is effectively stopped, its status will change to **Interrupted**.

### Run Info

At the top of the page is displayed the execution's unique UUID, as well as some general information about the execution:
- its status (here, our experiment deviated, meaning its result was not what was expected),
- when it ran,
- the name of the experiment (here, Latency remains under 200ms, which is one of our [starters](#starters)).

### Run Result

This section displays:

- the execution [status](./glossary.md#status-execution),
- if the execution [deviated](./glossary.md#deviation-execution),
- when the execution started,
- when the execution ended,
- the execution duration.

It also presents links to:

- the execution journal,
- the execution logs,
- the GitHub workflow page, if it was run as a GitHub Action

### Run Environment

This section presents information about the environment the Reliably experiment was run in.

- The version of the [Chaos Toolkit](https://chaostoolkit.org) library used
- Platform is the Operating System that was used
- Node is the name of the machine the experiment was run on

### Run Timeline

This Reliably timeline is a step-by-step breakdown of all the events that took place during an experiment execution.

It displays the main phases of the execution (steady-state hypothesis, method, rollbacks) as well as each activity that took place.

If an activity returns a result, this result is displayed in the event.

<p align=center><img src="/assets/images/concepts/executions/reliably-execution-timeline-events.png" alt="A screenshot showing two events in a timeline. The first event is the end of a probe activity. The probe is named measure-endpoint-response-time, and we can see it's tolerance was not met. The next event is the end of the steady-state hypothethis. It tells us the steady-state was not met, which is a consequence of the previous probe's tolerance not being met." width="1280" /></p>

Some activities, such as probes, can return more detailed results. If this is the case, a "Details" button reveals those results.

<p align=center><img src="/assets/images/concepts/executions/reliably-execution-timeline-event-details.png" alt="A screenshot showing the same first event as on the previous screenshot. The details section is opened and reveals the probe was successfully run, but it returned a value of 0.39 seconds, which is above the expected threshold of 200 ms" width="573" /></p>

## Deployments

Deployments are your way of telling Reliably how [plans](#plans) should be run and declaring required information.

### Deployment types

There are three types of deployment, each one associated with a way of running experiments.

| Deployment type | Usage |
| ----------------|-------|
| Reliably Cloud  | Reliably will run your plan in the Reliably Cloud |
| GitHub          | Reliably will run your plan as a GitHub Action in a GitHub workflow |
| Reliably CLI    | You will use the Reliably CLI to run your plan in your own environment, such as a CI/CD pipeline |
| Kubernetes      | Reliably will run your plan in your Kubernets cluster as a Kubernetes Job/CronJob |

The [How it Works](./how-it-works.md) page presents flowcharts for a more detailed view of the differences between running a plan with Reliably Cloud, GitHub, or the Reliably CLI.

### Create a deployment

#### GitHub

<p align=center>Creating a GitHub deployment will allow Reliably to create <a href="https://docs.github.com/en/actions" target="_blank" rel="noopener noreferer">GitHub Workflows <span class="screen-reader-text">External link will open in a new tab</span></a> on your behalf. These GitHub Workflows will then be used to install all the dependencies necessary to run the experiments on-demand, according to your [plans](#plans)</a>.</p>


!!! abstract

  Read more about the [architecture reference for GitHub deployment](./how-it-works.md#github-workflows).


<p align=center><img src="/assets/images/concepts/deployments/reliably-new-deployment-github.png" with="487" alt="A screenshot of the Reliably App, displaying the form the create a new GitHub deployment." width="490" /></p>

Creating a GitHub deployment requires the following information:

- A deployment name, which must be unique to your Reliably organization.
- The deployment type must be set to 'GitHub'.
- A GitHub repository, in the form of a **full** URL for the repository. _Example: github.com/my-org/my-repo_.
- The name of the GitHub environment for this repository where your secrets are stored. Environements are available in the 'Settings' section of the repository, and only available to repository collaborators with the right permissions.
- A <a href="https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token" target="_blank" rel="noopener noreferer">GitHub Token <span class="screen-reader-text">External link will open in a new tab</span></a> to access the repository.


#### Reliably CLI

Reliably CLI deployments are used to run plans with the Reliably CLI. Using the Reliably CLI allows you to run experiments from anywhere in your system.

!!! abstract

    Read more about the [architecture reference for Reliably CLI deployment](./how-it-works.md#on-premise-reliably-cli).


<p align=center><img src="/assets/images/concepts/deployments/reliably-new-deployment-cli.png" with="487" alt="A screenshot of the Reliably App, displaying the form the create a new Reliably CLI deployment." width="490" /></p>

Creating a Reliably CLI deployment requires the following information:

- A deployment name, which must be unique to your Reliably organization.
- The deployment type must be set to 'Reliably CLI'.

#### Kubernetes

Kubernetes deployments are used to run plans from any Kubernetes cluster directly.

!!! abstract

    Read more about the [architecture reference for Reliably Kubernetes deployment](./how-it-works.md#kubernetes).


<p align=center><img src="/assets/images/concepts/deployments/reliably-new-deployment-kubernetes.png" with="487" alt="A screenshot of the Reliably App, displaying the form the create a new Reliably Kubernetes deployment." width="490" /></p>

Creating a Reliably Kubernetes deployment requires the following information:

- A deployment name, which must be unique to your Reliably organization.
- The deployment type must be set to 'Reliably Kubernetes'.
- The namespace where to create the Kubernetes resources.
- The image exposing the [Reliably CLI](/docs/cli) as an entrypoint and no command arguments when using the default manifest.
- Either use a default Kubernetes Pod manifest to run the plan.
  Or, your own Kubernetes Pod manifest. The first container of the manifest must be using the image that will run the Reliably CLI.
- The Kubernetes credentials to connect to the cluster.

A few notes:

- You must create a Service Account in the target namespace. This service
  account will be attached to the Kubernetes Pod running the Plan
  ```yaml
    ---
    kind: ServiceAccount
    apiVersion: v1
    metadata:
        namespace: default
        name: reliably-job
    labels:
        app.kubernetes.io/name: reliably-job
    automountServiceAccountToken: false
    ```
- Make sure to bind the roles matching the expected operations carried by
  the Experiment.
- Reliably will create either Kubernetes Job or a Kubernetes Cron Job
  depending on if the plan uses a CRON schedule or not
- The Kubernetes Job/CronJob will then create the appropriate Kubernetes Pod
  to run the Plan
- The following labels will be set on the Kubernetes Job and Pod:
  * `reliably.com/plan` set to the Reliably Plan identifier
  * `reliably.com/org` set to the Reliably Organization
  * `app.kubernetes.io/managed-by` set to `reliably`
  * `app.kubernetes.io/component` set to `experiment`
  * `app.kubernetes.io/name` set to `plan-<PLAN_ID>`
- For AWS EKS clusters:
  - Reliably supports authenticating with the
[aws-iam-authenticator](https://docs.aws.amazon.com/eks/latest/userguide/install-aws-iam-authenticator.html).
  - Your credentials configuration must include the `AWS_ACCESS_KEY_ID` and 
    `AWS_SECRET_ACCESS_KEY` properties set in the `users.user.exec.env` section


## Environments

Environments allow you to store variables and encrypted secrets that will be used by the Reliably App, the Reliably CLI or GitHub workflows (see [How it works](how-it-works.md)).

### Create an environment

<p align=center>Navigate to {==the Environments page==} to view your existing environments and click on "New" to create a new one.</p>

<p align=center><img src="/assets/images/concepts/environments/reliably-new-environment-form.png" alt="A screenshot of the Environment creation form in the Reliably App. The form displays a text input to name the deployment and fields to add new variables and secrets" width="490" /></p>

#### Environment variables

Environment variables are key/value pairs used to store non-sensitive data.

#### Secrets

Secrets are encrypted variables used to store sensitive information, such as service accounts, tokens, etc.

There are two types of secrets:

- Variables are key/value pairs.
- Paths are designed to be used as files your experiment will read from. They're made of:
    - a path (like /home/svc/.chaostoolkit/integrations/c5ce...7fd80/sa.json),
    - the content of the file (as a string).


## Starters

<p align=center>Reliably's {==300+ starters==} allow you to run your first experiments and verifications in minutes.</p>

Starters are a selection of [probes](./glossary.md/#probe-experiment) and [actions](./glossary.md/#action-experiment) that you can turn into a full-fledged experiment by filling out a form in the UI and immediately added to a plan.

**Please note most actions and probes require an existing [environment](#environments) granting access to your environment variables and secrets.**

<p align=center><img src="/assets/images/concepts/starters/starters.png" alt="A screenshot of the Reliably starters list." width="655" /></p>

## Custom Templates

Custom templates allow you to provide your teammates with customizable experiments, that can be used in your organization with little to no configuration. It's like being able to create your own [starters](#starters).

<div class="media media--video" align=center>
  <iframe
    width="560"
    height="315"
    src="https://www.youtube.com/embed/LCs0rvTvEtA"
    title="Custom template creation and usage demo"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen></iframe>
</div>

### Creating a template

From the {==templates page==}, click the __New template__ button.

#### Upload an experiment

Then, you need to upload or paste a JSON file describing a Chaos Toolkit experiment.

<p align=center><img src="/assets/images/concepts/custom-templates/reliably-import-experiment.png" width="851" alt="Screenshot showing an experiment pasted in the Reliably UI" /></p>

This template must declare a `configuration` property. This property will allow Reliably to define which values will be made editable in the template.

Example of a `configuration` property in a JSON experiment.

```json
"configuration": {
  "reliably_latency": {
    "key": "RELIABLY_PARAM_LATENCY",
    "type": "env",
    "default": 0.2
  },
  "reliably_service_url": {
    "key": "RELIABLY_PARAM_SERVICE",
    "type": "env",
    "default": "https://example.com"
  }
}
```

#### Edit template metadata and fields.

Once the experiment has been uploaded, Reliably asks you to provide a title for your template, as well as optional labels. These labels will be used to allow users to search for specific templates.

<p align=center><img src="/assets/images/concepts/custom-templates/reliably-edit-metadata.png" width="548" alt="The UI for providing a title and labels" /></p>

Reliably will then present you with a field-description block for each entry in your `configuration` property.

<p align=center><img src="/assets/images/concepts/custom-templates/reliably-edit-template-field.png" width="1350" alt="The UI for describing a field that will be presented to users" /></p>

Each block consists of two sections. The left-hand side section is a form prompting you to provide a title for the field, the expected data type (string, number, boolean, or a JSON object), as well as an optional default value, and define if this data is required or optional. The right-hand side section displays a preview of the field as it will appear to users, as well as a reminder of the `configuration` item they will be overriding.

### Using a template

On the templates list page, select an existing template.

<p align=center><img src="/assets/images/concepts/custom-templates/reliably-templates-list.png" width="1336" alt="The list displays a single template, titled Simple Latency Verification" /></p>

You will then be brought to the template's detailed view, with its title, description and a preview of the editable fields.

<p align=center><img src="/assets/images/concepts/custom-templates/reliably-template-view.png" width="1357" alt="" /></p>

Clicking the **Create an experiment from this template** button will bring you to the experiment creation form.

<p align=center><img src="/assets/images/concepts/custom-templates/reliably-create-experiment-from-template.png" width="1352" alt="" /></p>

On this page, you can edit the experiment title, its description, and fill in the required data. After you click the __Save experiment__ button, the experiment will be visible in the {==experiments list==} and will be available for your [plans](#plans).
