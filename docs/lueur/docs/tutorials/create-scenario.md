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

  - Configure Lueur to apply latency.
  - Run a defined scenario that systematically applies this fault.
  - Observe the application’s behavior and interpret the resulting report.

## Prerequisites

**Tools & Setup**:

  - Lueur installed on your local machine.
  - An existing application or a simple test client that makes calls to a known
    third-party endpoint (e.g., `https://api.example.com`).
  - Basic familiarity with setting `HTTP_PROXY` or `HTTPS_PROXY` environment
    variables.
  
**Assumptions**:  
  The tutorial assumes you have followed the
  [Getting Started](./getting-started.md) tutorial and understand how to launch
  lueur proxy.

## Step 1: Choosing the Third-Party Endpoint

Before simulating any faults, it’s essential to establish a reliable baseline.
This step ensures that your application can communicate successfully with a
stable API, so you know that any issues observed later are truly due to the
injected faults.

### How to Pick a Stable Endpoint

- **Reachability:**  
  lueur supports HTTP/1.1 and HTTP/2 only. If your endpoint only responds to
  HTTP/3, lueur cannot work with it.
  
- **Consistency:**  
  Select an endpoint known for its consistency. A public API that rarely experiences
  downtime is ideal.
  
- **Predictability:**  
  The endpoint should return predictable responses, making it easier to spot the impact
  of any simulated network faults.

For demonstration purposes, use `http://localhost:7070`.

## Step 2: Creating a Scenario File

In this step, you'll create a scenario file in YAML that defines a series of
tests. Each scenario acts like a mini-test case, telling lueur exactly how to
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

This section defines the HTTP request that Lueur will make.

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

This section tells Lueur which upstream services are involved and which faults
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
        side: client
    strategy:
      mode: Repeat
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

    The reasone we are using this server here is because the demo application
    provided by lueur makes a call to it when the `/ping` endpoint is called.

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
  scenarios:
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
            side: client
        strategy:
          mode: Repeat
          step: 30
          count: 3
          add_baseline_call: true
      expect:
        status: 200
        response_time_under: 490
  ```


## Step 3: Configuring Your Application and Environment

Before running your fault injection scenarios, it's crucial to ensure that
traffic to and from your application is routed via lueur's proxy.

### Set the Proxy Environment Variable

Configure your environment so that all HTTPS traffic is routed through lueur.
This is typically done by setting the `HTTP_PROXY`  and/or `HTTPS_PROXY`
environment variable to point to lueur's proxy endpoint.

- **On Linux/MacOS/Windows (WSL):**

  ```bash
  export HTTP_PROXY=http://127.0.0.1:8080
  export HTTPS_PROXY=http://127.0.0.1:8080
  ```

- **On Windows:**

  ```command
  set HTTP_PROXY=http://127.0.0.1:8080
  set HTTPS_PROXY=http://127.0.0.1:8080
  ```

  or using Powershell:

  ```powershell
  $env:HTTP_PROXY = "http://127.0.0.1:8080"
  $env:HTTPS_PROXY = "http://127.0.0.1:8080"
  ```

## Step 4: Running the Scenario

Now that you’ve defined your scenarios and configured your environment,
it’s time to run the tests and see lueur in action.

### Run the Scenario

Execute the following command in your terminal:

```bash
lueur scenario run --scenario scenario.yaml
```

!!! tip

    You may pass a directory instead of a single file, lueur will process all
    of them as part of a single run.

Here is the output of the run:

```bash
================ Running Scenarios ================

⠏  4/4  Latency Increase By 30ms Steps From Downstream  ▮▮▮▮

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

- lueur starts a local proxy server (by default at `http://127.0.0.1:8080`) to
intercept and manipulate network traffic.

**Fault Injection:**

- For each test defined in your scenario file, lueur applies the specified
  network faults.

**Metrics and Logging:**

- As the tests run, lueur captures detailed metrics (like response times,
  status codes, and error occurrences) along with logs. All this data is then
  saved to `scenario-report.json` for later analysis.

