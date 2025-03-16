# tl;dr

## The one-liner lueur proxy

The following command starts the proxy impacting any requests to any upstream
server with a `300ms` latency on average.

```console
lueur run --with-latency --latency-mean=300 --upstream=* 
```

That's it!

## Next Steps

* **Start exploring our [tutorials](getting-started.md)** to gently get into using lueur.
* **Explore our [How-To guides](../how-to/proxy/faults/configure-latency.md)** to explore lueur's features.
