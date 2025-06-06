# How to Inject Latency into Your Flow with <span class="f">fault</span>

This guide shows how to delay traffic by a configurable amount, distribution,
side (client or server), and direction (ingress or egress). You can simulate
everything from a stable normal latency to heavy-tailed Pareto scenarios and
selectively apply them to only client or server traffic.

??? abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span>

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../../install.md).

    -   [X] Basic Proxy Setup
        Be familiar with running `fault run` {==--with-[fault]==} commands from
        your terminal.

## Normal Distribution

A normal (Gaussian) distribution around a mean of `300ms` with a standard
deviation of `40ms`.

Most delays hover around `300ms`, but some are quicker/slower based on the bell
curve.

-   [X] Start the proxy with a normal distribution latency

    ```bash
    fault run \
        --with-latency \ # (1)!
        --latency-distribution normal \ # (2)!
        --latency-mean 300 \ # (3)!
        --latency-stddev 40 # (4)!
    ```

    1.  Enable the latency fault support
    2.  Use the {==normal==} distribution
    3.  Introduce a latency of {==300ms==} on average
    4.  Add {==40ms==} standard deviation `±40 ms`

## Uniform Distribution

A uniform distribution means every delay in `min..max` is equally likely.

The added delay is anywhere between `300 / 500ms` without bias around a middle
value.

-   [X] Start the proxy with a uniform distribution latency

    ```bash
    fault run \
        --with-latency \ # (1)!
        --latency-distribution uniform \ # (2)!
        --latency-min 300 \ # (3)!
        --latency-max 500 # (4)!
    ```

    1.  Enable the latency fault support
    2.  Use the {==uniform==} distribution
    3.  Introduce a latency of at least {==300ms==}
    4.  Set the maximum latency to {==500ms==}


## Pareto Distribution

A Pareto distribution often creates a heavy‐tail, meaning most delays are small,
but occasional extremely large spikes.

You’ll see frequent short delays (`20ms` or so) but occasionally large outliers.

-   [X] Start the proxy with a Pareto distribution latency

    ```bash
    fault run \
        --with-latency \ # (1)!
        --latency-distribution pareto \ # (2)!
        --latency-scale 20 \ # (3)!
        --latency-shape 1.5 # (4)!
    ```

    1.  Enable the latency fault support
    2.  Use the {==pareto==} distribution
    3.  Set a scale of {==20ms==}
    4.  Set the shape of the distribution to {==1.5==}

## Pareto + Normal Hybrid Distribution

Get a base normal offset of `~50±15ms`, plus a heavy‐tailed portion from the
Pareto factors.

-   [X] Start the proxy with a Pareto + Normal distribution latency

    ```bash
    fault run \
        --with-latency \ # (1)!
        --latency-distribution paretonormal \ # (2)!
        --latency-scale 20 \ # (3)!
        --latency-shape 1.5 \ # (4)!
        --latency-mean 50 \ # (5)!
        --latency-stddev 15 # (6)!
    ```

    1.  Enable the latency fault support
    2.  Use the {==pareto==} distribution
    3.  Set a scale of {==20ms==}
    4.  Set the shape of the distribution to {==1.5==}
    5.  Set a mean of {==50ms==} on average
    6.  Standard deviation of {==15ms==} around that mean.

## Latency On Ingress Only

Delay traffic from the server to the client.

-   [X] Start the proxy with any distribution and set the direction to {==ingress==}.

    ```bash
    fault run \
        --with-latency \ # (1)!
        --latency-direction ingress \ # (2)!
        --latency-mean 50
    ```

    1.  Enable the latency fault support
    2.  Set the latency to take place in {==ingress==}

## Latency On Egress Only

Delay traffic from the client to the server.

-   [X] Start the proxy with any distribution and set the direction to {==egress==}.

    ```bash
    fault run \
        --with-latency \ # (1)!
        --latency-direction egress \ # (2)!
        --latency-mean 50
    ```

    1.  Enable the latency fault support
    2.  Set the latency to take place in {==egress==}

## Latency On Client-Side Only

-   [X] Start the proxy with any distribution and set the side to {==client==}.

    ```bash
    fault run \
        --with-latency \ # (1)!
        --latency-side client \ # (2)!
        --latency-mean 50
    ```

    1.  Enable the latency fault support
    2.  Set the latency to take place on {==client==} side

## Latency On Server-Side Only

-   [X] Start the proxy with any distribution and set the side to {==server==}.

    ```bash
    fault run \
        --with-latency \ # (1)!
        --latency-side server \ # (2)!
        --latency-mean 50
    ```

    1.  Enable the latency fault support
    2.  Set the latency to take place on {==server==} side


## Latency On Ingress From Server-Side Only

-   [X] Start the proxy with any distribution and set the direction to {==ingress==} and the side to {==server==}.

    ```bash
    fault run \
        --with-latency \
        --latency-direction ingress \
        --latency-side server \
        --latency-mean 50
    ```

## Next Steps

- Scheduled Delays: Use `--latency-sched "start:20%,duration:30%"` to enable
  high latency for part of the total run.
- Stacking: Combine latency with [jitter](configure-jitter.md) or
  [bandwidth](configure-bandwidth.md) constraints for a more
  realistic environment.
- Extreme Spikes: Increase standard deviation or shape to stress test how your
  application handles sudden bursts of slowness.