## Step 5: Observing Logs and Output

lueur records metrics while running the scenario. You can use this information
to analyse the way your application reacted to increasingly degraded network
conditions.

lueur produces two files:

- `results.json` Represents the structured log of the scenario execution.
  Notably, it shows the faults as they were applied
- `report.json` Represents an automated analysis of the run. lueur applies some
  heuristics to evaluate what would be the impact on a variety of service-level
  objectives (SLO)

### Run Metrics

Here is an example of `results.json` file:

```json
{
  "plugins": [],
  "items": [
    {
      "title": "Latency Increase By 30ms Steps From Downstream",
      "timestamp": 1741273041489713,
      "target": {
        "address": "http://localhost:7070/ping"
      },
      "metrics": {
        "dns": [],
        "protocol": {
          "type": "http",
          "code": 200,
          "body_length": 308
        },
        "ttfb": 411.620809,
        "total_time": 411.620792,
        "faults": []
      },
      "expect": {
        "type": "http",
        "wanted": {
          "status_code": 200,
          "response_time_under": 490.0
        },
        "got": {
          "status_code": 200,
          "response_time": 411.620792,
          "decision": "success"
        }
      },
      "faults": [],
      "errors": [],
      "total_time": 0.0
    },
    {
      "title": "Latency Increase By 30ms Steps From Downstream",
      "timestamp": 1741273041972099,
      "target": {
        "address": "http://localhost:7070/ping"
      },
      "metrics": {
        "dns": [],
        "protocol": {
          "type": "http",
          "code": 200,
          "body_length": 308
        },
        "ttfb": 478.129449,
        "total_time": 478.129428,
        "faults": []
      },
      "expect": {
        "type": "http",
        "wanted": {
          "status_code": 200,
          "response_time_under": 490.0
        },
        "got": {
          "status_code": 200,
          "response_time": 478.129428,
          "decision": "success"
        }
      },
      "faults": [
        {
          "type": "latency",
          "distribution": null,
          "global": null,
          "side": "client",
          "mean": 80.0,
          "stddev": 5.0,
          "min": null,
          "max": null,
          "shape": null,
          "scale": null,
          "direction": "ingress"
        }
      ],
      "errors": [],
      "total_time": 0.0
    },
    {
      "title": "Latency Increase By 30ms Steps From Downstream",
      "timestamp": 1741273042577946,
      "target": {
        "address": "http://localhost:7070/ping"
      },
      "metrics": {
        "dns": [],
        "protocol": {
          "type": "http",
          "code": 200,
          "body_length": 307
        },
        "ttfb": 601.706611,
        "total_time": 601.706599,
        "faults": []
      },
      "expect": {
        "type": "http",
        "wanted": {
          "status_code": 200,
          "response_time_under": 490.0
        },
        "got": {
          "status_code": 200,
          "response_time": 601.706599,
          "decision": "failure"
        }
      },
      "faults": [
        {
          "type": "latency",
          "distribution": null,
          "global": null,
          "side": "client",
          "mean": 110.0,
          "stddev": 5.0,
          "min": null,
          "max": null,
          "shape": null,
          "scale": null,
          "direction": "ingress"
        }
      ],
      "errors": [],
      "total_time": 0.0
    },
    {
      "title": "Latency Increase By 30ms Steps From Downstream",
      "timestamp": 1741273043255539,
      "target": {
        "address": "http://localhost:7070/ping"
      },
      "metrics": {
        "dns": [],
        "protocol": {
          "type": "http",
          "code": 200,
          "body_length": 308
        },
        "ttfb": 673.595708,
        "total_time": 673.595687,
        "faults": []
      },
      "expect": {
        "type": "http",
        "wanted": {
          "status_code": 200,
          "response_time_under": 490.0
        },
        "got": {
          "status_code": 200,
          "response_time": 673.595687,
          "decision": "failure"
        }
      },
      "faults": [
        {
          "type": "latency",
          "distribution": null,
          "global": null,
          "side": "client",
          "mean": 140.0,
          "stddev": 5.0,
          "min": null,
          "max": null,
          "shape": null,
          "scale": null,
          "direction": "ingress"
        }
      ],
      "errors": [],
      "total_time": 0.0
    }
  ]
}
```

