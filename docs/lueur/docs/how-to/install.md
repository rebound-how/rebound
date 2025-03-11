# Installing lueur

lueur is a designed to be easily installed on major systems such as Linux,
macOS and Windows. We provide a variety of approaches to install lueur depending
on your environment.

## Install the lueur binary

The most direct route is to download the lueur binary on your machine.

-   [X] Download lueur

    You can download the appropriate binary for your platform from
    [here](https://github.com/lueurdev/lueur/releases/latest).

-   [X] Ensure `lueur` can be found in your `PATH`

    === "Linux, macOS, Windows Bash"

        ```bash
        export PATH=$PATH:`pwd`
        ```

    === "Windows Powershell"

        ```console
        $env:Path += ';C:\directoy\where\lueur\lives' 
        ```


-   [X] Turn the binary into an executable

    On Linux and macOS you will need to make sure the binary gets the
    executable permission flipped on with:

    ```bash
    chmod a+x lueur
    ```

### Stealth Dependencies

lueur [stealth mode](../how-to/proxy/stealth/configure-stealth-mode.md)
requires additional dependencies only available on Linux.

-   [X] Download lueur's ebpf programs

    You can download {==lueur-ebpf==} from
    [here](https://github.com/lueurdev/lueur/releases/latest).

-   [X] Copy them in their default location

    Move the `lueur-ebpf` binary to `$HOME/.local/bin`

    ```bash
    mv lueur-ebpf $HOME/.local/bin
    ```

## Install using `cargo`

lueur is a [rust](https://www.rust-lang.org/) application. It can be installed
using [cargo](https://github.com/rust-lang/cargo) which will recompile it on the
machine.

-   [X] Requirements

    lueur expects rust 1.85+ and the {==nightly==}
    [channel](https://rust-lang.github.io/rustup/concepts/channels.html).

    ```bash
    rustup toolchain install nightly
    ```

-   [X] Install the `lueur` executable

    ```bash
    cargo +nightly install lueur
    ```

### Stealth Dependencies

-   [X] Install the `ebpf` binaries on Linux

    In addition, you may also install the {==ebpf programs==} if you are running
    on Linux. This enables 
    [stealth mode](./proxy/stealth/configure-stealth-mode.md).

    ```bash
    cargo +nightly install lueur-ebpf-programs --target=bpfel-unknown-none -Z build-std=core
    ```

## Run as a container

### Standard Mode

lueur is packaged as a Docker image.

-   [X] Pull the Docker image 

    ```bash
    docker pull rebound/lueur:latest
    ```

-   [X] Run the proxy as a container

    ```bash
    docker run --rm -it rebound/lueur run --help
    ```

### Stealth Mode

To run with [stealth mode](./proxy/stealth/configure-stealth-mode.md)
enabled, you need to pull the following image.

-   [X] Pull the Docker image with ebpf enabled

    ```bash
    docker pull rebound/lueur-ebpf:latest
    ```

-   [X] Run the proxy as a container

    ```bash
    docker run --rm -it rebound/lueur \
        run \  # (1)!
        --stealth \  # (2)!
        --network=host \  # (3)!
        --pid=host \  # (4)!
        --capture-process curl \  # (5)!
        -v /sys/fs/cgroup/:/sys/fs/cgroup/:ro  \  # (6)!
        --cap-add=SYS_ADMIN \  # (7)!
        --cap-add=BPF \
        --cap-add=NET_ADMIN
    ```

    1. Run the lueur proxy
    2. Enable lueur {==stealth==} mode and loads the {==ebpf programs==}
    3. Attach to a particular network to view/modify its traffic. This can also be another container's network
    4. Attach to a particular process namespace to access its processes. This can also be another container's network
    5. Tell lueur to focus on traffic coming from a specific process name such as {==curl==}
    6. Share the host's {==cgroup==} resources with the container so the ebpf programs can be attached to them
    7. Give the process required [capabilities for eBPF](https://mdaverde.com/posts/cap-bpf/)

