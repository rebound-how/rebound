# Proxy Fault Scheduling Intervals

fault provides a simple, yet flexible, syntax to schedule faults with intervals.
By defining these intervals, you can create richer scenarios that resemble more
real-life network conditions.

## What is an interval?

Each network fault takes a flag to declare such scheduling. When unset, the
fault runs continuously from start to finish.

An interval is made of two tokens:

* a starting point: determines when the fault should be apply by fault
* a duration: defines how long this fault should be run for

When the starting point is unset, fault takes this as "run from the beginning".
When no duration is set, fault understand you want to run from the given
starting point all the way to the end.

To create multiple intervals, you can repeat these as many times as your
scenario requires.

### Fixed vs Relative

An interval may be fixed or relative. A fixed interval uses concrete time units,
such as a seconds or minutes. These are independant from how long the proxy
runs for. Relative intervals uses percentages of the total duration of the
run. They explicitely require that the user defines a total duration via
the `--duration` flag.

Relative intervals are powerful because the stretch or shrink withe the
declared duration. That means these intervals are more portable.

## Grammar

The schedule grammar is a tiny DSL. Below is its EBNF grammar:

```ebnf
schedule       = period *(";" period) ;
period         =  start_clause [ "," duration_clause ] | duration_clause ;
start_clause   = "start" ":" time_spec ;
duration_clause= "duration" ":" time_spec ;
time_spec      = fraction | duration ;
fraction       = integer "%" ;
duration       = integer time_unit ;
time_unit      = "ms" | "s" | "m" | "h" | "d" | "w" 
integer        = DIGIT { DIGIT } ;
DIGIT          = "0" | "1" | "2" | "3" | "4"
               | "5" | "6" | "7" | "8" | "9" ;
```

## Examples

Here are a few examples:

**Fixed interval**

```bash
--latency-sched "start:30s;duration:3m"
```

**Fixed intervals With Many Fauts**

```bash
--latency-sched "start:30s;duration:3m"  --packet-loss-sched "start:2m;duration:25s"
```

**Fixed interval full duration**

```bash
--latency-sched "start:30s"
```

**Fixed interval limited duration**

```bash
--latency-sched "duration:50s"
```

**Fixed intervals**

```bash
--latency-sched "start:30s;duration:3m;start:4m,duration:45s"
```

**Mixed intervals**

```bash
--latency-sched "start:30s;duration:3m;start:4m"
```

**Mixed relative/fixed intervals**

```bash
--duration 5m --latency-sched "start:30s;duration:3m;start:90%,duration:5%"
```

**Relative intervals**

```bash
--duration 5m --latency-sched "start:5%;duration:30%;start:90%,duration:5%"
```
