# How to Simulate Network Faults On Any TCP-based Traffic

This guide shows you how to use <span class="f">fault</span> to simulate network faults on any
TCP-oriented network traffic, even with TLS encryption.

??? abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span>

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../../install.md).

    -   [X] Basic Proxy Setup
        Be familiar with running `fault run` {==--with-[fault]==} commands from
        your terminal.

    -   [X] Understanding of TCP Proxying
        Explore the [TCP proxy protocol reference](../../../reference/proto-syntax.md).


??? question "Do I still need `HTTP_PROXY` or `HTTPS_PROXY`?"

    When you setup a proxy, you are effectively swapping your target
    address with the proxy's address in your application. You do not need to
    set the standard these environment variables.

??? question "What about encryption?"

    The traffic from the client to the proxy is in clear. From the proxy
    to the target host, the traffic is encrypted if the endpoint expects
    it to be.

    A future version of <span class="f">fault</span> may allow to encrypt the traffic between
    client and proxy as well with your own certificate.


## Create a Dedicated TCP Proxy

<span class="f">fault</span> can create any number of proxies that can be used as endpoints by
your applications to experiment with network fault impacts.

-   [X] Start a proxy on port `9098`

    ```bash
    fault run \
        --proxy "9098=https://www.google.com:443" \ # (1)!
        --with-latency \
        --latency-mean 300
    ```

    1. Make sure to set a host and its port. fault cannot figure it out.

    You can use as many `--proxy` flags as needed. <span class="f">fault</span> will start
    listening on port {==9098==} for TCP connections. Any network going to that
    the address {==0.0.0.0:9098==} will be transmitted to the endpoint, here
    `https://www.google.com`. <span class="f">fault</span> will apply any faults you have setup to the
    traffic. Please read the
    [reference](../../../reference/proto-syntax.md#grammar). for the supported
    definition of the proxy protocol.

-   [X] Make a request to the endpoint via our proxy

    ```bash
    curl \
        -4 \  # (1)!
        -H "Host: www.google.com" \  # (2)!
        -I \
        -o /dev/null -s \
        -w "Connected IP: %{remote_ip}\nTotal time: %{time_total}s\n" \ 
    https://0.0.0.0:9098  # (3)!
    ```

    1. fault's proxy only support IPv4 for now. That my change in the future.
    2. Make sure the `Host` headers matches the actual target server.
    3. Instead of connecting to `https://www.google.com`, we connect to the
       proxy and let it forward our HTTP request to `https://www.google.com`
       on our behalf.
       Note that the proxy doesn't make a request, the traffic sent by curl is
       sent as-is (aside from the network faults) to the final target endpoint.

## Simulate Network Faults on PostgreSQL Traffic

While you may benefit from learning how network faults impact your application
at the API (often HTTP) level, it may also be valuable to explore effects from
dependencies such as traffic between your application and its database.

-   [X] Start a proxy on port `35432`

    ```bash
    fault run \
        --proxy "35432=localhost:5432" \ # (1)!
        --with-latency \
        --latency-mean 800 \  # (2)!
        --latency-per-read-write  # (3)!
    ```

    1. Let's assume the database is local and listening on port `5432`.
       Change to match your system.
    2. Let's use a fairly high latency to notice it
    3. The default for latency faults is to be applied only once in the
       life of the connection. With `--latency-per-read-write` you tell <span class="f">fault</span>
       to apply the fault on any read or write operation. This is useful
       here for our example because we will connect with {==psql==} and without
       this flag, the latency would be applied only once at connection time.

-   [X] Connect with {==psql==} to the PostgreSQL server via <span class="f">fault</span>'s proxy

    ```bash
    psql -h localhost \ # (1)!
        -p 35432 \ # (2)!
        -U demo \ # (3)!
        -d demo # (4)!
    ```

    1. The address of your the <span class="f">fault</span>'s proxy. You may use `localhost` here or
       a non-loopback address since the proxy is bound to all interfaces with
       `0.0.0.0`
    2. The proxy's port
    3. The username to connect to the server, adjust to your own system
    4. The database name, adjust to your own system

    Once you are connected, any query made to the server will go through the
    proxy which will apply the configured network faults to it.
