# Creating a Reliability Testing Scenario

## Introduction

**Context**:  

  Modern applications are not running in isolation. Whether it is a distributed
  file system, a database or a remote API, applications depend on network to
  be reliable and fast.

  Understanding how an application reacts under network duress is prime to build
  more resilient systems overall.
  
**Goal**:

  By the end of this tutorial, you will:

  - Configure fault to apply latency.
  - Run a defined scenario that systematically applies this fault.
  - Observe the application’s behavior and interpret the resulting report.

## Prerequisites

**Tools & Setup**:

  - fault [installed](../how-to/install.md) on your local machine.
  - An existing application or a simple test client that makes calls to a known
    third-party endpoint (e.g., `https://api.example.com`).
  - Basic familiarity with setting `HTTP_PROXY` or `HTTPS_PROXY` environment
    variables.
  
**Assumptions**:  
  The tutorial assumes you have followed the
  [Getting Started](./getting-started.md) tutorial and understand how to launch
  fault proxy.

## Step 1: Choosing the Third-Party Endpoint

Before simulating any faults, it’s essential to establish a reliable baseline.
This step ensures that your application can communicate successfully with a
stable API, so you know that any issues observed later are truly due to the
injected faults.

### How to Pick a Stable Endpoint

- **Reachability:**  
  fault supports HTTP/1.1 and HTTP/2 only. If your endpoint only responds to
  HTTP/3, fault cannot work with it.
  
- **Consistency:**  
  Select an endpoint known for its consistency. A public API that rarely experiences
  downtime is ideal.
  
- **Predictability:**  
  The endpoint should return predictable responses, making it easier to spot the impact
  of any simulated network faults.

For demonstration purposes, use `http://localhost:7070`.

## Step 2: Creating a Scenario File

In this step, you'll create a scenario file in YAML that defines a series of
tests. Each scenario acts like a mini-test case, telling fault exactly how to
simulate network faults and what to expect from your application. This file is
your blueprint for reliability engineering.

Follow these steps to build your scenario file:

### Define User-Centric Metadata

- **Title:**  
  Every scenario starts with a clear title. This gives you a quick reference for
  what the test is about.
- **Description:**  
  Optionally, add a short description for extra context about the scenario.

  Example:

  ```yaml
  ---
  title: "Latency Increase By 30ms Steps From Downstream"
  description: "A collection of tests to evaluate how our service handles network faults."
  ```

### Define a Scenario Test

Each item in the scenarios array represents one test case. It must contain three
parts:

**Call:**

This section defines the HTTP request that fault will make.

- `method`: The HTTP method (GET, POST, etc.).
- `url`: The full URL to call.
- `headers`: An object with header key-value pairs (if needed).
- `body`: The request payload (if needed).

  ```yaml
  call:
    method: GET
    url: http://localhost:7070/ping
  ```

**Context:**

This section tells fault which upstream services are involved and which faults
to inject.

- `upstreams`: An array of endpoints (as strings) where faults should be applied.
- `faults`: An array of fault configurations. The JSON schema defines the
  structure for each fault type (Latency, PacketLoss, Bandwidth, etc.).
- `strategy`: (Optional) Defines how to repeat the test with incremental changes
  (for example, gradually increasing latency).

  ```yaml
  context:
    upstreams:
      - https://postman-echo.com
    faults:
      - type: latency
        mean: 80
        stddev: 5
        direction: ingress
        side: server
    strategy:
      mode: repeat
      step: 30
      count: 3
      add_baseline_call: true
  ```

The `add_baseline_call` property is useful when you want to make a first call
to your application without applying any faults. This provides a very basic
baseline record of your application in normal conditions.

The test declares that traffic going to upstream `https://postman-echo.com`
will be routed to the proxy and that latency will be applied to ingress traffic
from this endpoint.

!!! note

    The reason we are using this server here is because the demo application
    provided by fault makes a call to it when the `/ping` endpoint is called.

