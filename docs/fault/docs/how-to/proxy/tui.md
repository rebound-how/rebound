# Configure the TUI

fault is a CLI. But it doesn't mean it shouldn't display the information with
a beautiful TUI (Terminal User Interface).

## Default TUI

The default TUI mode shows a summary of the configuration you set for the proxy
and a summary of the events it sees:

<img src="/assets/images/default-tui.png">

A more comprehensive example:

<img src="/assets/images/comprehensive-tui.png">


## Disable the TUI

Sometimes the verbosity of fault is not acceptable or useful. In that case,
you can entirely hide it with the `--no-ui` flag.

## Tailing

The default behavior of the UI is to show a summary of events (traffic and
fault injection) in a very concise manner.

You may switch to a more verbose output by tailing the events using the
`--tail` flag.

<img src="/assets/images/tail-tui.png">
