# Explore Scenario Reports

In this guide, you will learn how to interpret the reports generated from
running scenarios.

??? abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span>

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../install.md).

    -   [X] Generate Scenario Files

        If you haven’t created a scenario file, please read this
        [guide](./generate.md).

    -   [X] Run Scenario Files

        If you haven’t executed scenario files, please read this
        [guide](./run.md).

## Results vs Report

faul<span class="f">fault</span>t generates two assets when running scenarios:

* `results.json` an extensive account of what happened during the run, including
  a detailed trace of all the faults that were injected
* `report.md` a markdown high-level report from a run

## Report Example

Below is an example of a generated markdown report.

---

## Scenarios Report

Start: 2025-05-05 11:20:12.665603456 UTC

End: 2025-05-05 11:20:37.004974829 UTC

### Scenario: Latency Increase By 30ms Steps From Downstream  (items: 6)

#### 🎯 `GET` http://localhost:7070/ping | Passed

**Call**:

- Method: `GET`
- Timeout: -
- Headers: -
- Body?: No

**Strategy**: single shot

**Faults Applied**:
- Latency: ➡️🖧, Per Read/Write Op.: false, Mean: 80.00 ms, Stddev: 5.00 ms

**Expectation**: Response time Under 490ms | Status Code 200

**Run Overview**:

| Num. Requests | Num. Errors | Min. Response Time | Max Response Time | Mean Latency (ms) | Expectation Failures | Total Time |
|-----------|---------|--------------------|-------------------|-------------------|----------------------|------------|
| 1 | 0 (0.0%) | 457.66 | 457.66 | 457.66 | 0 | 464 ms |

| Latency Percentile | Latency (ms) | Num. Requests (% of total) |
|------------|--------------|-----------|
| p25 | 457.66 | 1 (100.0%) |
| p50 | 457.66 | 1 (100.0%) |
| p75 | 457.66 | 1 (100.0%) |
| p95 | 457.66 | 1 (100.0%) |
| p99 | 457.66 | 1 (100.0%) |

#### 🎯 `GET` http://localhost:7070/ping | Failed

**Call**:

- Method: `GET`
- Timeout: -
- Headers: -
- Body?: No

**Strategy**: repeat 3 times with a step of 30

**Faults Applied**:
- Latency: ➡️🖧, Per Read/Write Op.: false, Mean: 80.00 ms, Stddev: 5.00 ms

**Expectation**: Response time Under 390ms | Status Code 200

**Run Overview**:

| Num. Requests | Num. Errors | Min. Response Time | Max Response Time | Mean Latency (ms) | Expectation Failures | Total Time |
|-----------|---------|--------------------|-------------------|-------------------|----------------------|------------|
| 4 | 0 (0.0%) | 365.09 | 838.84 | 373.65 | 1 | 1 second and 968 ms |

| Latency Percentile | Latency (ms) | Num. Requests (% of total) |
|------------|--------------|-----------|
| p25 | 365.99 | 2 (50.0%) |
| p50 | 373.65 | 3 (75.0%) |
| p75 | 723.78 | 4 (100.0%) |
| p95 | 838.84 | 4 (100.0%) |
| p99 | 838.84 | 4 (100.0%) |

| SLO       | Pass? | Objective | Margin | Num. Requests Over Threshold (% of total) |
|-----------|-------|-----------|--------|--------------------------|
| P95 < 300ms | ❌ | 95% < 300ms | Above by 538.8ms | 4 (100.0%) |

#### 🎯 `GET` http://localhost:7070/ | Passed

**Call**:

- Method: `GET`
- Timeout: 500ms
- Headers:
    - Authorization: xxxxxx
    - X-Whatever: blah
- Body?: No

**Strategy**: load for 10s with 5 clients @ 20 RPS

**Faults Applied**:

| Type | Timeline | Description |
|------|----------|-------------|
| latency | 0% `xxxxxxxxxx` 100% | Latency: ➡️🖧, Per Read/Write Op.: true, Mean: 90.00 ms |
| blackhole | 0% `.xx.......` 100% | Blackhole: ➡️🖧 |


**Run Overview**:

| Num. Requests | Num. Errors | Min. Response Time | Max Response Time | Mean Latency (ms) | Expectation Failures | Total Time |
|-----------|---------|--------------------|-------------------|-------------------|----------------------|------------|
| 396 | 30 (7.6%) | 32.89 | 504.95 | 93.19 | 0 | 10 seconds and 179 ms |

| Latency Percentile | Latency (ms) | Num. Requests (% of total) |
|------------|--------------|-----------|
| p25 | 78.47 | 100 (25.3%) |
| p50 | 93.19 | 199 (50.3%) |
| p75 | 108.81 | 298 (75.3%) |
| p95 | 500.94 | 378 (95.5%) |
| p99 | 504.64 | 394 (99.5%) |

