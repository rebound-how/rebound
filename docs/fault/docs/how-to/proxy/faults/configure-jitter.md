# How to Simulate Jitter Using <span class="f">fault</span>

This guide explains how to introduce variable latency (jitter) into your
application flow. Jitter is random, short‐term fluctuations in latency that can
disrupt real‐time communication or stream quality.

??? abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span>

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../../install.md).

    -   [X] Basic Proxy Setup
        Be familiar with running `fault run` {==--with-[fault]==} commands from
        your terminal.

## Light Ingress Jitter

In this example, incoming (ingress) traffic experiences a mild, random delay.

Inbound data from the server to the client is randomly delayed by up to 30ms,
repeated at a frequency of 5 times per second, causing mild but noticeable
fluctuations.

-   [X] Start the proxy with jitter on ingress

    ```bash
    fault run \
        --with-jitter \ # (1)!
        --jitter-amplitude 30 \ # (2)!
        --jitter-frequency 5 \ # (3)!
        --jitter-direction ingress # (4)!
    ```

    1.  Enable the jitter fault support
    2.  Set the {==amplitude==} which  the maximum random delay added to each packet
    3.  Set the {==frequency==} representing how often jitter is applied per second
    4.  Apply the fault on {==ingress==}

## Strong Egress Jitter

Here, you impose a larger jitter on outbound traffic, simulating choppy sends
from the client to the server.

Outgoing data from the client can sporadically stall by up to `50ms`, repeated
10 times a second. This is a heavier jitter that can disrupt interactive or
streaming client uploads.

-   [X] Start the proxy with jitter on egress

    ```bash
    fault run \
        --with-jitter \ # (1)!
        --jitter-amplitude 50 \ # (2)!
        --jitter-frequency 10 \ # (3)!
        --jitter-direction egress # (4)!
    ```

    1.  Enable the jitter fault support
    2.  Set the {==amplitude==} which  the maximum random delay added to each packet
    3.  Set the {==frequency==} representing how often jitter is applied per second
    4.  Apply the fault on {==egress==}

## Bidirectional Jitter

Here, all traffic, whether inbound or outbound, suffers random short spikes.
This is great for testing two‐way real‐time apps.

-   [X] Start the proxy with jitter on egress and ingress

    ```bash
    fault run \
        --with-jitter \ # (1)!
        --jitter-amplitude 30 \ # (2)!
        --jitter-frequency 8 \ # (3)!
        --jitter-direction both # (4)!
    ```

    1.  Enable the jitter fault support
    2.  Set the {==amplitude==} which  the maximum random delay added to each packet
    3.  Set the {==frequency==} representing how often jitter is applied per second
    4.  Apply the fault on {==egress==} and {==ingress==}

## Next Steps

- Combine with [Latency](./configure-latency.md): For a more realistic
  environment, layer static latency (`--with-latency`) plus jitter for base
  latency + random spikes.

- Vary the Frequency: If your application is bursty, reduce frequency for
  occasional stutters.

- Apply Schedules: Use `--jitter-sched` to enable jitter in short intervals
  (e.g., [start:20%,duration:30%]), toggling unpredictably.

By adjusting amplitude and frequency and applying them to ingress, egress, or
both, you can simulate a wide spectrum of jitter conditions—from slight
fluctuations to severe choppy networks.
