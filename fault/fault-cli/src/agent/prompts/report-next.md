# Rules & Constraints

- Suggest a few more resilience and reliability configuration to explore further
- Use the `fault` command line [https://fault-project.com/][https://fault-project.com/] to create relevant use cases

{# – Context from recommendations –#}
{% if previous_advice %}
### Previous Analysis  
```text
{{ previous_advice }}
```  

---
{% endif %}

# Step 6: Next Exploration

You are a senior **{{ role | capitalize }}**.  
Based on the following fault examples, provide more test use cases that could
explore further.


Draw inspiration from the example good response below but don't copy it as-is.

```markdown
    ## More Reliability Tests

    ```bash
    # How a front-end handles “realistic” network jitter/latency
    fault run \
        --upstream '*' \
        --with-latency \
        --latency-side server \
        --latency-direction both \
        --latency-distribution normal \
        --latency-mean 100.0 \
        --latency-stddev 20.0 \
        --duration 5m
    ```

    ```bash
    # Quickly see if client-side code backs off properly or times out under a
    # slow uplink.
    fault run \
        --upstream '*' \
        --with-bandwidth \
        --bandwidth-side client \
        --bandwidth-direction egress \
        --bandwidth-rate 500 \
        --bandwidth-unit KBps \
        --duration 10m
    ```

    ```bash
    # Good for uncovering race conditions or timeouts in code that assumes
    # steady network.
    fault run \
        --upstream '*' \
        --with-jitter \
        --jitter-side server \
        --jitter-direction ingress \
        --jitter-amplitude 20.0 \
        --jitter-frequency 10.0 \
        --duration 3m
    ```

    ```bash
    # Great way to see how client library / retry logic reacts to intermittent
    # packet loss + sporadic 503s under load.
    fault run \
        --upstream '*' \
        --with-packet-loss \
        --packet-loss-direction both \
        --packet-loss-probability 0.10 \
        --with-http-response \
        --http-response-direction both \
        --http-response-status 503 \
        --http-response-trigger-probability 0.05 \
        --duration 2m
    ```

    ```bash
    # Useful to simulate a "chaos monkey" network in a staging
    # environment, letting you replay all API calls through the proxy and watch
    # how microservices mesh handles cascading failures.
    fault run \
        --upstream '*' \
        --duration 5m \
        --with-bandwidth --bandwidth-rate 300 --bandwidth-unit KBps \
        --with-jitter --jitter-side server --jitter-amplitude 50 --jitter-frequency 2 \
        --with-dns --dns-rate 0.3
    ```
```
