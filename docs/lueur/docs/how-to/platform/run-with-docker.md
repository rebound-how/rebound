# Run lueur as a Docker Container

This guide will show you how can you easily introduce network faults with 
Docker containers.

## What You'll Achieve

You will learn how to use lueur in a Docker environment, either as
a standalone container or as part of a set of services orchestrated with
Docker Compose.

## Run lueur as A Container - Step-by-Step

-   [X] Pull the lueur image

    ```bash
    docker pull rebound/lueur
    ```

-   [X] Run lueur with a latency fault

    ```bash
    docker run \
        -p 8080:8080 \  # (1)!
        --rm \  # (2)!
        -it \  # (3)!
        rebound/lueur \ 
            run \
            --proxy-address 0.0.0.0:8080  \ # (4)!
            --upstream http://192.168.1.3:7070 \  # (5)!
            --with-latency --latency-mean 300
    ```

    1. Expose the proxy port if you need to access it from the host
    2. Release the system resources once the container finishes
    3. Give the process a terminal
    4. The default behavior is to bind the proxy to the loopback which would prevent the proxy from being reached. Bind to all public interfaces with `0.0.0.0`
    5. The address of the demo application we will apply the latency to

-   [X] Run the lueur demo using the same image

    ```bash
    docker run \
        -p 7070:7070 \  # (1)!
        rebound/lueur \
            demo run 0.0.0.0  # (2)!
    ```

    1. Expose the demo application port to the host
    2. Run the demo server and bind to all container's interfaces

-   [X] Make a request to the demo application and see it impacted by the proxy

    ```bash
    curl \
        -w "\nConnected IP: %{remote_ip}\nTotal time: %{time_total}s\n" \
        -x http://localhost:8080 \
        http://192.168.1.3:7070

    <h1>Hello, World!</h1>
    Connected IP: ::1
    Total time: 0.313161s
    ```

## Run Stealh Mode in A Container - Step-by-Step

!!! warning

    Stealth mode gives the opportunity to intercept traffic without having to
    explicitely set the proxy on the client. It relies on eBPF and therefore
    requires a lot of provileges which likely you would not have in a production
    environment.

-   [X] Pull the lueur image

    ```bash
    docker pull rebound/lueur
    ```

-   [X] Run lueur with a latency fault

    ```bash
    docker run \
        -p 8080:8080 \  # (1)!
        -p 8089:8089 \  # (2)!
        --rm \  # (3)!
        -it \  # (4)!
        --network=host \  # (5)!
        --pid=host \ # (6)!
        -v /sys/fs/cgroup/:/sys/fs/cgroup/:ro \ # (7)!
        --cap-add=SYS_ADMIN \ # (8)!
        --cap-add=BPF \ # (9)!
        --cap-add=NET_ADMIN \ # (10)!
        rebound/lueur \ 
            run \
            --stealth \  # (11)!
            --ebpf-proxy-port 8989 \  # (12)!
            --proxy-address 0.0.0.0:8080  \  # (13)!
            --upstream http://192.168.1.3:7070 \  # (14)!
            --with-latency --latency-mean 300
    ```

    1. Expose the proxy port if you need to access it from the host
    2. Expose the eBPF proxy port
    3. Release the system resources once the container finishes
    4. Give the process a terminal
    5. Share the host network as in our example, the client runs on the host. You could also share another container's network instead
    6. Share the host porocess namespace to access the client's process
    7. Give access to the host's kernel resources for lueur eBPF programs to attach to
    8. Give too much power to the container but unfortunately we cannot reduce the scope so we need it
    9. Specific BPF priviledges
    10. lueur needs quite a bit of access to networking to do its job
    11. Enable stealth mode and loads eBPF programs
    12. By default, lueur picks up a random port for listening to traffic routed via ebBPF, but we need to set it to expose it
    13. The default behavior is to bind the proxy to the loopback which would prevent the proxy from being reached. Bind to all public interfaces with `0.0.0.0`
    14. The address of the demo application we will apply the latency to. Note that this is ignored by lueur for now

-   [X] Run the lueur demo using the same image

    ```bash
    docker run \
        -p 7070:7070 \  # (1)!
        rebound/lueur \
            demo run 0.0.0.0  # (2)!
    ```

    1. Expose the demo application port to the host
    2. Run the demo server and bind to all container's interfaces

-   [X] Make a request to the demo application and see it impacted by the proxy

    ```bash
    curl \
        -w "\nConnected IP: %{remote_ip}\nTotal time: %{time_total}s\n" \
        http://192.168.1.3:7070

    <h1>Hello, World!</h1>
    Connected IP: ::1
    Total time: 0.313161s
    ```

    Notice how we do not need to be explicit about routing traffic to the
    proxy by omitting setting `-x http://localhost:8080`
