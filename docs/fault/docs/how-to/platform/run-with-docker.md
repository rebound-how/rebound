# Run fault as a Docker Container

This guide will show you how can you easily introduce network faults with 
Docker containers.

!!! info

    <span class="f">fault</span> container images are hosted on
    [GitHub Container Registry](https://github.com/rebound-how/rebound/pkgs/container/fault).

    They are [distroless](https://github.com/GoogleContainerTools/distroless)
    images available for amd64 and arm64 architectures.

## Run <span class="f">fault</span> as A Container

-   [X] Pull the <span class="f">fault</span> image

    ```bash
    docker pull ghcr.io/rebound-how/fault
    ```

    !!! warning
        
        This image is based on distroless and embeds the static version of the
        `fault` cli which
        [doesn't support the AI Agent feature](../install.md#features-matrix).

-   [X] Run <span class="f">fault</span> with a latency fault

    ```bash
    docker run \
        -p 3180:3180 \  # (1)!
        --rm \  # (2)!
        -it \  # (3)!
        ghcr.io/rebound-how/fault \ 
            run \
            --proxy-address 0.0.0.0:3180  \ # (4)!
            --upstream http://192.168.1.3:7070 \  # (5)!
            --with-latency --latency-mean 300
    ```

    1. Expose the proxy port if you need to access it from the host
    2. Release the system resources once the container finishes
    3. Give the process a terminal
    4. The default behavior is to bind the proxy to the loopback which would prevent the proxy from being reached. Bind to all public interfaces with `0.0.0.0`
    5. The address of the demo application we will apply the latency to

-   [X] Run the fault demo using the same image

    ```bash
    docker run \
        -p 7070:7070 \  # (1)!
        rebound/fault \
            demo run 0.0.0.0  # (2)!
    ```

    1. Expose the demo application port to the host
    2. Run the demo server and bind to all container's interfaces

-   [X] Make a request to the demo application and see it impacted by the proxy

    ```bash
    curl \
        -w "\nConnected IP: %{remote_ip}\nTotal time: %{time_total}s\n" \
        -x http://localhost:3180 \
        http://192.168.1.3:7070

    <h1>Hello, World!</h1>
    Connected IP: ::1
    Total time: 0.313161s
    ```

## Run Stealh Mode in A Container

!!! warning

    Stealth mode gives the opportunity to intercept traffic without having to
    explicitely set the proxy on the client. It relies on eBPF and therefore
    requires a lot of provileges which likely you would not have in a production
    environment.

-   [X] Pull the <span class="f">fault</span> image

    ```bash
    docker pull ghcr.io/rebound-how/fault:0.6.0-stealth
    ```

    !!! abstract

        We do not provide a container image with a `latest` tag for the
        {==stealth==} mode. You must provide a specific versionned tag. The one
        used in this documentation may be outdated, please check the
        [registry](https://github.com/rebound-how/rebound/pkgs/container/fault)
        for the newest version.

-   [X] Run <span class="f">fault</span> with a latency fault

    ```bash
    docker run \
        -p 3180:3180 \  # (1)!
        --rm \  # (2)!
        -it \  # (3)!
        --pid=host \ # (4)!
        -v /sys/fs/cgroup/:/sys/fs/cgroup/:ro \ # (5)!
        --cap-add=SYS_ADMIN \ # (6)!
        --cap-add=BPF \ # (7)!
        --cap-add=NET_ADMIN \ # (8)!
        ghcr.io/rebound-how/fault:0.6.0-stealth \  # (9)!
            run \
            --stealth \  # (10)!
            --capture-process curl \  # (11)!
            --proxy-address 0.0.0.0:3180  \  # (12)!
            --with-latency --latency-mean 300
    ```

    1. Expose the proxy port if you need to access it from the host
    2. Release the system resources once the container finishes
    3. Give the process a terminal
    4. Share the host process namespace to access the client's process
    5. Give access to the host's kernel resources for fault eBPF programs to attach to
    6. Give too much power to the container but unfortunately we cannot reduce the scope so we need it
    7. Specific BPF priviledges
    8. fault needs quite a bit of access to networking to do its job
    9. fault does not expose a `latest` tag for its eBPF-ready images. You must use a specific versionned tag.
    10. Enable stealth mode and loads eBPF programs
    11. Let's capture traffic coming from `curl` commands
    12. The default behavior is to bind the proxy to the loopback which would prevent the proxy from being reached. Bind to all public interfaces with `0.0.0.0`

-   [X] Run the fault demo using the same image

    ```bash
    docker run \
        -p 7070:7070 \  # (1)!
        rebound/fault \
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
    proxy by omitting setting `-x http://localhost:3180`
