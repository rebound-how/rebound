# CLI Reference

This document provides an overview of the CLI. The CLI is organized into a
single command with grouped parameters, allowing you to configure and run
the proxy with various network fault simulations, execute test scenarios
defined in a file or launch a local demo server.

---

## Commands

### `run`

Run the proxy with fault injection enabled. This command applies the specified
network faults to HTTP requests and tunnel streams.

### `scenario`

Execute a predefined fault injection scenario. This command includes additional
subcommands for selecting different scenarios.

### `demo`

Run a simple demo server for learning purposes, with various fault simulation options available.

---

## Global Options

These options apply across all commands:

- **`--log-file <file>`**  
  _Path to a file where lueur can append new logs during its execution._  
  **Example:** `--log-file lueur.log`

- **`--log-stdout`**  
  _Flag enabling logs to be printed to the standard output._  
  _Default:_ Disabled  
  **Example:** `--log-stdout`

- **`--log-level <level>`**  
  _Logging level which must follow the format set by cargo._  
  _Default:_ `info,tower_http=debug`  
  **Example:** `--log-level warning`

---

## Observability Options

These options apply across all commands:

- **`--with-otel`**  
  _Enable Open Telemetry traces and metrics. Expects the correct [Open Telemetry environment variables](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/) to be configured._  
  _Default:_ Disabled  
  **Example:** `--with-otel`

---

## `run` Command Options

Fault injection parameters are grouped into sections based on the type of
network fault. Each section allows you to enable or disable a fault and
configure its properties.

### UI Options

These options define how the UI is setup on lueur's output:

- **`--no-ui`**  
  _Disable entirely the terminal UI and make the output fully silent._  

- **`--tail`**  
  _Enable tailing of intercepted traffic into the console._  
  _Default:_ Disabled

### Proxy Configuration Options

These options define how to comnfigure the proxy started by lueur:

