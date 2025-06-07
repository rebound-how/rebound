# Intercept Network Traffic Transparently

This guide will walk you through enabling <span class="f">fault</span>'s {==stealth mode==} to capture
network traffic without modifying your application.

!!! warning "This feature requires eBPF and a Linux host"

    This feature is only available on Linux as it relies on a kernel
    advanced capability called
    [ebpf](../../../explanations/understanding-ebpf.md).


??? abstract "Prerequisites"

    -   [X] Install <span class="f">fault</span> with Stealth mode support

        If you haven’t installed <span class="f">fault</span> yet, follow the
        [installation instructions](../../install.md#stealth-feature).

## Capture HTTPS Traffic

-   [X] Start the proxy in stealth mode with a normal distribution latency

    ```bash
    fault run \
        --stealth \ # (1)!
        --capture-process curl \ # (2)!
        --with-latency \ # (3)!
        --latency-mean 300 \
        --latency-stddev 40
    ```

    1.  Enable stealth mode
    2.  Stealth mode will focus only on processes named `curl`
    3.  Enable the latency fault support

-   [X] Send traffic

    ```bash
    curl \
        -4 \ # (1)!
        -I \ # (2)!
        -o /dev/null -s \ # (3)!
        -w "Connected IP: %{remote_ip}\nTotal time: %{time_total}s\n" \ # (4)!
        https://www.google.com
    ```

    1.  fault can only intercept IPv4 traffic
    2.  Let's only focus on a HEAD request for brevety
    3.  Discard any returned output
    4.  Display statistics about the call

## Apply Latency to a PostgreSQL Connection

-   [X] Install fault's ebpf dependencies
    
    Follow the procedure to
    [install](../../install.md#stealth-feature) the
    eBPF programs on your machine.

-   [X] Start a local PostgreSQL server using a container

    ```bash
    docker run \
        --name demo-db \ # (1)!
        -e POSTGRES_USER=demo \ # (2)!
        -e POSTGRES_PASSWORD=demo \ # (3)!
        -e POSTGRES_DB=demo \ # (4)!
        --rm -it \ # (5)!
        -p 5432:5432 \ # (6)!
        postgres
    ```

    1.  Name of the container, useful to identify and delete it later on
    2.  Default basic user named {{==demo==}}
    3.  Password set to {{==demo==}} for the user {{==demo==}}
    4.  Default database name
    5.  Release all resources once we stop the container
    6.  Expose the database port onto the host

-   [X] Start the proxy in stealth mode with a normal distribution latency

    ```bash
    fault run \
        --stealth \ # (1)!
        --capture-process curl \ # (2)!
        --with-latency \ # (3)!
        --latency-mean 300 \
        --latency-stddev 40
    ```

    1.  Enable stealth mode
    2.  Stealth mode will focus only on processes named `curl`
    3.  Enable the latency fault support

-   [X] Communicate with your PostgreSQL server

    First, install `uv` to run the demonstration script below. Follow the
    instructions from the
    [uv documentation](https://docs.astral.sh/uv/getting-started/installation/).

    Let's use the following basic Python script:

    ```python title="connect-to-pgsql.py"
    import time

    import psycopg


    def query_database_server_time(url: str) -> None:
        start = time.time()

        with psycopg.Connection.connect(url) as conn: # (1)!
            cur = conn.execute("select now()")
            print(cur.fetchone()[0])

        print(f"Time taken {time.time() - start}")


    if __name__ == "__main__":
        connection_url = "postgresql://demo:demo@localhost:5432/demo" # (2)!

        query_database_server_time(connection_url)
    ```

    1.  We are using a context manager which closes the connection automatically
    2.  This should reflect the address of your PostgreSQL database

    Run the script using `uv`.

    ```bash
    uv run \ # (1)!
        --with psycopg[binary] \  # (2)!
        python connect-to-pgsql.py
    ```

    1. Use {==uv==} to run the script with the required dependency
    2. Install the required dependency on the fly. Here the {==psycopg==} driver

    This should output something such as:

    ```bash
    2025-03-08 13:06:16.968350+00:00
    Time taken 0.30957818031311035  # (1)!
    ```

    1. This shows the impact of the latency injected by <span class="f">fault</span> into the exchange

    !!! info

        We use `uv` to ease the management of the Python environment for this
        particular script. When we run the script this way, the actual process
        executing the script is indeed `python`. This is why <span class="f">fault</span> captures
        the network traffic from the `python` process, not from `uv`.
