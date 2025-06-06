# Scenario File Format

## Scenario Overview

A <span class="f">fault</span> scenario file is a structured document that defines a suite of tests
designed to simulate adverse network conditions and assess your application's
resilience.

At the top level, a scenario file contains metadata that provides context for
the entire test suite. This is followed by a collection of individual test
cases, each of which is known as a scenario item.

Each scenario item is composed of three primary components:

!!! info

    You can generate scenarios using the
    [fault scenario generate](../how-to/scenarios/generate.md) command.

**Call:**  
This section describes the HTTP request that will be executed during the test.
It specifies essential details such as the HTTP method
(for example, GET or POST), the target URL, and any headers or body content that
are required. Essentially, it outlines the action that triggers the fault
injection.

!!! question "Only HTTP?"

    <span class="f">fault</span> currently supports HTTP-based scenarios. In a future version, we may
    try to support more protocols.

**Context:**  
The context defines the environment in which the test runs. It lists the
upstream endpoints that will be affected by fault injection and specifies the
type of faults to simulate. Faults can include network latency, packet loss,
bandwidth restrictions, jitter, blackhole anomalies, or HTTP errors.
Additionally, an optional strategy can be included to repeat or vary the test
conditions systematically.

**Expectation:**  
This component sets the criteria for a successful test. It defines what outcomes
are acceptable by specifying expected HTTP status codes and performance metrics
like maximum response times. Alternatively, expectations can also be Servie
Level Objectives to verify. By clearly stating these expectations, the scenario
file provides a benchmark against which the test results can be measured.

The structured approach of a scenario file not only helps maintain consistency
across tests but also simplifies troubleshooting and iterative refinement. For
detailed information on individual fault parameters, refer to the relevant
definitions. This ensures that each test case is both precise and aligned with
your reliability objectives.

!!! example "A few scenarios to get a taste..."

    === "Basic scenario"

        ```yaml
        title: Single high-latency spike (client ingress)
        description: A single 800ms spike simulates jitter buffer underrun / GC pause on client network stack.
        items:
        - call:
            method: GET
            url: http://localhost:9090/
          context:
            upstreams:
            - http://localhost:9090/
            faults:
            - type: latency
              side: client
              mean: 800.0
              stddev: 100.0
              direction: ingress
          expect:
            status: 200
        ```

    === "Load test scenario with SLO"

        ```yaml
        title: 512 KBps bandwidth cap
        description: Models throttled 3G link; validates handling of large payloads.
        items:
        - call:
            method: POST
            url: http://localhost:9090/users/
            headers:
              content-type: application/json
            body: '{"name": "jane", "password": "boom"}'
            meta:
              operation_id: create_user_users__post
          context:
            upstreams:
            - http://localhost:9090
            faults:
            - type: bandwidth
              rate: 512
              unit: KBps
              direction: ingress
            strategy:
              mode: load
              duration: 15s
              clients: 2
              rps: 1
            slo:
            - slo_type: latency
              title: P95 < 300ms
              objective: 95.0
              threshold: 300.0
            - slo_type: error
              title: P99 < 1% errors
              objective: 99.0
              threshold: 1.0
          expect:
            status: 200
        ```

## Scenario Structure

### HTTP `call`

A file may contain many scenarios. They can be grouped however you need to
make sense of the results. For instance, one approach is to group them by
endpoint URL.

A scenario is made of at least one `call`. A `call` describes an endpoint, a
<span class="f">fault</span> context and optionally a block to verify expectations.

The `call` thus declares the HTTP configuration. The endpoint URL, a valid
HTTP method. Optional headers and body may also be provided.