| SLO       | Pass? | Objective | Margin | Num. Requests Over Threshold (% of total) |
|-----------|-------|-----------|--------|--------------------------|
| P95 Latency < 110ms | ❌ | 95% < 110ms | Above by 390.9ms | 92 (23.2%) |
| P99 Latency < 200ms | ❌ | 99% < 200ms | Above by 304.6ms | 30 (7.6%) |
| P98 Error Rate < 1% | ❌ | 98% < 1% | Above by 6.6 | 30 (7.6%) |


---
### Scenario: Single high latency spike  (items: 1)

_Description:_ Evaluate how we tolerate one single high latency spike

#### 🎯 `GET` http://localhost:7070/ | Passed

**Call**:

- Method: `GET`
- Timeout: -
- Headers: -
- Body?: No

**Strategy**: single shot

**Faults Applied**:
- Latency: ➡️🖧, Per Read/Write Op.: false, Mean: 800.00 ms, Stddev: 100.00 ms

**Expectation**: Status Code 200

**Run Overview**:

| Num. Requests | Num. Errors | Min. Response Time | Max Response Time | Mean Latency (ms) | Expectation Failures | Total Time |
|-----------|---------|--------------------|-------------------|-------------------|----------------------|------------|
| 1 | 0 (0.0%) | 795.82 | 795.82 | 795.82 | 0 | 800 ms |

| Latency Percentile | Latency (ms) | Num. Requests (% of total) |
|------------|--------------|-----------|
| p25 | 795.82 | 1 (100.0%) |
| p50 | 795.82 | 1 (100.0%) |
| p75 | 795.82 | 1 (100.0%) |
| p95 | 795.82 | 1 (100.0%) |
| p99 | 795.82 | 1 (100.0%) |


---
### Scenario: Gradual moderate latency increase  (items: 6)

_Description:_ Evaluate how we tolerate latency incrementally growing

#### 🎯 `GET` http://localhost:7070/ | Passed

**Call**:

- Method: `GET`
- Timeout: -
- Headers: -
- Body?: No

**Strategy**: repeat 5 times with a step of 100

**Faults Applied**:
- Latency: ➡️🖧, Per Read/Write Op.: false, Mean: 100.00 ms, Stddev: 30.00 ms

**Expectation**: Status Code 200

**Run Overview**:

| Num. Requests | Num. Errors | Min. Response Time | Max Response Time | Mean Latency (ms) | Expectation Failures | Total Time |
|-----------|---------|--------------------|-------------------|-------------------|----------------------|------------|
| 6 | 0 (0.0%) | 50.67 | 137.63 | 89.63 | 0 | 566 ms |

| Latency Percentile | Latency (ms) | Num. Requests (% of total) |
|------------|--------------|-----------|
| p25 | 52.03 | 2 (33.3%) |
| p50 | 89.63 | 4 (66.7%) |
| p75 | 123.53 | 6 (100.0%) |
| p95 | 137.63 | 6 (100.0%) |
| p99 | 137.63 | 6 (100.0%) |


---
### Scenario: Repeated mild latencies periods over a 10s stretch  (items: 1)

_Description:_ Evaluate how we deal with periods of moderate latencies over a period of time

#### 🎯 `GET` http://localhost:7070/ | Passed

**Call**:

- Method: `GET`
- Timeout: -
- Headers: -
- Body?: No

**Strategy**: load for 10s with 3 clients @ 2 RPS

**Faults Applied**:

| Type | Timeline | Description |
|------|----------|-------------|
| latency | 0% `.xx.......` 100% | Latency: ➡️🖧, Per Read/Write Op.: false, Mean: 150.00 ms |
| latency | 0% `....xx....` 100% | Latency: ➡️🖧, Per Read/Write Op.: false, Mean: 250.00 ms |
| latency | 0% `.......xx.` 100% | Latency: ➡️🖧, Per Read/Write Op.: false, Mean: 150.00 ms |


**Run Overview**:

| Num. Requests | Num. Errors | Min. Response Time | Max Response Time | Mean Latency (ms) | Expectation Failures | Total Time |
|-----------|---------|--------------------|-------------------|-------------------|----------------------|------------|
| 60 | 0 (0.0%) | 0.27 | 616.96 | 524.52 | 0 | 10 seconds and 330 ms |

| Latency Percentile | Latency (ms) | Num. Requests (% of total) |
|------------|--------------|-----------|
| p25 | 401.47 | 16 (26.7%) |
| p50 | 524.52 | 31 (51.7%) |
| p75 | 550.17 | 46 (76.7%) |
| p95 | 596.09 | 58 (96.7%) |
| p99 | 616.96 | 60 (100.0%) |

| SLO       | Pass? | Objective | Margin | Num. Requests Over Threshold (% of total) |
|-----------|-------|-----------|--------|--------------------------|
| P95 Latency < 110ms | ❌ | 95% < 110ms | Above by 486.1ms | 54 (90.0%) |
| P99 Latency < 200ms | ❌ | 99% < 200ms | Above by 417.0ms | 54 (90.0%) |
| P98 Error Rate < 1% | ✅ | 98% < 1% | Below by 1.0 | 0 (0.0%) |


---
