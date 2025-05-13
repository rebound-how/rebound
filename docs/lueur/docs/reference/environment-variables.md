# Environment Variables

lueur is configured through its CLI arguments. However, in some cases, it may
be simpler to populate these options via environment variables.

## Common Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `LUEUR_LOG_FILE`                  | (none)    | Path to a file where to write lueur logs                                                 |
| `LUEUR_WITH_STDOUT_LOGGING`                  | `false`    | Whether to enable logging to stdout                                                 |
| `LUEUR_LOG_LEVEL`                  | `info,tower_http=debug`    | Level respecting tracing subscriber [env filter](https://docs.rs/tracing-subscriber/latest/tracing_subscriber/filter/struct.EnvFilter.html#directives) directives                                                 |

## Observability Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `LUEUR_WITH_OTEL`                  | `false`    | Whether to enable Open Telemetry tracing and metrics                                                 |

## `run` Command Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `LUEUR_PROXY_NO_UI`                  | (none)    | Disables the terminal UI and make the output fully silent.                                                 |
| `LUEUR_PROXY_ADDRESS`                  | `127.0.0.1:3180`    | The address on which the proxy server listens.                                                 |
| `LUEUR_ENABLE_STEALTH`                   | `false`             | Whether stealth mode (using eBPF) is enabled.                                                    |
| `LUEUR_EBPF_PROCESS_NAME`                 | (none)              | The name of a process to intercept traffic from (used when stealth mode is enabled).           |
| `LUEUR_EBPF_PROGRAMS_DIR`                 | `"$HOME/cargo/bin"`              | The directory where eBPF programs for lueur can be found (used when stealth mode is enabled).           |
| `LUEUR_EBPF_PROXY_IP`                 | (none)              | The address to use by the eBPF proxy. If unset, uses the same as the default proxy address.           |
| `LUEUR_EBPF_PROXY_PORT`                 | (none)              | The port the eBPF proxy is bound to. By default uses a random port.           |
| `LUEUR_EBPF_PROXY_IFACE`                 | (none)              | The interface to attach the eBPF programs to. Uses the interface of the proxy IP by default.           |
| `LUEUR_GRPC_PLUGINS`                   | (none)              | Comma-separated list of gRPC plugin addresses.                                                 |
| `LUEUR_UPSTREAMS`                 | (none)              | Comma-separated list of upstream hostnames to proxy.                                           |
| `LUEUR_WITH_LATENCY`                   | `false`             | Whether a latency fault is enabled.                                                    |
| `LUEUR_LATENCY_PER_READ_WRITE`                   | `false`             | Whether latency should be applied on a per read/write operation or once.                                      |
| `LUEUR_LATENCY_DISTRIBUTION`                   | `normal`             | The statistical distribution used.                                      |
| `LUEUR_LATENCY_SIDE`                   | `server`             | The side which will be impacted by the fault.                                      |
| `LUEUR_LATENCY_DIRECTION`                   | `ingress`             | The direction which will be impacted by the fault.                                      |
| `LUEUR_LATENCY_MEAN`                   | (none)             | Mean latency in milliseconds for latency fault injection.                                      |
| `LUEUR_LATENCY_STANDARD_DEVIATION`                 | (none)              | Standard deviation of latency in milliseconds.                                                 |
| `LUEUR_LATENCY_SHAPE`                 | (none)              | Distribution shape when using pareto or pareto normal.                                                 |
| `LUEUR_LATENCY_SCALE`                 | (none)              | Distribution scale when using pareto or pareto normal.                                                 |
| `LUEUR_LATENCY_MIN`                 | (none)              | Minimum latency when using a uniform distribution.                                                 |
| `LUEUR_LATENCY_MAX`                 | (none)              | Maximum latency when using a uniform distribution.                                                 |
| `LUEUR_WITH_BANDWIDTH`                   | `false`             | Whether a bandwidth fault is enabled.                                                    |
| `LUEUR_BANDWIDTH_DIRECTION`                   | `ingress`             | The direction which will be impacted by the fault.                                      |
| `LUEUR_BANDWIDTH_RATE`                   | `1000`             | Rate to impose on traffic.                                      |
| `LUEUR_BANDWIDTH_UNIT`                   | `bps`             | Unit of the rate.                                      |
| `LUEUR_WITH_JITTER`                   | `false`             | Whether a jitter fault is enabled.                                                    |
| `LUEUR_JITTER_AMPLITUDE`               | `20.0`              | Maximum jitter delay in milliseconds for jitter fault injection.                               |
| `LUEUR_JITTER_FREQ`               | `5.0`               | Frequency (in Hertz) of jitter application.                                                    |
| `LUEUR_WITH_PACKET_LOSS`                   | `false`             | Whether a packet-loss fault is enabled.                                                    |
| `LUEUR_PACKET_LOSS_SIDE`                   | `server`             | The side which will be impacted by the fault.                                      |
| `LUEUR_PACKET_LOSS_DIRECTION`                   | `ingress`             | The direction which will be impacted by the fault.                                      |
| `LUEUR_WITH_HTTP_FAULT`                   | `false`             | Whether a http fault fault is enabled.                                                    |
| `LUEUR_HTTP_FAULT_STATUS`                    | `500`               | HTTP status code to return when the HTTP response fault is triggered.                          |
| `LUEUR_HTTP_FAULT_PROBABILITY`                      | `1.0`              | Probability to apply the fault on a given HTTP exchange.               |
| `LUEUR_WITH_DNS`                       | `false`                | Whether a dns fault is enabled.                                                    |
| `LUEUR_DNS_PROBABILITY`                       | `0.5`                | Probability (0–100) to trigger a DNS fault.                                                    |

## `scenario` Command Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `LUEUR_SCENARIO_REPORT_PATH`                  | (none)    | The file path to a scenario file or a directory path to a folder containing scenario files.                                                 |
| `LUEUR_SCENARIO_PROXY_ADDR`                  | `127.0.0.1:3180`    | Address of the proxy the secanrio command will run during the tests                                |

## `agent` Command Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `LUEUR_AGENT_CLIENT`                  | `open-ai`    | The LLM client to use (amongst `open-ai`, `open-router` or `ollama`).                                                 |
| `LLM_PROMPT_REASONING_MODEL`                  | `o4-mini`    | The LLM reasoning model to use.                                                 |
| `LLM_PROMPT_CHAT_MODEL`                  | `gpt-4.1-mini`    | The LLM chat model to use.                                                 |
| `LUEUR_AGENT_EMBED_MODEL`                  | `text-embedding-3-small`    | The LLM embedding model to use.                                                 |

### `scenario-review` Subcommand Variables

| **Name**                         | **Default Value**   |  **Explanation**  |
|----------------------------------|---------------------|---------------------|
| `LUEUR_SCENARIO_RESULTS_PATH`                  | (none)    | Path to the results file from the `scenario run` command.                                                 |
| `LUEUR_AGENT_SCENARIO_REVIEW_REPORT_FILE`                  | `scenario-analysis-report.md`    | Path to the file where to save the generated report.                                                 |
| `LUEUR_AGENT_ADVICE_ROLE`                  | `developer`    | Role to generate the report from, one of `developer` or `sre`.                                                 |


### `code-review` Subcommand Variables

| **Name**                         | **Default Value**   |  **Explanation**  |
|----------------------------------|---------------------|---------------------|
| `LUEUR_SCENARIO_RESULTS_PATH`                  | (none)    | Path to the results file from the `scenario run` command.                                                 |
| `LUEUR_AGENT_CODE_REVIEW_REPORT_FILE`                  | `code-review-report.md`    | Path to the file where to save the generated report.                                                 |
| `LUEUR_AGENT_CODE_REVIEW_SOURCE_DIR`                  | (none)    | Directory where the source code is located                                                 |
| `LUEUR_AGENT_CODE_REVIEW_SOURCE_LANGUAGE`                  | (none)    | Language of the source code: `python`, `go`, `rust`, `java`, `typescript`, `javascript`, `elixir`                                                 |
| `LUEUR_AGENT_CODE_REVIEW_SOURCE_INDEX_PATH`                  | `/tmp/index.db`    | Path of the [DuckDB](https://duckdb.org/) vector database where storing the index                                               |
| `LUEUR_AGENT_SCENARIO_REVIEW_REPORT_FILE`                  | `scenario-analysis-report.md`    | Path of the report generated by `agent scenario-review`                                               |


## `demo` Command Variables

| **Name**                         | **Default Value**   | **Explanation**                                                                                  |
|----------------------------------|---------------------|--------------------------------------------------------------------------------------------------|
| `LUEUR_DEMO_ADDR`                  | `127.0.0.1`    | IP address to bind the server to.                                                 |
| `LUEUR_DEMO_PORT`                  | `7070`    | Port to bind the server to.                                                 |