### Report Analysis

lueur is able to generate a report for you when running the scenario. By
default, it will serialize it to JSON. Alternatively, you may change this to
YAML or Markdown. lueur will select the right format based on the extension
of the report file. For instance, we could have executed the scenario as
follows:


```bash
lueur scenario run --scenario scenario.yaml --report report.md
```

Here is an example its output:

```markdown
# Lueur Resilience Test Report

| **Endpoint** | **Total Fault Injected** | **SLO: 99% < 200ms** | **SLO: 95% < 500ms** | **SLO: 90% < 1s** | **SLO: 99% < 1% Error Rate** | **SLO: 95% < 0.5% Error Rate** |
|-------------|--------------------------|-----------------------|-----------------------|-----------------------|----------------------------------|-----------------------------------|
| `http://localhost:7070/ping` |  | ✅ | ✅ | ✅ | ✅ | ✅ |
| `http://localhost:7070/ping` | - Latency Fault [Global: true, Side: client, Mean: 80.00 ms, Stddev: 5.00 ms, Direction: ingress] | ✅ | ✅ | ✅ | ✅ | ✅ |
| `http://localhost:7070/ping` | - Latency Fault [Global: true, Side: client, Mean: 110.00 ms, Stddev: 5.00 ms, Direction: ingress] | ❌ (+401.7ms), 0h 0m 0.4s | ❌ (+101.7ms), 0h 0m 0.1s | ❌ (+-398.3ms), 0h 0m 0s | ❌ (+49.0%), 0h 0m 0.1s | ❌ (+49.5%), 0h 0m 0.1s |
| `http://localhost:7070/ping` | - Latency Fault [Global: true, Side: client, Mean: 140.00 ms, Stddev: 5.00 ms, Direction: ingress] | ❌ (+473.6ms), 0h 0m 0.5s | ❌ (+173.6ms), 0h 0m 0.2s | ❌ (+-326.4ms), 0h 0m 0s | ❌ (+49.0%), 0h 0m 0.1s | ❌ (+49.5%), 0h 0m 0.1s |
## Summary
- **Total Test Cases:** 4
- **Failures:** 2
- 🔍 Recommendation: Investigate the failed test cases to enhance your application's resilience.

## Fault Type Analysis


## Recommendations
- No specific recommendations based on fault types.

```

!!! success "Bring our own SLOs"

    In a future release, lueur will allow you to pull information from
    your own SLO to give a more bespoke picture.


## Step 6: Identifying Areas for Improvement

Now that you’ve run your scenarios, it’s time to take a close look at the
results and ask yourself: How did your application really perform under these
simulated network conditions? Reflect on the following questions:

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

  - **Response Time:** 411.62ms
  - **Expected:** Under 490ms
  - **Outcome:** **Success**  
    *Your service handled the request quickly under ideal conditions.*

**Test 2: Latency Fault with Mean 80ms**

  - **Injected Fault:** Latency fault with a mean of 80ms
  - **Response Time:** 478.13ms
  - **Expected:** Under 490ms
  - **Outcome:** **Success**  
    *The slight increase in latency was within acceptable limits.*

**Test 3: Latency Fault with Mean 110ms**

  - **Injected Fault:** Latency fault with a mean of 110ms
  - **Response Time:** 601.71ms
  - **Expected:** Under 490ms
  - **Outcome:** **Failure**  
    *The additional latency caused the response time to exceed the target threshold.*

**Test 4: Latency Fault with Mean 140ms**

  - **Injected Fault:** Latency fault with a mean of 140ms
  - **Response Time:** 673.60ms
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

- Point to other How-To guides for fine-tuning scenarios or integrating lueur into CI pipelines.
- Suggest expanding the scenario file with more complex tests or different endpoints.
- Encourage experimenting with different fault profiles to continuously challenge and improve the application’s resilience.
