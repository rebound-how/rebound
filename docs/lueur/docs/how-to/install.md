# Installing lueur

lueur is a designed to be easily installed on major systems such as Linux,
macOS and Windows. We provide a variety of approaches to install lueur depending
on your environment.

## Download the lueur binary

The most direct route is to download the lueur binary on your machine.

-   [X] Download lueur

    You can download the appropriate {==lueur-cli==} binary for your platform
    from [here](https://github.com/rebound-how/rebound/releases).

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

-   [X] Download lueur with ebpf support

    Instead, of `lueur-cli`, you will need to download and run `lueur-cli-ebpf`
    which comes with the appropriate stealth mode enabled.

    You can download {==lueur-cli-ebpf==}
    [here](https://github.com/lueurdev/lueur/releases/latest).

-   [X] Turn the binary into an executable

    On Linux and macOS you will need to make sure the binary gets the
    executable permission flipped on with:

    ```bash
    chmod a+x lueur
    ```

-   [X] Download lueur's ebpf programs

    You can download {==lueur-ebpf-programs==} from
    [here](https://github.com/lueurdev/lueur/releases/latest).

-   [X] Copy them in their default location

    Move the `lueur-ebpf` binary to `$HOME/.local/bin`

    ```bash
    mv lueur-ebpf $HOME/.local/bin
    ```

-   [X] Give privileges to `lueur` to load and attach these ebpf programs

    eBPF is powerful Linux kernel level feature which requires elevated
    privileges to be used. While you can always run `lueur` with `sudo`, it
    might be better to set privileges more specifically to the executable:

    ```bash
    sudo setcap cap_sys_admin,cap_bpf,cap_net_admin+ep `$HOME/.local/bin/lueur`
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

-   [X] Install the `lueur` executable with {==stealth==} mode enabled

    In this case, you need to enable the
    [stealth](./proxy/stealth/configure-stealth-mode.md) feature. when
    installing the `lueur` executable.

    ```bash
    cargo +nightly install lueur --features stealth
    ```

-   [X] Install the `ebpf` binaries on Linux

    ```bash
    cargo +nightly install lueur-ebpf-programs --target=bpfel-unknown-none -Z build-std=core
    ```

-   [X] Give privileges to `lueur` to load and attach these ebpf programs

    eBPF is powerful Linux kernel level feature which requires elevated
    privileges to be used. While you can always run `lueur` with `sudo`, it
    might be better to set privileges more specifically to the executable:

    ```bash
    sudo setcap cap_sys_admin,cap_bpf,cap_net_admin+ep `$HOME/.cargo/bin/lueur`
    ```