**Expect:**

This section specifies the criteria that determine whether the test has passed.

`status`: The expected HTTP status code (or null).
`response_time_under`: The maximum allowed response time (in milliseconds).

  ```yaml
  expect:
    status: 200
    response_time_under: 490
  ```

**Putting it all together:**

  ```yaml
  ---
  title: "Latency Increase By 30ms Steps From Downstream"
  description: "A collection of tests to evaluate how our service handles network faults."
  items:
    - call:
        method: GET
        url: http://localhost:7070/ping
      context:
        upstreams:
          - https://postman-echo.com
        faults:
          - type: latency
            mean: 80
            stddev: 5
            direction: ingress
            side: server
        strategy:
          mode: repeat
          step: 30
          count: 3
          add_baseline_call: true
      expect:
        status: 200
        response_time_under: 490
  ```


## Step 3: Configuring Your Application and Environment

Before running your fault injection scenarios, it's crucial to ensure that
traffic to and from your application is routed via fault's proxy.

### Set the Proxy Environment Variable

Configure your environment so that all HTTPS traffic is routed through fault.
This is typically done by setting the `HTTP_PROXY`  and/or `HTTPS_PROXY`
environment variable to point to fault's proxy endpoint.

- **On Linux/MacOS/Windows (WSL):**

  ```bash
  export HTTP_PROXY=http://127.0.0.1:3180
  export HTTPS_PROXY=http://127.0.0.1:3180
  ```

- **On Windows:**

  ```command
  set HTTP_PROXY=http://127.0.0.1:3180
  set HTTPS_PROXY=http://127.0.0.1:3180
  ```

  or using Powershell:

  ```powershell
  $env:HTTP_PROXY = "http://127.0.0.1:3180"
  $env:HTTPS_PROXY = "http://127.0.0.1:3180"
  ```

## Step 4: Running the Scenario

Now that you’ve defined your scenarios and configured your environment,
it’s time to run the tests and see fault in action.

### Run the Scenario

Execute the following command in your terminal:

```bash
fault scenario run --scenario scenario.yaml
```

!!! tip

    You may pass a directory instead of a single file, fault will process all
    of them as part of a single run.

Here is the output of the run:

```console
================ Running Scenarios ================

⠦  4/4  [00:00:01] Latency Increase By 30ms Steps From Downstream ▮▮▮▮ [GET http://localhost:7070/ping]

===================== Summary =====================

Tests run: 4, Tests failed: 1
Total time: 1.9s

Report saved as report.json
```

!!! note

    We have 4 iterations even though we set the iteration count to `3` in the
    scenario. This is due to the fact we also added a baseline call first with
    the parameter `add_baseline_call: true`.

### What’s Happening Behind the Scenes

**Proxy Launch:**

- fault starts a local proxy server (by default at `http://127.0.0.1:3180`) to
intercept and manipulate network traffic.

**Fault Injection:**

- For each test defined in your scenario file, fault applies the specified
  network faults.

**Metrics and Logging:**

- As the tests run, fault captures detailed metrics (like response times,
  status codes, and error occurrences) along with logs. All this data is then
  saved to `scenario-report.json` for later analysis.

## Step 5: Observing Logs and Output

fault records metrics while running the scenario. You can use this information
to analyse the way your application reacted to increasingly degraded network
conditions.

fault produces two files:

- `results.json` Represents the structured log of the scenario execution.
  Notably, it shows the faults as they were applied
- `report.json` Represents an automated analysis of the run. fault applies some
  heuristics to evaluate what would be the impact on a variety of service-level
  objectives (SLO)

### Run Metrics

Here is an example of `results.json` file:

