# Install lueur

lueur strives to get of your way and it starts with a smooth installation.

## Download lueur

lueur is provided as a binary targetting the three major platforms: Linux,
macOS and Windows.

You can download the appropriate binary for your platform from
[here](https://github.com/lueurdev/lueur/releases/latest).

Once you have downloaded the archive, you can uncompress it and make sure
it can be found in your `PATH`.

=== "Linux, macOS, Windows Bash"

    ```bash
    export PATH=$PATH:`pwd`
    ```

=== "Windows Powershell"

    ```console
    $env:Path += ';C:\directoy\where\lueur\lives' 
    ```

!!! tip

    On Linux and macOS you will need to make sure the binary gets the
    executable permission flipped on with:

    ```bash
    chmod a+x lueur
    ```

## Check lueur is ready to roll

Let's verify it all went well by running the following command:

```bash
lueur --help
```

This should output the following:

```
A proxy to test network resilience by injecting various faults.

Usage: lueur [OPTIONS] <COMMAND>

Commands:
  run       Apply a network fault
  scenario  Execute a predefined scenario
  demo      Run a simple demo server for learning purpose
  help      Print this message or the help of the given subcommand(s)

Options:
      --log-file <LOG_FILE>    Path to the log file. Disabled by default
      --log-stdout             Stdout logging enabled
      --log-level <LOG_LEVEL>  Log level [default: info,tower_http=debug]
  -h, --help                   Print help
  -V, --version                Print version
```

## Troubleshooting

If you receive a message such as ̀`lueur: No such file or directory`, it likely
means you have not put the directory containing the `lueur` binary in your 
`PATH`, or you may need to restart your session for the changes to take
effect.

## Next Steps

You’ve successfully downloaded and made lueure. What’s next?

- **Explore our [Getting Started Tutorial](../getting-started/)** to learn how to first use lueur.
- **Dive into [How-To Guides](../../how-to/)** to integrate lueur deeper into
  your workflow, from automated testing to continuous integration.
