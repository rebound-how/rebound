# How to Blackhole Traffic Using fault

This guide will walk you through emulating network severe degradation into your
application using fault proxy capabilities.

??? abstract "Prerequisites"

    -   [X] Install fault

        If you haven’t installed fault yet, follow the
        [installation instructions](../../install.md).

    -   [X] Basic Proxy Setup
        Be familiar with running fault run {==--with-[fault]==} commands from
        your terminal.

## Completely Blackhole All Traffic

In this scenario traffic is blackholed indefinitely and no packets will get
through to its destination.

The client or application will attempt to connect or send data but never receive
a response, eventually timing out.

-   [X] Start the proxy with blackhole fault

    ```bash
    fault run --with-blackhole
    ```

## Blackhole Traffic for Specific Time Windows

Often, you want to simulate a partial outage—periods of normal traffic followed
by complete blackhole intervals.

-   [X] Start the proxy with blackhole fault and a schedule

    ```bash
    fault run \
        --duration 10m \  # (1)!
        --with-blackhole \
        --blackhole-sched "start:10%,duration:50%;start:75%,duration:20%"  # (2)!
    ```

    1. Run the proxy process for 10 minutes
    2. At 10% of 10 minutes (the 1‐minute mark), start blackholing for 50% of
       total time (i.e., 5 minutes).
       Then, at 75% of 10 minutes (the 7.5‐minute mark), blackhole again for 20%
       of total time (2 minutes).
       Effect:
        * For the first minute, traffic flows normally.
        * Minutes 1–6: All traffic is blackholed (clients see no reply).
        * Minutes 6–7.5: Returns to normal.
        * Minutes 7.5–9.5: Blackhole again, finishing just before the proxy ends at 10 minutes.