```json
{
  "start": 1747072156,
  "end": 1747072158,
  "results": [
    {
      "scenario": {
        "title": "Latency Increase By 30ms Steps From Downstream",
        "description": "A collection of tests to evaluate how our service handles network faults.",
        "items": [
          {
            "call": {
              "method": "GET",
              "url": "http://localhost:7070/ping"
            },
            "context": {
              "upstreams": [
                "https://postman-echo.com"
              ],
              "faults": [
                {
                  "type": "latency",
                  "side": "server",
                  "mean": 80.0,
                  "stddev": 5.0,
                  "direction": "ingress"
                }
              ],
              "strategy": {
                "mode": "repeat",
                "step": 30.0,
                "count": 3,
                "add_baseline_call": true
              }
            },
            "expect": {
              "status": 200,
              "response_time_under": 490.0
            }
          }
        ]
      },
      "results": [
        {
          "target": {
            "address": "http://localhost:7070/ping"
          },
          "results": [
            {
              "start": 1747072156512117,
              "expect": {
                "type": "http",
                "wanted": {
                  "status_code": 200,
                  "response_time_under": 490.0,
                  "all_slo_are_valid": null
                },
                "got": {
                  "status_code": 200,
                  "response_time": 462.121729,
                  "all_slo_are_valid": null,
                  "decision": "success"
                }
              },
              "metrics": {
                "dns": [
                  {
                    "host": "localhost",
                    "duration": 0.095075,
                    "resolved": true
                  }
                ],
                "protocol": {
                  "type": "http",
                  "code": 200,
                  "body_length": 308
                },
                "ttfb": 0.00177,
                "total_time": 462.121729,
                "faults": [
                  {
                    "url": "localhost:7070",
                    "applied": [
                      {
                        "event": {
                          "type": "latency",
                          "direction": "ingress",
                          "side": "client",
                          "delay": 84.615696
                        }
                      }
                    ]
                  }
                ],
                "errored": false,
                "timed_out": false
              },
              "faults": [
                {
                  "type": "latency",
                  "side": "client",
                  "mean": 80.0,
                  "stddev": 5.0,
                  "direction": "ingress"
                }
              ],
              "errors": []
            },
            {
              "start": 1747072156987144,
              "expect": {
                "type": "http",
                "wanted": {
                  "status_code": 200,
                  "response_time_under": 490.0,
                  "all_slo_are_valid": null
                },
                "got": {
                  "status_code": 200,
                  "response_time": 460.167284,
                  "all_slo_are_valid": null,
                  "decision": "success"
                }
              },
              "metrics": {
                "dns": [
                  {
                    "host": "localhost",
                    "duration": 0.050846,
                    "resolved": true
                  }
                ],
                "protocol": {
                  "type": "http",
                  "code": 200,
                  "body_length": 308
                },
                "ttfb": 0.003175,
                "total_time": 460.167284,
                "faults": [
                  {
                    "url": "localhost:7070",
                    "applied": [
                      {
                        "event": {
                          "type": "latency",
                          "direction": "ingress",
                          "side": "client",
                          "delay": 77.726423
                        }
                      }
                    ]
                  }
                ],
                "errored": false,
                "timed_out": false
              },
              "faults": [
                {
                  "type": "latency",
                  "side": "client",
                  "mean": 80.0,
                  "stddev": 5.0,
                  "direction": "ingress"
                }
              ],
              "errors": []
            },
            {
              "start": 1747072157452249,
              "expect": {
                "type": "http",
                "wanted": {
                  "status_code": 200,
                  "response_time_under": 490.0,
                  "all_slo_are_valid": null
                },
                "got": {
                  "status_code": 200,
                  "response_time": 448.75748,
                  "all_slo_are_valid": null,
                  "decision": "success"
                }
              },
              "metrics": {
                "dns": [
                  {
                    "host": "localhost",
                    "duration": 0.051273,
                    "resolved": true
                  }
                ],
                "protocol": {
                  "type": "http",
                  "code": 200,
                  "body_length": 307
                },
                "ttfb": 0.003145,
                "total_time": 448.75748,
                "faults": [
                  {
                    "url": "localhost:7070",
                    "applied": [
                      {
                        "event": {
                          "type": "latency",
                          "direction": "ingress",
                          "side": "client",
                          "delay": 72.084749
                        }
                      }
                    ]
                  }
                ],
                "errored": false,
                "timed_out": false
              },
              "faults": [
                {
                  "type": "latency",
                  "side": "client",
                  "mean": 80.0,
                  "stddev": 5.0,
                  "direction": "ingress"
                }
              ],
              "errors": []
            },
            {
              "start": 1747072157910258,
              "expect": {
                "type": "http",
                "wanted": {
                  "status_code": 200,
                  "response_time_under": 490.0,
                  "all_slo_are_valid": null
                },
                "got": {
                  "status_code": 200,
                  "response_time": 479.741817,
                  "all_slo_are_valid": null,
                  "decision": "success"
                }
              },
              "metrics": {
                "dns": [
                  {
                    "host": "localhost",
                    "duration": 0.078204,
                    "resolved": true
                  }
                ],
                "protocol": {
                  "type": "http",
                  "code": 200,
                  "body_length": 308
                },
                "ttfb": 0.002776,
                "total_time": 479.741817,
                "faults": [
                  {
                    "url": "localhost:7070",
                    "applied": [
                      {
                        "event": {
                          "type": "latency",
                          "direction": "ingress",
                          "side": "client",
                          "delay": 79.378289
                        }
                      }
                    ]
                  }
                ],
                "errored": false,
                "timed_out": false
              },
              "faults": [
                {
                  "type": "latency",
                  "side": "client",
                  "mean": 80.0,
                  "stddev": 5.0,
                  "direction": "ingress"
                }
              ],
              "errors": []
            }
          ],
          "requests_count": 4,
          "failure_counts": 0,
          "total_time": {
            "secs": 1,
            "nanos": 886894730
          }
        }
      ]
    }
  ]
}
```

