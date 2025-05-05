# Proxy Lifecycle

The default behavior of the lueur's proxy is to run indefinitely. You may
change that by setting the `--duration` flag with a value in seconds. Once this
duration has been reached, the proxy will automatically terminates.

```bash
lueur run --duration 10m ...
```

The flag supports a variety of
[units](https://docs.rs/parse_duration/latest/parse_duration/#units) to
express the duration more conveniently.

Setting the duration has a nice side-effect that the scheduling of
fault injections can be declared relatively to this duration. For instance:

```bash
lueur run --duration 5m --latency-sched "start:5%;duration:30%;start:90%,duration:5%"
```

* lueur will run for `5 minutes`
* A first wave of latency will start after `15s` and run for `90s`
* A second wave of latency will start after `270s` and run for `15s`