Note that the a `call` block also supports a `meta` structure that allows you
to declare the `operation_id` (from [OpenAPI](https://swagger.io/docs/specification/v3_0/paths-and-operations/#operationid). This is a piece of information used by
the <span class="f">fault</span> agent when analyzing the scenario results.

### fault `context`

The `context` gathers the configuration for <span class="f">fault</span>. These are the typical
information <span class="f">fault</span>'s CLI uses already so you should be familiar with them
hopefully.

A list of `upstreams` servers which should be impacted by the network faults.
A sequence of `faults` applied during the run. Finally, a `strategy` block
describing how to run the scenario.

* No `strategy` block means a asingle shot call (e.g. a single HTTP request)
* A strategy with `mode` set to `repeat`. The scenario will be executed N
  iterations
* A strategy with `mode` set to `load`. The scenario will be executed for
  a duration with a given traffic.

Finally, the `context` may take a `slo` block that describes a list of
service level objectives (SLO). These SLOs are not meant to exist. They allow
you to declare what they might be for that endpoint (actually, they can
represent real SLOs but <span class="f">fault</span> doesn't link to them). These fake SLOs are useful
when running a `strategy` of type `load` because the report <span class="f">fault</span> generates
will give you feedback about them in the context of the scenario.

#### Running On a Platform

The default behavior is to execute scenarios locally in the current
`fault` process. Scenarios may be run on a different target. <span class="f">fault</span>
supports the following platforms:

* Kubernetes
* GCP (coming soon)
* AWS (coming soon)

To execute on a remote platform, use the `runs_on` property. When found, 
<span class="f">fault</span> creates the necessary resources on the platform and launch a dedicated
<span class="f">fault</span> instance to actually perform the injection of network faults.

##### Kubernetes

Here is an example to run a scenario as a Kubernetes job:

```yaml
context:
  runs_on:
    platform: kubernetes
    service: <service name>  # (1)!
    ns: default  # (2)!
    image: "ghcr.io/rebound-how/fault:latest"  # (3)!
```

1. The service to inject fault into
2. The namespace where this service is located
3. (optional) The default image used to launch the pod's fault. If you create your own image, make sure that `fault` remains the entrypoint

Read [about how fault injects itself into a Kubernetes cluster](./injection.md#kubernetes).

#### A word about SLO


fault advocates for practicing reliability and resilience as early and often
as possible. Both require constant attention to make an impact. To achieve this,
a team may be looking at implementing Site Reliability Engineering or SRE.

!!! question "What is SRE?"

    If you are interested in learning more about SRE, please check out the
    excellent [documentation](https://sre.google/) put out by Google on the
    topic.

One the tool coming from SRE is called
[Service Level Objective](https://sre.google/sre-book/service-level-objectives/)
or {==SLO==}. These provide a mechanism to decide how close a service is to
requiring attention. By defining a level of health for a service, a team has a
new capability called an error budget. Essentially, it's a room for a team to
bring change safely.

So, where does <span class="f">fault</span> come into this?

In the context of a <span class="f">fault</span> scenario, we can use SLO to help us figure out
if a particular combination of network faults might impact the health of our
service, and the extent of this impact.

!!! example "fault SLO definition"

    SLO are declared as part of the scenario's `context` and is a sequence of
    slo objects. For instance:

    ```yaml
      slo:
        - type: latency
          title: "P95 Latency < 110ms"
          objective: 95
          threshold: 110.0
        - type: latency
          title: "P99 Latency < 200ms"
          objective: 99
          threshold: 200.0
        - type: error
          title: "P98 Error Rate < 1%"
          objective: 98
          threshold: 1
    ```

    These SLO do not need to exist per-se. In other words, they aren't tied to
    any APM or monitoring tool. They simply express health service expectations.

    !!! note
    
        <span class="f">fault</span> supports two types of SLO: `latency` and `error`. 

When a scenario runs, <span class="f">fault</span> computes then a variety of latency and error
percentiles (p25, p50, p75, p95 and p99) to compare them with these SLO.

!!! example "fault SLO reporting"

    For instance, <span class="f">fault</span> may generate the following report:

    | Latency Percentile | Latency (ms) | Num. Requests (% of total) |
    |------------|--------------|-----------|
    | p25 | 394.95 | 16 (26.2%) |
    | p50 | 443.50 | 31 (50.8%) |
    | p75 | 548.39 | 47 (77.0%) |
    | p95 | 607.70 | 59 (96.7%) |
    | p99 | 636.84 | 61 (100.0%) |

    | SLO       | Pass? | Objective | Margin | Num. Requests Over Threshold (% of total) |
    |-----------|-------|-----------|--------|--------------------------|
    | P95 < 300ms | ❌ | 95% < 300ms | Above by 307.7ms | 55 (90.2%) |
    | P99 < 1% errors | ✅ | 99% < 1% | Below by 1.0 | 0 (0.0%) |

<span class="f">fault</span> is well aware that the window of the scenario is short. <span class="f">fault</span> takes
the view that even from such a small period of time, we can extrapolate valuable
information.

We believe <span class="f">fault</span> `slo` bridges SRE to developers. SLO is a simple language
which makes it explicit what a healthy service performs.

!!! info

    <span class="f">fault</span> is not an APM/monitoring tool, it doesn't aim at becoming one. A slo
    in the context of <span class="f">fault</span> is only a language to help developers see the world
    as their operations expect it to be.

### An `expect` block

The `expect` block defines how you want to verify the results from the `call`.

* `status` to match against the `call` response code (must be a valid HTTP code)
* `response_time_under` defines the ceiling of the `call` response's time

Note that, these two are ignored when `strategy` is set to `load`.

## Scenario Flow

<span class="f">fault</span> scenarios are self-contained and standalone in their execution. When
a scenario is executed, the proxy is configured with the appropriate fault
settings. Next <span class="f">fault</span> starts sending network traffic to the
scenario's target URL following the configured strategy. Then, <span class="f">fault</span>
compares results with the optional expectations or SLOs.

Once all the scenario items have been executed, <span class="f">fault</span> makes a final
report and writes to a markdown document.

## OpenAPI Support

<span class="f">fault</span> supports OpenAPI v3 (v3.0.x and v3.1.x). It may generate scenarios
from an OpenAPI specification to rapidly bootstrap your catalog of scenarios.

<span class="f">fault</span> scans an OpenAPI specification and gather the following information:

* the endpoint `url`
* the HTTP `method`
* if the method is either `POST` or `PUT`, it also scans the body definition.
  When this is a typical structured body, it creates a default payload as well.

Then <span class="f">fault</span> generates a variety of scenarios to create a solid baseline of
scenarios against each endpoint.

The default behavior from <span class="f">fault</span> is to create the following scenarios:

* **Single high-latency spike**: single short client ingress
* **Stair-step latency growth (5 x 100 ms)**: gradualy increase latency
* **Periodic 150-250 ms latency pulses during load**: load test 3 clients/2 rps
* **5% packet loss for 4s**: single shot egress
* **High jitter (±80ms @ 8Hz)**: single shot ingress
* **512 KBps bandwidth cap**: load test 2 clients/1 rps
* **Random 500 errors (5% of calls)**: load test 5 clients/4 rps
* **Full black-hole for 1s**: load test 2 clients/3 rps

!!! tip "Make it your own"

    A future version of <span class="f">fault</span> should allow you to bring your own scenario
    templates.

!!! tip "More coverage in the future"

    Right now, <span class="f">fault</span> generates scenarios against the endpoints themselves,
    a future release will also generate them for downstream dependencies.

## Example

The following example demonstrates a scenario file with many tests and their
expectations.

```yaml title="scenario.yaml"
title: Single high-latency spike (client ingress)
description: A single 800ms spike simulates jitter buffer underrun / GC pause on client network stack.
items:
- call:
    method: GET
    url: http://localhost:9090/
    meta:
      operation_id: read_root__get
  context:
    upstreams:
    - http://localhost:9090/
    faults:
    - type: latency
      side: client
      mean: 800.0
      stddev: 100.0
      direction: ingress
    strategy: null
  expect:
    status: 200
---
title: Stair-step latency growth (5 x 100 ms)
description: Latency increases 100 ms per call; emulate slow congestion build-up or head-of-line blocking.
items:
- call:
    method: GET
    url: http://localhost:9090/
    meta:
      operation_id: read_root__get
  context:
    upstreams:
    - http://localhost:9090/
    faults:
    - type: latency
      side: client
      mean: 100.0
      stddev: 30.0
      direction: ingress
    strategy:
      mode: repeat
      step: 100.0
      count: 5
      add_baseline_call: true
  expect:
    status: 200
---
title: Periodic 150-250 ms latency pulses during load
description: Three latency bursts at 10-40-70% of a 10s window; good for P95 drift tracking.
items:
- call:
    method: GET
    url: http://localhost:9090/
    meta:
      operation_id: read_root__get
  context:
    upstreams:
    - http://localhost:9090/
    faults:
    - type: latency
      mean: 150.0
      period: start:10%,duration:15%
    - type: latency
      mean: 250.0
      period: start:40%,duration:15%
    - type: latency
      mean: 150.0
      period: start:70%,duration:15%
    strategy:
      mode: load
      duration: 10s
      clients: 3
      rps: 2
    slo:
    - slo_type: latency
      title: P95 < 300ms
      objective: 95.0
      threshold: 300.0
    - slo_type: error
      title: P99 < 1% errors
      objective: 99.0
      threshold: 1.0
---
title: 5% packet loss for 4s
description: Simulates flaky Wi-Fi or cellular interference.
items:
- call:
    method: GET
    url: http://localhost:9090/
    timeout: 500
    meta:
      operation_id: read_root__get
  context:
    upstreams:
    - http://localhost:9090/
    faults:
    - type: packetloss
      direction: egress
      period: start:30%,duration:40%
    strategy: null
  expect:
    status: 200
    response_time_under: 100.0
---
title: High jitter (±80ms @ 8Hz)
description: Emulates bursty uplink, measuring buffering robustness.
items:
- call:
    method: GET
    url: http://localhost:9090/
    meta:
      operation_id: read_root__get
  context:
    upstreams:
    - http://localhost:9090/
    faults:
    - type: jitter
      amplitude: 80.0
      frequency: 8.0
      direction: ingress
      side: server
    strategy: null
  expect:
    status: 200
---
title: 512 KBps bandwidth cap
description: Models throttled 3G link; validates handling of large payloads.
items:
- call:
    method: GET
    url: http://localhost:9090/
    meta:
      operation_id: read_root__get
  context:
    upstreams:
    - http://localhost:9090/
    faults:
    - type: bandwidth
      rate: 512
      unit: KBps
      direction: ingress
    strategy:
      mode: load
      duration: 15s
      clients: 2
      rps: 1
  expect:
    status: 200
```

You can run this scenario file agains the demo server:

```bash
fault demo run
```

To execute the scenario file, run the following command:

```bash
fault scenario run --scenario scenario.yaml
```

## JSON Schema

Below is the full JSON schema of the scenario file:

```json title="scenario-schema.json"
{
  "$ref": "#/$defs/Scenario",
  "$defs": {
    "Scenario": {
      "title": "Scenario",
      "type": "object",
      "properties": {
        "title": {
          "type": "string"
        },
        "description": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ]
        },
        "scenarios": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/ScenarioItem"
          }
        },
        "config": {
          "anyOf": [
            {
              "type": "null"
            },
            {
              "$ref": "#/$defs/ScenarioGlobalConfig"
            }
          ],
          "default": null
        }
      },
      "required": [
        "title",
        "description",
        "scenarios"
      ]
    },
    "ScenarioItem": {
      "title": "ScenarioItem",
      "type": "object",
      "properties": {
        "call": {
          "$ref": "#/$defs/ScenarioItemCall"
        },
        "context": {
          "$ref": "#/$defs/ScenarioItemContext"
        },
        "expect": {
          "anyOf": [
            {
              "type": "null"
            },
            {
              "$ref": "#/$defs/ScenarioItemExpectation"
            }
          ],
          "default": null
        }
      },
      "required": [
        "call",
        "context"
      ]
    },
    "ScenarioItemCall": {
      "title": "ScenarioItemCall",
      "type": "object",
      "properties": {
        "method": {
          "type": "string"
        },
        "url": {
          "type": "string"
        },
        "headers": {
          "anyOf": [
            {
              "type": "object",
              "additionalProperties": {
                "type": "string"
              }
            },
            {
              "type": "null"
            }
          ]
        },
        "body": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ]
        },
        "timeout": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "meta": {
          "anyOf": [
            {
              "type": "null"
            },
            {
              "$ref": "#/$defs/ScenarioItemCallOpenAPIMeta"
            }
          ],
          "default": null
        }
      },
      "required": [
        "method",
        "url",
        "headers",
        "body"
      ]
    },
    "ScenarioItemCallOpenAPIMeta": {
      "title": "ScenarioItemCallOpenAPIMeta",
      "type": "object",
      "properties": {
        "operation_id": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": []
    },
    "ScenarioItemContext": {
      "title": "ScenarioItemContext",
      "type": "object",
      "properties": {
        "upstreams": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "faults": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/FaultConfiguration"
          }
        },
        "strategy": {
          "anyOf": [
            {
              "type": "null"
            },
            {
              "anyOf": [
                {
                  "$ref": "#/$defs/ScenarioRepeatItemCallStrategy"
                },
                {
                  "$ref": "#/$defs/ScenarioLoadItemCallStrategy"
                }
              ],
              "discriminator": {
                "propertyName": "type",
                "mapping": {
                  "ScenarioRepeatItemCallStrategy": "#/$defs/ScenarioRepeatItemCallStrategy",
                  "ScenarioLoadItemCallStrategy": "#/$defs/ScenarioLoadItemCallStrategy"
                }
              }
            }
          ]
        },
        "slo": {
          "anyOf": [
            {
              "type": "array",
              "items": {
                "$ref": "#/$defs/ScenarioItemSLO"
              }
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": [
        "upstreams",
        "faults",
        "strategy"
      ]
    },
    "FaultConfiguration": {
      "title": "FaultConfiguration",
      "type": "object",
      "properties": {
        "Latency": {
          "$ref": "#/$defs/Latency"
        },
        "PacketLoss": {
          "$ref": "#/$defs/PacketLoss"
        },
        "Bandwidth": {
          "$ref": "#/$defs/Bandwidth"
        },
        "Jitter": {
          "$ref": "#/$defs/Jitter"
        },
        "Blackhole": {
          "$ref": "#/$defs/Blackhole"
        },
        "HttpError": {
          "$ref": "#/$defs/HttpError"
        }
      },
      "required": [
        "Latency",
        "PacketLoss",
        "Bandwidth",
        "Jitter",
        "Blackhole",
        "HttpError"
      ]
    },
    "Latency": {
      "title": "Latency",
      "type": "object",
      "properties": {
        "distribution": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ]
        },
        "global_": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ]
        },
        "mean": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "stddev": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "min": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "max": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "shape": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "scale": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "side": {
          "anyOf": [
            {
              "enum": [
                "client",
                "server"
              ]
            },
            {
              "type": "null"
            }
          ],
          "default": "server"
        },
        "direction": {
          "anyOf": [
            {
              "enum": [
                "egress",
                "ingress"
              ]
            },
            {
              "type": "null"
            }
          ],
          "default": "ingress"
        },
        "sched": {
          "anyOf": [
            {
              "type": "string",
              "pattern": "(?:start:\\s*(\\d+s|\\d+m|\\d+%)(?:,)?;?)*(?:duration:\\s*(\\d+s|\\d+m|\\d+%)(?:,)?;?)*"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": [
        "distribution",
        "global_",
        "mean",
        "stddev",
        "min",
        "max",
        "shape",
        "scale"
      ]
    },
    "PacketLoss": {
      "title": "PacketLoss",
      "type": "object",
      "properties": {
        "side": {
          "anyOf": [
            {
              "enum": [
                "client",
                "server"
              ]
            },
            {
              "type": "null"
            }
          ],
          "default": "server"
        },
        "direction": {
          "anyOf": [
            {
              "enum": [
                "egress",
                "ingress"
              ]
            },
            {
              "type": "null"
            }
          ],
          "default": "ingress"
        },
        "sched": {
          "anyOf": [
            {
              "type": "string",
              "pattern": "(?:start:\\s*(\\d+s|\\d+m|\\d+%)(?:,)?;?)*(?:duration:\\s*(\\d+s|\\d+m|\\d+%)(?:,)?;?)*"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": []
    },
    "Bandwidth": {
      "title": "Bandwidth",
      "type": "object",
      "properties": {
        "rate": {
          "type": "integer",
          "minimum": 0,
          "default": 1000
        },
        "unit": {
          "enum": [
            "bps",
            "gbps",
            "kbps",
            "mbps"
          ],
          "default": "bps"
        },
        "side": {
          "anyOf": [
            {
              "enum": [
                "client",
                "server"
              ]
            },
            {
              "type": "null"
            }
          ],
          "default": "server"
        },
        "direction": {
          "anyOf": [
            {
              "enum": [
                "egress",
                "ingress"
              ]
            },
            {
              "type": "null"
            }
          ],
          "default": "ingress"
        },
        "sched": {
          "anyOf": [
            {
              "type": "string",
              "pattern": "(?:start:\\s*(\\d+s|\\d+m|\\d+%)(?:,)?;?)*(?:duration:\\s*(\\d+s|\\d+m|\\d+%)(?:,)?;?)*"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": []
    },
    "Jitter": {
      "title": "Jitter",
      "type": "object",
      "properties": {
        "amplitude": {
          "type": "number",
          "minimum": 0.0,
          "default": 20.0
        },
        "frequency": {
          "type": "number",
          "minimum": 0.0,
          "default": 5.0
        },
        "side": {
          "anyOf": [
            {
              "enum": [
                "client",
                "server"
              ]
            },
            {
              "type": "null"
            }
          ],
          "default": "server"
        },
        "direction": {
          "anyOf": [
            {
              "enum": [
                "egress",
                "ingress"
              ]
            },
            {
              "type": "null"
            }
          ],
          "default": "ingress"
        },
        "sched": {
          "anyOf": [
            {
              "type": "string",
              "pattern": "(?:start:\\s*(\\d+s|\\d+m|\\d+%)(?:,)?;?)*(?:duration:\\s*(\\d+s|\\d+m|\\d+%)(?:,)?;?)*"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": []
    },
    "Blackhole": {
      "title": "Blackhole",
      "type": "object",
      "properties": {
        "direction": {
          "enum": [
            "egress",
            "ingress"
          ],
          "default": "egress"
        },
        "side": {
          "anyOf": [
            {
              "enum": [
                "client",
                "server"
              ]
            },
            {
              "type": "null"
            }
          ],
          "default": "server"
        }
      },
      "required": []
    },
    "HttpError": {
      "title": "HttpError",
      "type": "object",
      "properties": {
        "body": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ]
        },
        "status_code": {
          "$ref": "#/$defs/HTTPStatus",
          "default": 500
        },
        "probability": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "default": 1.0
        }
      },
      "required": [
        "body"
      ]
    },
    "HTTPStatus": {
      "title": "HTTPStatus",
      "description": "",
      "enum": [
        100,
        101,
        102,
        103,
        200,
        201,
        202,
        203,
        204,
        205,
        206,
        207,
        208,
        226,
        300,
        301,
        302,
        303,
        304,
        305,
        307,
        308,
        400,
        401,
        402,
        403,
        404,
        405,
        406,
        407,
        408,
        409,
        410,
        411,
        412,
        413,
        414,
        415,
        416,
        417,
        418,
        421,
        422,
        423,
        424,
        425,
        426,
        428,
        429,
        431,
        451,
        500,
        501,
        502,
        503,
        504,
        505,
        506,
        507,
        508,
        510,
        511
      ]
    },
    "ScenarioRepeatItemCallStrategy": {
      "title": "ScenarioRepeatItemCallStrategy",
      "type": "object",
      "properties": {
        "type": {
          "enum": [
            "ScenarioRepeatItemCallStrategy"
          ]
        },
        "mode": {
          "enum": [
            "repeat"
          ]
        },
        "step": {
          "type": "number",
          "minimum": 0.0
        },
        "failfast": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ]
        },
        "wait": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        },
        "add_baseline_call": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ]
        },
        "count": {
          "type": "integer",
          "minimum": 0,
          "default": 0
        }
      },
      "required": [
        "type",
        "mode",
        "step",
        "failfast",
        "wait",
        "add_baseline_call"
      ]
    },
    "ScenarioLoadItemCallStrategy": {
      "title": "ScenarioLoadItemCallStrategy",
      "type": "object",
      "properties": {
        "type": {
          "enum": [
            "ScenarioLoadItemCallStrategy"
          ]
        },
        "mode": {
          "enum": [
            "load"
          ]
        },
        "duration": {
          "type": "string"
        },
        "clients": {
          "type": "integer",
          "minimum": 0
        },
        "rps": {
          "type": "integer",
          "minimum": 0
        }
      },
      "required": [
        "type",
        "mode",
        "duration",
        "clients",
        "rps"
      ]
    },
    "ScenarioItemSLO": {
      "title": "ScenarioItemSLO",
      "type": "object",
      "properties": {
        "type": {
          "type": "string"
        },
        "title": {
          "type": "string"
        },
        "objective": {
          "type": "number"
        },
        "threshold": {
          "type": "number"
        }
      },
      "required": [
        "type",
        "title",
        "objective",
        "threshold"
      ]
    },
    "ScenarioItemExpectation": {
      "title": "ScenarioItemExpectation",
      "type": "object",
      "properties": {
        "status": {
          "anyOf": [
            {
              "type": "integer",
              "minimum": 0
            },
            {
              "type": "null"
            }
          ]
        },
        "response_time_under": {
          "anyOf": [
            {
              "type": "number",
              "minimum": 0.0
            },
            {
              "type": "null"
            }
          ]
        }
      },
      "required": [
        "status",
        "response_time_under"
      ]
    },
    "ScenarioGlobalConfig": {
      "title": "ScenarioGlobalConfig",
      "type": "object",
      "properties": {
        "http": {
          "anyOf": [
            {
              "type": "null"
            },
            {
              "$ref": "#/$defs/ScenarioHTTPGlobalConfig"
            }
          ],
          "default": null
        }
      },
      "required": []
    },
    "ScenarioHTTPGlobalConfig": {
      "title": "ScenarioHTTPGlobalConfig",
      "type": "object",
      "properties": {
        "headers": {
          "type": "object",
          "additionalProperties": {
            "type": "string"
          }
        },
        "paths": {
          "anyOf": [
            {
              "type": "null"
            },
            {
              "$ref": "#/$defs/HTTPPathsConfig"
            }
          ],
          "default": null
        }
      },
      "required": [
        "headers"
      ]
    },
    "HTTPPathsConfig": {
      "title": "HTTPPathsConfig",
      "type": "object",
      "properties": {
        "segments": {
          "type": "object",
          "additionalProperties": {
            "type": "string"
          }
        }
      },
      "required": [
        "segments"
      ]
    }
  }
}
```

## Next Steps

- **Learn how to [generate](../how-to/scenarios/generate.md)** scenarios.