### Report Analysis

fault is able to generate a report for you when running the scenario. By
default, it will serialize it to JSON. Alternatively, you may change this to
YAML or Markdown. fault will select the right format based on the extension
of the report file. For instance, we could have executed the scenario as
follows:


```bash
fault scenario run --scenario scenario.yaml --report report.md
```

!!! example "Scenario report"

    # Scenarios Report

    Start: 2025-05-13 06:11:34.262257729 UTC

    End: 2025-05-13 06:11:36.746793078 UTC

    ## Scenario: Latency Increase By 30ms Steps From Downstream  (items: 4)

    _Description:_ A tests to evaluate how our service handles network faults.

    ### 🎯 `GET` http://localhost:7070/ping | Failed

    **Call**:

    - Method: `GET`
    - Timeout: -
    - Headers: -
    - Body?: No

    **Strategy**: repeat 3 times with a step of 30

    **Faults Applied**:
    - Latency: ➡️🖧, Per Read/Write Op.: false, Mean: 80.00 ms, Stddev: 5.00 ms

    **Expectation**: Response time Under 490ms | Status Code 200

    **Run Overview**:

    | Num. Requests | Num. Errors | Min. Response Time | Max Response Time | Mean Latency (ms) | Expectation Failures | Total Time |
    |-----------|---------|--------------------|-------------------|-------------------|----------------------|------------|
    | 4 | 0 (0.0%) | 401.56 | 955.63 | 450.99 | 1 | 2 seconds and 407 ms |

    | Latency Percentile | Latency (ms) | Num. Requests (% of total) |
    |------------|--------------|-----------|
    | p25 | 413.50 | 2 (50.0%) |
    | p50 | 450.99 | 3 (75.0%) |
    | p75 | 829.88 | 4 (100.0%) |
    | p95 | 955.63 | 4 (100.0%) |
    | p99 | 955.63 | 4 (100.0%) |


    ---


