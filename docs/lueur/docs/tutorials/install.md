# Install lueur

lueur strives to get of your way and it starts with a smooth installation.

## Download lueur

lueur is provided as a binary targetting the three major platforms: Linux,
macOS and Windows.

You may try the installation script:

```bash
curl -sSL https://lueur.dev/get | bash
```

Alternatively, explore our other [installation options](../how-to/install.md#download-the-lueur-binary).

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
  run       Resilience proxy
  scenario  Resilience automation
  agent     Resilience Agentic Buddy
  demo      Run a simple demo server for learning purpose
  help      Print this message or the help of the given subcommand(s)

Options:
  -h, --help     Print help
  -V, --version  Print version

Logging Options:
      --log-file <LOG_FILE>    Path to the log file. Disabled by default [env: LUEUR_LOG_FILE=]
      --log-stdout             Stdout logging enabled [env: LUEUR_WITH_STDOUT_LOGGING=]
      --log-level <LOG_LEVEL>  Log level [env: LUEUR_LOG_LEVEL=] [default: info]

Observability Options:
      --with-otel  Enable Open Telemetry tracing and metrics. [env: LUEUR_WITH_OTEL=]

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
