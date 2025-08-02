# Environment Variables

<span class="f">fault</span> is configured through its CLI arguments. However, in some cases, it may
be simpler to populate these options via environment variables.

## Common Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `FAULT_LOG_FILE`                  | (none)    | Path to a file where to write fault logs                                                 |
| `FAULT_WITH_STDOUT_LOGGING`                  | `false`    | Whether to enable logging to stdout                                                 |
| `FAULT_LOG_LEVEL`                  | `info,tower_http=debug`    | Level respecting tracing subscriber [env filter](https://docs.rs/tracing-subscriber/latest/tracing_subscriber/filter/struct.EnvFilter.html#directives) directives                                                 |

## Observability Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `FAULT_WITH_OTEL`                  | `false`    | Whether to enable Open Telemetry tracing and metrics                                                 |

## `run` Command Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `FAULT_PROXY_NO_UI`                  | (none)    | Disables the terminal UI and make the output fully silent.                                                 |
| `FAULT_PROXY_ADDRESS`                  | `127.0.0.1:3180`    | The address on which the proxy server listens.                                                 |
| `FAULT_DISABLE_HTTP_PROXY`                  | `false`    | Disables the HTTP proxies.                                                 |
| `FAULT_PROXY_DURATION`                  | (none)    | Defines [how long](https://docs.rs/parse_duration/latest/parse_duration/#syntax) the proxy runs for.                                                 |
| `FAULT_ENABLE_STEALTH`                   | `false`             | Whether stealth mode (using eBPF) is enabled.                                                    |
| `FAULT_EBPF_PROCESS_NAME`                 | (none)              | The name of a process to intercept traffic from (used when stealth mode is enabled).           |
| `FAULT_EBPF_PROGRAMS_DIR`                 | `"$HOME/cargo/bin"`              | The directory where eBPF programs for fault can be found (used when stealth mode is enabled).           |
| `FAULT_EBPF_PROXY_IP`                 | (none)              | The address to use by the eBPF proxy. If unset, uses the same as the default proxy address.           |
| `FAULT_EBPF_PROXY_PORT`                 | (none)              | The port the eBPF proxy is bound to. By default uses a random port.           |
| `FAULT_EBPF_PROXY_IFACE`                 | (none)              | The interface to attach the eBPF programs to. Uses the interface of the proxy IP by default.           |
| `FAULT_GRPC_PLUGINS`                   | (none)              | Comma-separated list of gRPC plugin addresses.                                                 |
| `FAULT_UPSTREAMS`                 | (none)              | Comma-separated list of upstream hostnames to proxy.                                           |
| `FAULT_WITH_LATENCY`                   | `false`             | Whether a latency fault is enabled.                                                    |
| `FAULT_LATENCY_PER_READ_WRITE`                   | `false`             | Whether latency should be applied on a per read/write operation or once.                                      |
| `FAULT_LATENCY_DISTRIBUTION`                   | `normal`             | The statistical distribution used.                                      |
| `FAULT_LATENCY_SIDE`                   | `server`             | The side which will be impacted by the fault.                                      |
| `FAULT_LATENCY_DIRECTION`                   | `ingress`             | The direction which will be impacted by the fault.                                      |
| `FAULT_LATENCY_MEAN`                   | (none)             | Mean latency in milliseconds for latency fault injection.                                      |
| `FAULT_LATENCY_STANDARD_DEVIATION`                 | (none)              | Standard deviation of latency in milliseconds.                                                 |
| `FAULT_LATENCY_SHAPE`                 | (none)              | Distribution shape when using pareto or pareto normal.                                                 |
| `FAULT_LATENCY_SCALE`                 | (none)              | Distribution scale when using pareto or pareto normal.                                                 |
| `FAULT_LATENCY_MIN`                 | (none)              | Minimum latency when using a uniform distribution.                                                 |
| `FAULT_LATENCY_MAX`                 | (none)              | Maximum latency when using a uniform distribution.                                                 |
| `FAULT_LATENCY_SCHED`                       | (none)                | Scheduling of the latency fault.                                                    |
| `FAULT_WITH_BANDWIDTH`                   | `false`             | Whether a bandwidth fault is enabled.                                                    |
| `FAULT_BANDWIDTH_DIRECTION`                   | `ingress`             | The direction which will be impacted by the fault.                                      |
| `FAULT_BANDWIDTH_RATE`                   | `1000`             | Rate to impose on traffic.                                      |
| `FAULT_BANDWIDTH_UNIT`                   | `bps`             | Unit of the rate.                                      |
| `FAULT_BANDWIDTH_SCHED`                       | (none)                | Scheduling of the bandwidth fault.                                                    |
| `FAULT_WITH_JITTER`                   | `false`             | Whether a jitter fault is enabled.                                                    |
| `FAULT_JITTER_AMPLITUDE`               | `20.0`              | Maximum jitter delay in milliseconds for jitter fault injection.                               |
| `FAULT_JITTER_FREQ`               | `5.0`               | Frequency (in Hertz) of jitter application.                                                    |
| `FAULT_JITTER_SCHED`                       | (none)                | Scheduling of the jitter fault.                                                    |
| `FAULT_WITH_PACKET_LOSS`                   | `false`             | Whether a packet-loss fault is enabled.                                                    |
| `FAULT_PACKET_LOSS_SIDE`                   | `server`             | The side which will be impacted by the fault.                                      |
| `FAULT_PACKET_LOSS_DIRECTION`                   | `ingress`             | The direction which will be impacted by the fault.                                      |
| `FAULT_PACKET_LOSS_SCHED`                       | (none)                | Scheduling of the packet-loss fault.                                                    |
| `FAULT_WITH_HTTP_FAULT`                   | `false`             | Whether a http fault fault is enabled.                                                    |
| `FAULT_HTTP_FAULT_STATUS`                    | `500`               | HTTP status code to return when the HTTP response fault is triggered.                          |
| `FAULT_HTTP_FAULT_PROBABILITY`                      | `1.0`              | Probability to apply the fault on a given HTTP exchange.               |
| `FAULT_HTTP_FAULT_SCHED`                       | (none)                | Scheduling of the HTTP response fault.                                                    |
| `FAULT_WITH_DNS`                       | `false`                | Whether a dns fault is enabled.                                                    |
| `FAULT_DNS_PROBABILITY`                       | `0.5`                | Probability (0–100) to trigger a DNS fault.                                                    |
| `FAULT_DNS_SCHED`                       | (none)                | Scheduling of the dns fault.                                                    |

### `run llm` Command Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `FAULT_LLM_ENDPOINT`                  | (none)    | Base URL of the target LLM provider.                                                 |
| `FAULT_LLM_PROBABILITY`                  | `1.0`    | Probability which will trigger the fault injection (0  means never and 1 means always).                                                 |
| `FAULT_LLM_SLOW_STREAM_MEAN_DELAY`                  | `300`    | Latency to apply to the LLM response.                                                 |
| `FAULT_LLM_SCRAMBLE_PATTERN`                  | (none)    | Regex pattern to look for into the request.                                                 |
| `FAULT_LLM_SCRAMBLE_WITH`                  | (none)    | Replacement string when the pattern matches.                                                 |
| `FAULT_LLM_SCRAMBLE_INSTRUCTION`                  | (none)    | Instruction to inject into the LLM requests as a system prompt.                                                 |
| `FAULT_LLM_BIAS_PATTERN`                  | (none)    |  Regex pattern to look for into the response.                                                 |
| `FAULT_LLM_BIAS_REPLACEMENT`                  | (none)    | Replacement string when the pattern matches.                                                 |

## `injection` Command Variables

### `aws` Subcommand Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `FAULT_INJECTION_AWS_ECS_CLUSTER`                  | (none)    | ECS Cluster hosting the service.                                                 |
| `FAULT_INJECTION_AWS_REGION`                  | (none)    | Regions where the service lives.                                                 |
| `FAULT_INJECTION_AWS_ECS_SERVICE`                  | (none)    | Target ECS service name to inject faults into.                                                 |
| `FAULT_INJECTION_AWS_IMAGE`                  | (none)    | Container image to run as the sidecar of the service.                                                 |
| `FAULT_INJECTION_GCP_DURATION`                  | (none)    | Duration for which the fault is applied. Follows [this format](https://docs.rs/parse_duration/latest/parse_duration/#syntax).                                                 |

In addition, this subcommand supports the same proxy fault options as the
`run` command.

### `gcp` Subcommand Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `FAULT_INJECTION_GCP_PROJECT`                  | (none)    | Project hosting the service.                                                 |
| `FAULT_INJECTION_GCP_REGION`                  | (none)    | Regions where the service lives.                                                 |
| `FAULT_INJECTION_GCP_TRAFFIC_PERCENT`                  | 100    | Traffic percentage sent through the created revision.                                                 |
| `FAULT_INJECTION_GCP_SERVICE`                  | (none)    | Target CloudRun service name to inject faults into.                                                 |
| `FAULT_INJECTION_GCP_IMAGE`                  | (none)    | Container image to run as the sidecar of the service.                                                 |
| `FAULT_INJECTION_GCP_DURATION`                  | (none)    | Duration for which the fault is applied. Follows [this format](https://docs.rs/parse_duration/latest/parse_duration/#syntax).                                                 |

In addition, this subcommand supports the same proxy fault options as the
`run` command.

### `kubernetes` Subcommand Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `FAULT_INJECTION_K8S_NS`                  | `default`    | Namespace of the target service.                                                 |
| `FAULT_INJECTION_K8S_SERVICE`                  | (none)    | Target service to inject faults into.                                                 |
| `FAULT_INJECTION_K8S_IMAGE`                  | `ghcr.io/rebound-how/fault:latest`    | Container image to run in the cluster. Its entrypoint must be the `fault` binary.                                                 |
| `FAULT_INJECTION_K8S_DURATION`                  | (none)    | Duration for which the fault is applied. Follows [this format](https://docs.rs/parse_duration/latest/parse_duration/#syntax).                                                 |

In addition, this subcommand supports the same proxy fault options as the
`run` command.

## `scenario` Command Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `FAULT_SCENARIO_REPORT_PATH`                  | (none)    | The file path to a scenario file or a directory path to a folder containing scenario files.                                                 |
| `FAULT_SCENARIO_PROXY_ADDR`                  | `127.0.0.1:3180`    | Address of the proxy the secanrio command will run during the tests                                |

## `agent` Command Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `FAULT_AGENT_CLIENT`                  | `open-ai`    | The LLM client to use (amongst `gemini`, `open-ai`, `open-router` or `ollama`).                                                 |
| `LLM_PROMPT_REASONING_MODEL`                  | `o4-mini`    | The LLM reasoning model to use.                                                 |
| `FAULT_AGENT_EMBED_MODEL`                  | `text-embedding-3-small`    | The LLM embedding model to use.                                                 |

### `scenario-review` Subcommand Variables

| **Name**                         | **Default Value**   |  **Explanation**  |
|----------------------------------|---------------------|---------------------|
| `FAULT_SCENARIO_RESULTS_PATH`                  | (none)    | Path to the results file from the `scenario run` command.                                                 |
| `FAULT_AGENT_SCENARIO_REVIEW_REPORT_FILE`                  | `scenario-analysis-report.md`    | Path to the file where to save the generated report.                                                 |
| `FAULT_AGENT_ADVICE_ROLE`                  | `developer`    | Role to generate the report from, one of `developer` or `sre`.                                                 |


### `code-review` Subcommand Variables

| **Name**                         | **Default Value**   |  **Explanation**  |
|----------------------------------|---------------------|---------------------|
| `FAULT_SCENARIO_RESULTS_PATH`                  | (none)    | Path to the results file from the `scenario run` command.                                                 |
| `FAULT_AGENT_CODE_REVIEW_REPORT_FILE`                  | `code-review-report.md`    | Path to the file where to save the generated report.                                                 |
| `FAULT_AGENT_CODE_REVIEW_SOURCE_DIR`                  | (none)    | Directory where the source code is located                                                 |
| `FAULT_AGENT_CODE_REVIEW_SOURCE_LANGUAGE`                  | (none)    | Language of the source code: `python`, `go`, `rust`, `java`, `typescript`, `javascript`, `elixir`                                                 |
| `FAULT_AGENT_CODE_REVIEW_SOURCE_INDEX_PATH`                  | `/tmp/index.db`    | Path of the [DuckDB](https://duckdb.org/) vector database where storing the index                                               |
| `FAULT_AGENT_SCENARIO_REVIEW_REPORT_FILE`                  | `scenario-analysis-report.md`    | Path of the report generated by `agent scenario-review`                                               |


## `demo` Command Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `FAULT_DEMO_ADDR`                  | `127.0.0.1`    | IP address to bind the server to.                                                 |
| `FAULT_DEMO_PORT`                  | `7070`    | Port to bind the server to.                                                 |