## Step 6: Identifying Areas for Improvement

Now that you’ve run your scenarios, it’s time to take a close look at the
results and ask yourself: How did your application really perform under these
simulated network conditions? Questions you may ask about your service:

**Latency Handling:**
  Did your application gracefully manage the injected latency, or did some
  requests time out?

**Error Handling and Retries:**
  Although these examples focus on latency, think about how your system would
  respond to more disruptive faults. Are your
  error-handling and retry mechanisms robust enough to recover gracefully?

**Bandwidth Constraints:**
  Consider how the application behaves under limited bandwidth scenarios.
  Would a throttled connection significantly affect user experience or internal
  performance?

### Detailed Breakdown

**Test 1: Baseline Call (No Fault Injected)**

  - **Response Time:** 391.25ms
  - **Expected:** Under 490ms
  - **Outcome:** **Success**  
    *Your service handled the request quickly under ideal conditions.*

**Test 2: Latency Fault with Mean 80ms**

  - **Injected Fault:** Latency fault with a mean of 80ms
  - **Response Time:** 382.47ms
  - **Expected:** Under 490ms
  - **Outcome:** **Success**  
    *The slight increase in latency was within acceptable limits.*

**Test 3: Latency Fault with Mean 110ms**

  - **Injected Fault:** Latency fault with a mean of 110ms
  - **Response Time:** 434.31ms
  - **Expected:** Under 490ms
  - **Outcome:** **Failure**  
    *A higher increase in latency was within acceptable limits.*

**Test 4: Latency Fault with Mean 140ms**

  - **Injected Fault:** Latency fault with a mean of 140ms
  - **Response Time:** 655.48ms
  - **Expected:** Under 490ms
  - **Outcome:** **Failure**  
    *The response time further degraded, confirming that higher latency critically impacts performance.*

### Interpreting the Results

- **Performance Sensitivity:**  
  The baseline and initial fault test (80ms mean) indicate your application
  performs well under slight latency. However, when the latency increases beyond
  a certain point (110ms and 140ms), the response time quickly escalates,
  leading to failures.

- **Threshold Identification:**  
  These results help you pinpoint the latency threshold where your application
  begins to struggle. Knowing this, you can set realistic performance targets
  and optimize system behavior for expected network conditions.

- **Insight into Resilience:**  
  The incremental steps in fault injection reveal exactly how your system's
  performance degrades. This information is crucial for making targeted
  improvements. For instance, refining retry logic, adjusting timeouts, or
  optimizing resource management.

### Next Steps Based on These Insights

- **Investigate Bottlenecks:**  
  Analyze why your service handles up to 80ms latency successfully but fails at
  higher levels. This could be due to slow dependencies, inefficient error
  handling, or suboptimal timeouts.

- **Enhance Fault Tolerance:**  
  Consider implementing circuit breakers or adaptive retry mechanisms that kick
  in as latency increases.

- **Iterate and Test:**  
  Use these insights to further refine your scenarios. Adjust the fault
  parameters and re-run tests to see if your improvements yield the desired
  performance enhancements.

## Conclusion

In this tutorial, you learned how to:

- **Define and run a scenario:**  
  You created a scenario file to simulate multiple network faults:
  latency, bandwidth constraints, and error injections.

- **Observe real-world impact:**  
  By running your scenarios, you observed how your application behaves under
  stress. The collected metrics and logs provided clear evidence of its
  strengths and weaknesses.

- **Gather actionable data:**  
  The insights from the test reports guided you in identifying areas for
  performance optimization and error handling improvements.

By integrating these practices into your development cycle, you can catch issues
earlier in the process. The goal is to help your application to become more
resilient and production-ready. This proactive approach not only improves overall
system reliability but also paves the way for a smoother, more confident path to
production.

## Next Steps

- **Discover our [How-To Guides](../how-to/scenarios/generate.md)** to explore
  fault's capabilities and how to apply them.
