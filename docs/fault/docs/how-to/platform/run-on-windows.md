# Run <span class="f">fault</span> on a Microsoft Windows host

This guide will show you how to run <span class="f">fault</span> on a Microsoft Windows host.

## What You'll Achieve

You will learn how to run <span class="f">fault</span> from a PowerShell command line or
via the Windows Subsystem for Linux.

## Run fa<span class="f">fault</span>ult via Windows PowerShell

-   [X] Download <span class="f">fault</span> for Windows

    Download the latest Windows release of <span class="f">fault</span> from the
    [releases](https://github.com/rebound-how/rebound/releases/latest) page.

-   [X] Rename the binary

    Once downloaded, rename the executable to `fault.exe`

-   [X] Add the directory to the `Path`

    You may additionnaly update the `Path` so that <span class="f">fault</span> is found.

    ```console
    $env:Path += ';C:\directoy\where\fault\lives' 
    ```

## Run <span class="f">fault</span> via Windows Subsystem for Linux (WSL)

-   [X] Install a Ubuntu release

    Another approach to run from Windows is to benefit from the Windows
    [Substem for Linux](https://learn.microsoft.com/en-us/windows/wsl/setup/environment),
    which exposes Windows lower level resources in a way that allows Linux to
    run from them directly.

    ```powershell
    wsl --install -d Ubuntu-24.04
    ```

    This will install a base Ubuntu distribution. It will ask you for a
    username and password along the way. Finally, it will log you in to that
    user.


-   [X] Configure the environment

    Install the {==jq==} command:

    ```bash
    sudo apt install -y jq
    ```

    Then, create the target directory where `fault` will be installed:

    ```bash
    mkdir -p .local/bin
    ```

    Add the following to your `.bashrc` file:

    ```bash
    export PATH=$PATH:$HOME/.local/bin
    ```

-   [X] Install <span class="f">fault</span>

    Install <span class="f">fault</span> using our installer script:

    ```bash
    curl -sSL https://fault-project.com/get | bash
    ```
