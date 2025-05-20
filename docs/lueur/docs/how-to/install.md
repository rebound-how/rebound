# Installing the **fault** cli

fault is a designed to be easily installed on major systems such as Linux,
macOS and Windows. We provide a variety of approaches to install fault depending
on your environment.

## Features Matrix

fault disables some of its features depending on the platform. Below is a
summary of the capabilities per target.

| Platform (OS) / Feature | Proxy | Scenario | Stealth (eBPF) | AI Agent |
|-------------------------|:-----:|:---------------:|:------------------:|:-------------:|
| Linux shared library    |  :white_check_mark:    | :white_check_mark:               | :white_check_mark:             | :white_check_mark:        |
| Linux static (musl)    |  :white_check_mark:    | :white_check_mark:               | :white_check_mark:             | :no_entry:        |
| MacOSX     |  :white_check_mark:    | :white_check_mark:              | :no_entry: (2)            | :white_check_mark:        |
| Windows     |  :white_check_mark:    | :white_check_mark:               | :no_entry: (2)           | :no_entry: (3)       |

1. fault comes with binaries with and without eBPF support for the Linux
   platform.
2. Stealth mode relies on the Linux kernel technology called eBPF and therefore
   is disabled elsewhere.
3. AI Agent relies on the [swiftide](https://swiftide.rs/) rust framework which
   [doesn't support Windows](https://github.com/bosun-ai/swiftide/issues/299).
   However, the agent runs fine on "Linux on Windows" via
   [WSL](https://learn.microsoft.com/en-us/windows/wsl/install).
4. fault only supports 64 bits architectures: x86 and ARM.

When a feature is disabled, it won't appear in the CLI arguments.

## Download the fault binary

The most direct route is to download the fault binary on your machine.

-   [X] Download fault

    You can download the appropriate {==fault-cli==} binary for your platform
    from [here](https://github.com/rebound-how/rebound/releases).

-   [X] Ensure `fault` can be found in your `PATH`

    === "Linux, macOS, Windows Bash"

        ```bash
        export PATH=$PATH:`pwd`
        ```

    === "Windows Powershell"

        ```console
        $env:Path += ';C:\directoy\where\fault\lives' 
        ```


-   [X] Turn the binary into an executable

    On Linux and macOS you will need to make sure the binary gets the
    executable permission flipped on with:

    ```bash
    chmod a+x fault
    ```

### Stealth Feature

fault [stealth mode](../how-to/proxy/stealth/configure-stealth-mode.md)
requires additional dependencies only available on Linux. Follow
these instructions only if you intend on using the stealth feature. Otherwise,
you may skip this section.

-   [X] Download fault with ebpf support

    Instead, of `fault-cli`, you will need to download and run `fault-cli-ebpf`
    which comes with the appropriate stealth mode enabled.

    You can download {==fault-cli-ebpf==}
    [here](https://github.com/faultdev/fault/releases/latest).

-   [X] Turn the binary into an executable

    On Linux and macOS you will need to make sure the binary gets the
    executable permission flipped on with:

    ```bash
    chmod a+x fault
    ```

-   [X] Download fault's ebpf programs

    You can download {==fault-ebpf-programs==} from
    [here](https://github.com/faultdev/fault/releases/latest).

-   [X] Copy them in their default location

    Move the `fault-ebpf` binary to `$HOME/.local/bin`

    ```bash
    mv fault-ebpf $HOME/.local/bin
    ```

-   [X] Give privileges to `fault` to load and attach these ebpf programs

    eBPF is powerful Linux kernel level feature which requires elevated
    privileges to be used. While you can always run `fault` with `sudo`, it
    might be better to set privileges more specifically to the executable:

    ```bash
    sudo setcap cap_sys_admin,cap_bpf,cap_net_admin+ep `$HOME/.local/bin/fault`
    ```

## Install using `cargo`

fault is a [rust](https://www.rust-lang.org/) application. It can be installed
using [cargo](https://github.com/rust-lang/cargo) which will recompile it on the
machine.

-   [X] Requirements

    fault expects rust 1.85+ and the {==nightly==}
    [channel](https://rust-lang.github.io/rustup/concepts/channels.html).

    ```bash
    rustup toolchain install nightly
    ```

-   [X] Install the `fault` executable

    ```bash
    cargo +nightly install fault
    ```

### AI Agent Feature

!!! info

    fault AI Agent is not supported on Windows.

-   [X] Install the `fault` executable with {==agent==} feature enabled

    ```bash
    cargo +nightly install fault --features agent
    ```

### Stealth Feature

!!! info

    fault AI Agent is only available on Linux.

-   [X] Install the `fault` executable with {==stealth==} feature enabled

    In this case, you need to enable the
    [stealth](./proxy/stealth/configure-stealth-mode.md) feature. when
    installing the `fault` executable.

    ```bash
    cargo +nightly install fault --features stealth
    ```

-   [X] Install the `ebpf` binaries on Linux

    ```bash
    cargo +nightly install fault-ebpf-programs --target=bpfel-unknown-none -Z build-std=core
    ```

-   [X] Give privileges to `fault` to load and attach these ebpf programs

    eBPF is powerful Linux kernel level feature which requires elevated
    privileges to be used. While you can always run `fault` with `sudo`, it
    might be better to set privileges more specifically to the executable:

    ```bash
    sudo setcap cap_sys_admin,cap_bpf,cap_net_admin+ep `$HOME/.cargo/bin/fault`
    ```
