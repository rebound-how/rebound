# Proxy Lifecycle

## Duration

The default behavior of the <span class="f">fault</span>'s proxy is to run indefinitely. You may
change that by setting the `--duration` flag with a value in seconds. Once this
duration has been reached, the proxy will automatically terminates.

```bash
fault run --duration 10m ...
```

The flag supports a variety of
[units](https://docs.rs/parse_duration/latest/parse_duration/#units) to
express the duration more conveniently.

Setting the duration has a nice side-effect that the scheduling of
fault injections can be declared relatively to this duration. For instance:

```bash
fault run --duration 5m --latency-sched "start:5%;duration:30%;start:90%,duration:5%"
```

* <span class="f">fault</span> will run for `5 minutes`
* A first wave of latency will start after `15s` and run for `90s`
* A second wave of latency will start after `270s` and run for `15s`

When a duration is set, <span class="f">fault</span> displays a progress bar:

```bash
⠏ Progress: ------------------------------------------🐢-------- 🏁
```


## Scheduling

<span class="f">fault</span> applies faults for the entire duration of the run by default. You may
change this by setting a schedule for each enabled fault.

A schedule defines a sequence of {==start, duration==} for the fault. These
values describe ranges when a particular fault should be enabled. The rest of
the time, the fault is disabled.

The {==start==} and {==duration==} should be either fixed, and set in seconds,
of relative and set as a percentage of the total runtime. In that latter case,
you must pass the total duration via `--duration`.

Mixing relative and fixed schedules is supported.

!!! note

    Relative scheduling is declared using percentages of the total duration.
    It is not a ratio of seen requests.

!!! example "Fixed Schedule"

    ```bash
    fault run \
        ... \
        --latency-sched "start:20s,duration:40s;start:80s,duration:30s" \
        ...
        --bandwidth-sched "start:35s,duration:20s"
    ```

    <img src="/assets/images/fixed-schedule.png">


!!! example "Relative Schedule"

    ```bash
    fault run --duration 5m \
        ... \
        --latency-sched "start:5%,duration:30%;start:90%,duration:5%" \
        ... \
        --bandwidth-sched "start:125s,duration:20s;start:70%,duration:5%"
    ```

    <img src="/assets/images/relative-schedule.png">
