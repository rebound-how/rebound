# tl;dr

## The one-liner <span class="f">fault</span> HTTP proxy

The following command starts the proxy impacting any HTTP requests to any
upstream host with a `300ms` latency on average.

```console
fault run --with-latency --latency-mean=300 --upstream=* 
```

Send your HTTP/HTTPS traffic to `<proxy ip>:3180` and observe the latency
impacting the response time.

## The one-liner <span class="f">fault</span> TCP proxy

The following command starts the proxy impacting any TCP stream to host
`remote.com:9000` with a `300ms` latency on average.

```console
fault run --with-latency --latency-mean=300 --proxy "7878:remote.com:9000"
```

Replace `remote.com:9000` with `<proxy ip>:7878` in your application.

## Next Steps

* **Start exploring our [tutorials](getting-started.md)** to gently get into using <span class="f">fault</span>.
* **Explore our [How-To guides](../how-to/proxy/faults/configure-latency.md)** to explore <span class="f">fault</span>'s features.
