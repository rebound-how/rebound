# Integrate With Your Operations

This guide goes into the details of creating and using Reliably Integrations.

A Reliably Plan executes activities implementing the scenario
described by the Reliably Experiments of the plan. It is often pertinent to
let perform tasks while the execution takes place, to cover scenarios such as:

* sending events to your observability platform
* controlling the execution so that it terminates in case of system's specific
  condition
* make the run visible via platforms like Slack

and many other use cases that allow you to integrate Reliably into your
operations.

## The Basics

### Create an Integration

!!! info

    Unlike Reliably Environments, Reliably Integrations work with any Reliably
    Deployment type.


To create an integration, go to the
{==New integration==} page and start
filling the form as needed.

Provide a name that you can easily recall what it covers later on. Then fill
the requested parameters. Integrations are then available to be used in Reliably
Plans.

### Delete an Integration

You can delete integrations at will but only when all Reliably Plan that
use them have also been deleted first. This prevents mistakes where a Plan
tries to run and cannot find its integration.

## Configure Integrations

This section will review how to configure all integrations provided by Reliably.

### Slack

The Reliably Integration for Slack creates a Slack thread in a channel of your
choice. That thread contains all events of the execution of the experiment
in near real-time. Messages contain the result of each activity so you can
review where the action is at and its status as it runs.

| Field                    | Value |
| ------------------------ | ----- |
| `name`                   | The integration name. Make it specific so you can easily differentiate it when creating many of the same type. |
| `channel`                | The Slack channel where to send messages to. The Slack app must be invited into that channel first. |
| `token`                  | The Slack token of the Slack application enabled in the Slack workspace for the integration. |


