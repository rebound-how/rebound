# Generate Automated Resilience Testing Scenarios

This guide will walk you through generating fault resilience scenarios that you
can run automatically to validate the capability of your endpoints to deal
with network issues.

!!! abstract "Prerequisites"

    -   [X] Install fault

        If you haven’t installed fault yet, follow the
        [installation instructions](../install.md).
  
    -   [X] Scenario Reference

        You might want to familiar yourself with the
        [scenario reference](../../reference/scenario-file-format.md).

## Create Single Shot Scenarios

In this guide, we will demonstrate how to create a single scenario against the
fault demo application. Single call scenarios make only one request to the
target endpoint.

-   [X] Start demo application provided by fault

    ```bash
    fault demo run
    ```

-   [X] Create the scenario file

    The following scenario runs a single HTTP request against the
    `/ping` endpoint of the demo application. That endpoint in turns make
    a request to `https://postman-echo.com` which is the call our scenario
    will impact with a light latency.

    ```yaml title="scenario.yaml"
    ---  # (1)!
    title: "Add 80ms latency to ingress from the remote service and expects we verify our expectations"
    description: "Our endpoint makes a remote call which may not respond appropriately, we need to decide how this impacts our own users"
    items:  # (2)!
      - call:
          method: GET
          url: http://localhost:7070/ping
        context:
          upstreams:
            - https://postman-echo.com  # (3)!
          faults:  # (4)!
            - type: latency
              mean: 80
              stddev: 5
        expect:
          status: 200  # (5)!
          response_time_under: 500  # (6)!
    ```

    1. A scenario file may have as many scenarios as you want
    2. You may group several calls, and their own context, per scenario
    3. This is the host impacted by the latency
    4. You may apply multiple faults at the same time
    5. We do not tolerate the call to fail
    6. We expect to respond globally under `500ms`

## Create Repeated Call Scenarios

In this guide, we will demonstrate how to create a repeated scenario against the
fault demo application. Repated call scenarios make a determinitic number of
requests to the target endpoint, with the possibility to increase some of the
fault parameters by a step on each iteration.

-   [X] Start demo application provided by fault

    ```bash
    fault demo run
    ```

-   [X] Create the scenario file

    The following scenario runs several HTTP requests against the
    `/ping` endpoint of the demo application. That endpoint in turns make
    a request to `https://postman-echo.com` which is the call our scenario
    will impact with a light latency.

    ```yaml title="scenario.yaml"
    ---  # (1)!
    title: "Start with 80ms latency and increase it by 30ms to ingress from the remote service and expects we verify our expectations"
    description: "Our endpoint makes a remote call which may not respond appropriately, we need to decide how this impacts our own users"
    items:  # (2)!
      - call:
          method: GET
          url: http://localhost:7070/ping
        context:
          upstreams:
            - https://postman-echo.com  # (3)!
          strategy:  # (4)!
            mode: repeat
            step: 30  # (5)!
            count: 3  # (6)!
            add_baseline_call: true  # (7)!
          faults:  # (8)!
            - type: latency
              mean: 80
              stddev: 5
        expect:
          status: 200  # (9)!
          response_time_under: 500  # (10)!
    ```

    1. A scenario file may have as many scenarios as you want
    2. You may group several calls, and their own context, per scenario
    3. This is the host impacted by the latency
    4. The `strategy` block defines how fault should run this scenario's call
    5. The step by which we increase latency on each iteration
    6. How many iterations we iterate
    7. Do we have a baseline call, without fault, at the start?
    8. You may apply multiple faults at the same time
    9. We do not tolerate the call to fail
    10. We expect to respond globally under `500ms`

## Create Load Test Call Scenarios

In this guide, we will demonstrate how to create a load test scenario against
the fault demo application. Load test call scenarios make a number of
requests to the target endpoint over a duration.

!!! warning

    fault is not a full-blown load testing tool. It doesn't aim at becoming
    one. The facility provided by this strategy is merely a convenience for
    very small load tests. It can prove very useful nonetheless.

-   [X] Start demo application provided by fault

    ```bash
    fault demo run
    ```