- **`--duration <value>`**  
  _How long to run the proxy process for. See [here](https://docs.rs/parse_duration/latest/parse_duration/#syntax) for the supported syntax_  
  _Default:_  unlimited
  **Example:** `--duration 60s`
  **Example:** `--duration 10m`

- **`--proxy-address <address>`**  
  _Listening address for the proxy server._  
  _Default:_ `127.0.0.1:8080`  
  **Example:** `--proxy-address 192.168.12.45:8090`

- **`--upstream <host>`**  
  _Target host(s) to proxy (can be specified multiple times). You may also set `*` to tell lueur you want to impact any upstream._  
  **Example:** `--upstream example.com`
  **Example:** `--upstream '*'`
  **Example:** `--upstream=*`

- **`--grpc-plugin <address>`**  
  _Specify one or more gRPC plugin addresses._  
  **Example:** `--grpc-plugin 192.168.1.100:50051`

### Stealth Configuration Options

These options configure the stealth mode of the lueur's proxy.

!!! info

    Stealth mode is currently only supported on Linux hosts. Therefore you
    will not see these options on other systems.

    This option addresses recent Linux kernels.

!!! note

    Upstream hosts are currently ignored when traffic is redirected via the
    eBPF programs.

- **`--stealth`**  
  _Enable stealth mode using eBPF._  
  _Default:_ Disabled  
  **Example:** `--stealth`

- **`--capture-process <procname>`**  
  _Process name captured by the eBPF program (requires `--stealth`)._  
  **Example:** `--capture-process curl`

- **`--ebpf-proxy-ip <ip>`**  
  _IP address to bind the eBPF proxy to. If unset, uses the same as the default proxy address (requires `--stealth`)._  
  **Example:** `--ebpf-proxy-ip 192.168.1.26`

- **`--ebpf-proxy-port <port>`**  
  _Port to bind the eBPF proxy to. If unset, uses a random port (requires `--stealth`)._  
  **Example:** `--ebpf-proxy-port 47070`

- **`--ebpf-proxy-iface <iface>`**  
  _Interface to attach the eBPF programs to. Defaults to the interface associated to the eBPF proxy IP (requires `--stealth`)._  
  **Example:** `--ebpf-proxy-iface eth0`

### Latency Options

- **`--with-latency`**  
  Enable latency fault injection.  
  _Default:_ Disabled

- **`--latency-per-read-write`**  
  Apply latency on each read or write operation rather than once.  
  _Default:_ Disabled

- **`--latency-side <side>`**  
  Side to apply the latency fault. Options: `client`, `server`  
  _Default:_ `server`

- **`--latency-direction <direction>`**  
  Direction to apply the latency fault. Options: `ingress`, `egress`, `both`  
  _Default:_ `both`

- **`--latency-distribution <distribution>`**  
  Latency distribution type (uniform, normal, pareto, pareto_normal).  
  _Default:_ `normal`

- **`--latency-mean <value>`**  
  Mean latency in milliseconds (positive float) (requires `--latency-distribution normal`).  
  **Example:** `--latency-mean 300`

- **`--latency-stddev <value>`**  
  Standard deviation in milliseconds (non-negative float) (requires `--latency-distribution normal`).  
  **Example:** `--latency-stddev 20`

- **`--latency-shape <value>`**  
  Distribution shape parameter (non-negative float) (requires `--latency-distribution pareto|pareto_normal`).  
  **Example:** `--latency-shape 20`

- **`--latency-scale <value>`**  
  Distribution scale parameter (non-negative float) (requires `--latency-distribution pareto|pareto_normal`).  
  **Example:** `--latency-scale 20`

- **`--latency-min <value>`**  
  Minimum latency for uniform distribution (non-negative float) (requires `--latency-distribution uniform`).  
  **Example:** `--latency-min 20`

- **`--latency-max <value>`**  
  Maximum latency for uniform distribution (non-negative float) (requires `--latency-distribution uniform`).  
  **Example:** `--latency-max 50`

- **`--latency-sched <value>`**  
  [Intervals scheduling](./schedule-intervals-syntax.md) when to apply the fault (require `--duration` whhen using relative schedule).  
  **Example:** `--latency-sched "start:30s,duration:60s"`
  **Example:** `--latency-sched "start:5%,duration:40%"` (requires `--duration`)

---

### Bandwidth Options

- **`--with-bandwidth`**  
  Enable bandwidth fault injection.  
  _Default:_ Disabled

- **`--bandwidth-side <side>`**  
  Side to apply the bandwidth fault. Options: `client`, `server`  
  _Default:_ `server`

- **`--bandwidth-direction <direction>`**  
  Direction to apply the bandwidth fault. Options: `ingress`, `egress`, `both`  
  _Default:_ `ingress`

- **`--bandwidth-rate <value>`**  
  Bandwidth rate as a positive integer.  
  _Default:_ `1000`

- **`--bandwidth-unit <unit>`**  
  Unit for the bandwidth rate (options: Bps, KBps, MBps, GBps).  
  _Default:_ `Bps`

- **`--bandwidth-sched <value>`**  
  [Intervals scheduling](./schedule-intervals-syntax.md) when to apply the fault (require `--duration` whhen using relative schedule).  
  **Example:** `--bandwidth-sched "start:30s,duration:60s"`
  **Example:** `--bandwidth-sched "start:5%,duration:40%"` (requires `--duration`)

---

### Jitter Options

- **`--with-jitter`**  
  Enable jitter fault injection.  
  _Default:_ Disabled

- **`--jitter-direction <direction>`**  
  Direction to apply the jitter fault. Options: `ingress`, `egress`, `both`  
  _Default:_ `ingress`

- **`--jitter-amplitude <value>`**  
  Maximum jitter delay in milliseconds (non-negative float).  
  _Default:_ `20.0`

- **`--jitter-frequency <value>`**  
  Frequency of jitter application in Hertz times per second (non-negative float).  
  _Default:_ `5.0`

- **`--jitter-sched <value>`**  
  [Intervals scheduling](./schedule-intervals-syntax.md) when to apply the fault (require `--duration` whhen using relative schedule).  
  **Example:** `--jitter-sched "start:30s,duration:60s"`
  **Example:** `--jitter-sched "start:5%,duration:40%"` (requires `--duration`)

---

### DNS Options

- **`--with-dns`**  
  Enable DNS fault injection.  
  _Default:_ Disabled

- **`--dns-rate <value>`**  
  Probability to trigger a DNS failure (non-negative float).  
  _Default:_ `0.5`

- **`--dns-sched <value>`**  
  [Intervals scheduling](./schedule-intervals-syntax.md) when to apply the fault (require `--duration` whhen using relative schedule).  
  **Example:** `--dns-sched "start:30s,duration:60s"`
  **Example:** `--dns-sched "start:5%,duration:40%"` (requires `--duration`)

---

### Packet Loss Options

- **`--with-packet-loss`**  
  Enable packet loss fault injection.  
  _Default:_ Disabled

- **`--packet-loss-direction <direction>`**  
  Direction to apply the packet loss fault. Options: `ingress`, `egress`, `both`  
  _Default:_ `ingress`

- **`--packet-loss-sched <value>`**  
  [Intervals scheduling](./schedule-intervals-syntax.md) when to apply the fault (require `--duration` whhen using relative schedule).  
  **Example:** `--packet-loss-sched "start:30s,duration:60s"`
  **Example:** `--packet-loss-sched "start:5%,duration:40%"` (requires `--duration`)

---

### HTTP Response Options

- **`--with-http-response`**  
  Enable HTTP response fault injection (return a predefined response).  
  _Default:_ Disabled

- **`--http-response-direction <direction>`**  
  Direction to apply the HTTP response fault. Options: `ingress`, `egress`, `both`  
  _Default:_ `ingress`

- **`--http-response-status <code>`**  
  HTTP status code to return (e.g., 500, 503).  
  _Default:_ `500`

- **`--http-response-body <string>`**  
  Optional response body to return.  
  _Default:_ (none)

- **`--http-response-trigger-probability <value>`**  
  Probability (0.0 to 1.0) to trigger the HTTP response fault.  
  _Default:_ `1.0` (always trigger when enabled)

- **`--http-response-sched <value>`**  
  [Intervals scheduling](./schedule-intervals-syntax.md) when to apply the fault (require `--duration` whhen using relative schedule).  
  **Example:** `--http-response-sched "start:30s,duration:60s"`
  **Example:** `--http-response-sched "start:5%,duration:40%"` (requires `--duration`)

---

### Blackhole Options

- **`--with-blackhole`**  
  Enable blackhole fault injection.  
  _Default:_ Disabled

- **`--blackhole-direction <direction>`**  
  Direction to apply the blackhole fault. Options: `ingress`, `egress`, `both`  
  _Default:_ `ingress`

- **`--blackhole-sched <value>`**  
  [Intervals scheduling](./schedule-intervals-syntax.md) when to apply the fault (require `--duration` whhen using relative schedule).  
  **Example:** `--blackhole-sched "start:30s,duration:60s"`
  **Example:** `--blackhole-sched "start:5%,duration:40%"` (requires `--duration`)

---

### Usage Examples

#### Running the Proxy with Multiple Faults

```bash
lueur run \
  --proxy-address "127.0.0.1:8080" \
  --with-latency --latency-mean 120.0 --latency-stddev 30.0 \
  --with-bandwidth --bandwidth-rate 2000 --bandwidth-unit KBps
```

## `scenario` Command Options

A lueur scenario is a file containing test scenarios to execute automatically
by lueur generating report and result files for further analysis.

### Proxy Configuration Options

- **`--proxy-address <address>`**  
  _Listening address for the proxy server._  
  _Default:_ `127.0.0.1:8080`  
  **Example:** `--proxy-address 192.168.12.45:8090`

### Scenario Options

- **`--scenario <file>`**  
  _Path to a YAML scenario file._  
  **Example:** `--scenario ./scenario.yaml`

- **`--report <file>`**  
  _Path to a file where to save the final repor._  
  **Example:** `--scenario ./report.yaml`

## `demo` Command Options

A simple demo server listening for HTTP requests.

### Demo Options

- **`--address <addr>`**  
  _IP address to bind the the demo server to._  
  _Default:_ `127.0.0.1`  
  **Example:** `--address 192.168.2.34`

- **`--port <port>`**  
  _Port to bind to._  
  _Default:_ `7070`  
  **Example:** `--port 8989`
