# How to Simulate Bandwidth Constraints Using <span class="f">fault</span>

This guide shows you how to reduce or throttle network bandwidth in your
application flow with <span class="f">fault</span>. You’ll see examples of slowing traffic on the
server side, client side, or both directions.

??? abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span>

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../../install.md).

    -   [X] Basic Proxy Setup
        Be familiar with running `fault run` {==--with-[fault]==} commands from
        your terminal.

## Severe Upstream Slowdown

In this scenario, server-side ingress traffic is heavily constrained, so data
returning from the server becomes painfully slow for the client.

Any responses from the server are throttled to 500 kbps, causing slow downloads
or streaming on the client side.

-   [X] Start the proxy with bandwidth set from server-side ingress

    ```bash
    fault run \
        --with-bandwidth \ # (1)!
        --bandwidth-side server \ # (2)!
        --bandwidth-direction ingress \ # (3)!
        --bandwidth-rate 500 \ # (4)!
        --bandwidth-unit kbps
    ```

    1.  Enable the bandwidth fault support
    2.  Apply the fault on {==server==} side
    3.  Apply the fault on {==ingress==}
    4.  Set a very limited bandwidth to 500kbps

## Light Client Slowdown

Here, you cap both inbound and outbound bandwidth on the client side, but only
to a moderate level.

The client’s uploads and downloads are each capped at `1 Mbps`. This tests how
your app behaves if the client is the bottleneck.

-   [X] Start the proxy with bandwidth set from client-side both ingress and egress

    ```bash
    fault run \
        --with-bandwidth \ # (1)!
        --bandwidth-side client \ # (2)!
        --bandwidth-direction both \ # (3)!
        --bandwidth-rate 1 \ # (4)!
        --bandwidth-unit mbps
    ```

    1.  Enable the bandwidth fault support
    2.  Apply the fault on {==client==} side
    3.  Apply the fault on {==ingress==} and {==egress==}
    4.  Set a reduced bandwidth to 1mbps

## Throughput Degradation

In this scenario, we combine ingress and egress on the server side, giving a
moderate throughput limit of `2 Mbps`. This is helpful for general
"server is maxing out" scenarios.

Uploads and downloads from the server are capped at `2 Mbps`, simulating
moderate network constraints on the server side.

-   [X] Start the proxy with bandwidth set from server-side both ingress and egress

    ```bash
    fault run \
        --with-bandwidth \ # (1)!
        --bandwidth-side server \ # (2)!
        --bandwidth-direction both \ # (3)!
        --bandwidth-rate 2 \ # (4)!
        --bandwidth-unit mbps
    ```

    1.  Enable the bandwidth fault support
    2.  Apply the fault on {==server==} side
    3.  Apply the fault on {==ingress==} and {==egress==}
    4.  Set a reduced bandwidth to 2mbps

## Mobile Edge / 3G‐Style Network

Simulates a high‐latency, low‐throughput link.

The user sees slow and sluggish performance typical of older mobile networks.

-   [X] Start the proxy with bandwidth and latency faults

    ```bash
    fault run \
        --duration 10m \
        --with-bandwidth \  # (1)!
            --bandwidth-side client \
            --bandwidth-direction both \
            --bandwidth-rate 384 \
            --bandwidth-unit kbps \
        --with-latency \  # (2)!
            --latency-mean 200 \
            --latency-stddev 50
    ```

    1. Both ingress and egress are capped to about 384 kbps (typical of older 3G)
    2. Latency of ~200±50ms is layered on to reflect mobile edge behavior

## Next Steps

- Combine with [Latency](./configure-latency.md): For a more realistic
  environment, layer static latency (`--with-latency`) plus bandwidth fault.