??? note "Slack Credentials"

    To enable the Reliably Integration for Slack, you need to first create
    a [Slack application](https://api.slack.com/apps?new_app=1) and enable it in
    your Slack Workspace. Please, read more about how this is done on the
    [Slack documentation](https://app.slack.com/tutorials).

    The application should have the following scopes:

    * `channels:read`
    * `chat:write`
    * `file:write`

    We suggest you name it `Reliably` to make it clear to your users.


### Honeycomb

The Reliably Integration for Honeycomb uses the
[Open Telemetry](https://opentelemetry.io) protocol to send traces to
[Honeycomb](https://www.honeycomb.io) while the experiment is running.

| Field                    | Value |
| ------------------------ | ----- |
| `name`                   | The integration name. Make it specific so you can easily differentiate it when creating many of the same type. |
| `traces endpoint`        | The Honeycomb Open Telemetry traces endpoint. Usually `https://api.honeycomb.io/v1/traces`. |
| `api key`                | The Honeycomb API key using the format `x-honeycomb-team=your-api-key`. |

### Dynatrace

The Reliably Integration for [Dynatrace](https://www.dynatrace.com) uses the
[Open Telemetry](https://opentelemetry.io) protocol to send traces to
Dynatrace while the experiment is running. Please review Dynatrace
[documentation](https://www.dynatrace.com/support/help/extend-dynatrace/opentelemetry/opentelemetry-traces/opentelemetry-ingest)
for more information.

| Field                    | Value |
| ------------------------ | ----- |
| `name`                   | The integration name. Make it specific so you can easily differentiate it when creating many of the same type. |
| `traces endpoint`        | The Dynatrace Open Telemetry traces endpoint. Usually `https://{your-environment-id}.live.dynatrace.com/api/v2/oltp/v1/traces`. |
| `api token`              | The Dynatrace API token with the scope to send traces: `openTelemetryTrace.ingest`. |


### Google Cloud Platform

The Reliably Integration for [GCP](https://cloud.google.com) uses the
[Open Telemetry](https://opentelemetry.io) protocol to send traces to
GCP while the experiment is running.

| Field                    | Value |
| ------------------------ | ----- |
| `name`                   | The integration name. Make it specific so you can easily differentiate it when creating many of the same type. |
| `service account`        | The GCP service account which has the `roles/cloudtrace.agent` role to send OpenTelemetry traces. |


### Grafana

The Reliably Integration for [Grafana](https://grafana.com/)
uses the [Open Telemetry](https://opentelemetry.io) protocol to send traces to
Grafana Tempo while the experiment is running. Please review Grafana OTLP
[documentation](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/otlp/send-data-otlp/)
for more information.

| Field                    | Value |
| ------------------------ | ----- |
| `name`                   | The integration name. Make it specific so you can easily differentiate it when creating many of the same type. |
| `traces endpoint`        | The Grafana Open Telemetry traces endpoint. Usually `https://otlp-gateway-<zone>.grafana.net/otlp/v1/traces`. |
| `username`               | The Grafana instance ID from the details page. |
| `password`               | The Grafana access policy token. |

### OpenAI ChatGPT

The OpenAI ChatGPT Integration automatically pulls information about your
experiment once it's finished. The goal is to offer context of what other
aspect of the system you should be paying attention to.


| Field                    | Value |
| ------------------------ | ----- |
| `name`                   | The integration name. Make it specific so you can easily differentiate it when creating many of the same type. |
| `model`                  | The ChatGPT model to use. |
| `key`                    | Your OpenAI key. |
| `org`                    | Your OpenAI organization identifier. |

!!! warning

    We recommend you do not enable this integration on plans with a recurring
    schedule. This would generate likely the same output and would consume quite
    a lot of your tokens. Instead use it one plans using the schedule `now`.


### Reliably Pre-checks

The Reliably Pre-checks Integration offers a mechanism to verify some
pre-conditions before the experiment is allows to run. If these pre-conditions
are not met, the execution is interrupted and terminated.

This integration is useful if you need to ensure operational properties of
your system so the experiment does not run in conditions that could lead
to potential issues of the system.

<div class="markdown-tip">

If you are familiar with the steady-state hypothesis concept of the experiment
itself, you may feel these pre-checks are redundant. In fact, they use the
same approach but have a different purpose. The hypothesis of the experiment
is part of the experiment's definition itself and uses to inform us how a
specific change, or turbulence, can impact this hypothesis. The pre-checks
are operational gates that decide whether it's safe to execute the experiment
and does not make any assumption about the experiment itself.

</div>


| Field                    | Value |
| ------------------------ | ----- |
| `name`                   | The integration name. Make it specific so you can easily differentiate it when creating many of the same type. |
| `pre-check endpoint`     | The URL called during pre-checks to make the decision of interrupting the execution before it starts. The endpoint must return a JSON payload of the form `{"ok": true/false, "reason": "Reason when ok property is false"}`. When the `ok` field is `false`, the execution is interrupted. Any response with a status code different from `200` will be considered as an interruption as well. |
| `token`                  | If the endpoint is protected by a bearer token, provide it as well |
| `credentials file`       | If the endpoint is protected and requires a service account (GCP) or a credentials file (AWS), provide its content |


### Reliably Safeguards

The Reliably Safeguards Integration offers a mechanism to verify the operational
safety of executing the experiment as it occurs. If the conditions
are not met, the execution is interrupted and terminated.

This integration is useful if you need to ensure operational properties of
your system so the experiment does not run in conditions that could lead
to potential issues of the system while it executes.

| Field                    | Value |
| ------------------------ | ----- |
| `name`                   | The integration name. Make it specific so you can easily differentiate it when creating many of the same type. |
| `safeguard endpoint`     | The URL called during the execution of the experiment to make the decision of interrupting the execution. The endpoint must return a JSON payload of the form `{"ok": true/false, "reason": "Reason when ok property is false"}`. When the `ok` field is `false`, the execution is interrupted. Any response with a status code different from `200` will be considered as an interruption as well. |
| `frequency`              | The frequency at which the endpoint should be called. |
| `token`                  | If the endpoint is protected by a bearer token, provide it as well |
| `credentials file`       | If the endpoint is protected and requires a service account (GCP) or a credentials file (AWS), provide its content |


### Reliably Auto-pause

The Reliably Auto-pause Integration offers a mechanism to pause the execution
after each activity. Pauses can be resumed manually from the execution
page.

Pauses are useful when you want to investigate the system as the experiment
takes place.


| Field                    | Value |
| ------------------------ | ----- |
| `name`                   | The integration name. Make it specific so you can easily differentiate it when creating many of the same type. |
| `strategy`               | The strategy of pauses: before or after each activities in the method |

Pauses lasts as long as your Billing Plan offers.