-   [X] Create the scenario file

    The following scenario runs several HTTP requests against the
    `/` endpoint of the demo application.

    ```yaml title="scenario.yaml"
    ---  # (1)!
    title: "Sustained latency with a short loss of network traffic"
    description: "Over a period of 10s, inject a 90ms latency. After 3s and for a period of 2s also send traffic to nowhere."
    items:  # (2)!
      - call:
          method: GET
          url: http://localhost:7070/
        context:
          upstreams:
            - http://localhost:7070  # (3)!
          strategy:  # (4)!
            mode: load
            duration: 10  # (5)!
            clients: 3  # (6)!
            rps: 2  # (7)!
          faults:
            - type: latency
              global: false  # (8)!
              mean: 90
            - type: blackhole
              period: "start:30%,duration:20%"  # (9)!
        slo:  # (10)!
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

    1. A scenario file may have as many scenarios as you want
    2. You may group several calls, and their own context, per scenario
    3. This is the host impacted by the latency
    4. The `strategy` block defines how fault should run this scenario's call
    5. The total duration, in seconds, of our test
    6. The number of connected clients
    7. The number of request per second per client
    8. Inject latency for each read/write operation, not just once
    9. Schedule the blackhole fault for a period of the total duration only
    10. Rather thana single status code and latency, we evaluate SLO against the load results

The load strategy is powerful because it allows you to explore the
application's behavior over a period of time while keeping a similar
approach to other strategies.

Notably, you should remark how we can apply the faults with a schedule
so you can see how they impact the application when they come and go. You
should also note the use of SLO to review the results in light of service
expectations over period of times.

Please read more about these capabilities in the
[scenario reference](../../reference/scenario-file-format.md).

## Generate Scenarios from an OpenAPI Specification

This guide shows you can swiftly generate common basic scenarios for a large
quantity of endpoints discovered from an OpenAPI specification.

!!! info

    fault can generate scenarios from OpenAPI
    [v3.0.x](https://spec.openapis.org/oas/v3.0.3.html) and
    [v3.1.x](https://spec.openapis.org/oas/v3.1.1.html).

-   [X] Generate from a specification file

    ```bash
    fault scenario generate --scenario scenario.yaml --spec-file openapi.yaml
    ```

-   [X] Generate from a specification URL

    ```bash
    fault scenario generate --scenario scenario.yaml --spec-url http://myhost/openapi.json
    ```

-   [X] Generate one scenario file per endpoint

    ```bash
    fault scenario generate \
        --scenario scenarios/ \  # (1)!
        --spec-url http://myhost/openapi.json
    Generated 24 reliability scenarios across 3 endpoints!
    ```

    1. Pass a directory where the files will be stored

This approach is nice to quickly generate scenarios but if your specification
is large, you will endup with hundreds of them. Indeed, fault will create
tests for single shot, repeated calls or load tests. All of these with a
combination of faults.

We suggest you trim down only to what you really want to explore. Moreover,
you will need to edit the scenarios for placeholders and other headers
needed to make the calls.

Below is an example of a generated scenarios against the
[Reliably platform](https://reliably.com):

```yaml
title: Single high-latency spike (client ingress)
description: A single 800ms spike simulates jitter buffer underrun / GC pause on client network stack.
items:
- call:
    method: GET
    url: http://localhost:8090/api/v1/organization/{org_id}/experiments/all
    meta:
      operation_id: all_experiments_api_v1_organization__org_id__experiments_all_get
  context:
    upstreams:
    - http://localhost:8090/api/v1/organization/{org_id}/experiments/all
    faults:
    - type: latency
      side: client
      mean: 800.0
      stddev: 100.0
      direction: ingress
    strategy: null
  expect:
    status: 200
```

!!! abstract "Read more about scenarios..."

    [Learn more](../../reference/scenario-file-format.md) about scenarios and
    explore their capabilities.


## Pass Headers to the Scenario

In this guide, you will learn how to provide HTTP headers to the request made
for a scenario.

-   [X] Start demo application provided by fault

    ```bash
    fault demo run
    ```

-   [X] Create the scenario file

    The following scenario runs a single HTTP request against the
    `/ping` endpoint of the demo application. That endpoint in turns make
    a request to `https://postman-echo.com` which is the call our scenario
    will impact with a light latency.

    ```yaml title="scenario.yaml"
    ---
    title: "Add 80ms latency to ingress from the remote service and expects we verify our expectations"
    description: "Our endpoint makes a remote call which may not respond appropriately, we need to decide how this impacts our own users"
    items:
      - call:
          method: GET
          url: http://localhost:7070/ping
          headers:
            Authorization: bearer token  # (1)!
        context:
          upstreams:
            - https://postman-echo.com
          faults:
            - type: latency
              mean: 80
              stddev: 5
        expect:
          status: 200
          response_time_under: 500
    ```

    1. Pass headers as a mapping of `key: value` pairs. Note in the particular
       case of the `Authorization` header, its value will not be shown as par
       of the report but replaced by a placeholder opaque string.

## Make Requests With a Body

In this guide, you will learn how to pass a body string to the request.

-   [X] Start demo application provided by fault

    ```bash
    fault demo run
    ```

-   [X] Create the scenario file

    The following scenario runs a single HTTP request against the
    `/ping` endpoint of the demo application. That endpoint in turns make
    a request to `https://postman-echo.com` which is the call our scenario
    will impact with a light latency.

    ```yaml title="scenario.yaml"
    ---
    title: "Add 80ms latency to ingress from the remote service and expects we verify our expectations"
    description: "Our endpoint makes a remote call which may not respond appropriately, we need to decide how this impacts our own users"
    items:
      - call:
          method: POST  # (1)!
          url: http://localhost:7070/ping
          headers:
            Content-Type: application/json  # (2)!
          body: '{"message": "hello there"}'  # (3)!
        context:
          upstreams:
            - https://postman-echo.com
          faults:
            - type: latency
              mean: 80
              stddev: 5
        expect:
          status: 200
          response_time_under: 500
    ```

    1. Set the method to `POST`
    2. Pass the actual body content-type.
    3. Pass the body as an encoded string

## Bring on your SRE hat

When running scenarios with a {==load==} or {==repeat==} strategy, we encourage
you to bring SLO into their context. They will give you invaluable insights
about the expectations that could be broken due to a typical faults combination.

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

fault supports two types of SLO: `latency` and `error`. When a scenario is
executed, the generated report contains an analysis of the results of the run
against these objectives. It will decide if broke them or not based on the
volume of traffic and duration of the scenario.

## Next Steps

- **Learn how to [run](./run.md)** these scenarios.
- **Explore the [specification reference](../../reference/scenario-file-format.md)**
  for scenarios.
