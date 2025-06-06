# How to Simulate Packet Loss Using <span class="f">fault</span>

This How-To guide shows you how to configure <span class="f">fault</span> so that a portion of your
traffic is lost. You can keep a persistent level of packet loss or schedule it
in specific bursts to test how your application handles intermittent
unreliability.

??? abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span>

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../../install.md).

    -   [X] Basic Proxy Setup
        Be familiar with running `fault run` {==--with-[fault]==} commands from
        your terminal.

    -   [X] Check Available Packet Loss Strategies

        <span class="f">fault</span> implements the Multi-State Markov strategy. Familiarize yourself
        with any advanced settings if needed.

## Constant Packet Loss

In this scenario, <span class="f">fault</span> starts with packet loss enabled throughout the entire
proxy run.

-   [X] Start the proxy with packet loss on ingress from server side

    ```bash
    fault run --with-packet-loss 
    ```

## Scheduled Packet Loss Bursts

-   [X] Start the proxy with packet loss fo

    ```bash
    fault run \
      --duration 10m \
      --with-packet-loss \
      --packet-loss-sched "start:5%,duration:20%;start:60%,duration:15%" # (1)!
    ```

    1.  At 5% of 10 minutes (the 30-second mark), enable packet loss for 20% (2 minutes total).
        At 60% of 10 minutes (the 6-minute mark), enable packet loss again for 15% (1.5 minutes).

        Timeline:
        * Minutes 0–0.5: No loss (normal).
        * Minutes 0.5–2.5: Packet loss enabled (clients see up to some “lost” packets).
        * Minutes 2.5–6.0: Normal again.
        * Minutes 6.0–7.5: Packet loss resumes.
        * Remaining time to minute 10: No loss.

## Next Steps

- Monitor Application Behavior: Track if clients adapt or retry effectively when
  some packets vanish.
- Combine with Other Faults: For deeper reliability testing, mix packet loss
  with [latency](./configure-latency.md) or [bandwidth](configure-bandwidth.md)
  constraints.
