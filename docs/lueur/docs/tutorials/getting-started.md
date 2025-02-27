# Getting Started with lueur

Welcome to lueur—your new ally in exploring and understanding the impact of
these petty network issues on your application!
In this brief tutorial, we’ll help you get up and running with lueur so that you
can start experimenting with network faults and latency right from your own
environment.

By the end of this tutorial, you’ll have:

- Installed lueur on your machine.
- Started a local proxy to simulate network conditions.
- Started a local demo application for learning purpose
- Made your first request through the proxy, observing how latency affects the
  application.

Let’s get started!

## Prerequisites

Before diving in, make sure you have the following:

- **A supported operating system:** lueur runs smoothly on most modern Linux,
  macOS, and Windows systems.

## Step 1: Installation

If you haven’t installed lueur yet, here’s a quick way to do it:

1. Head over to the [lueur Releases page](https://github.com/lueurdev/lueur/releases)
   and download the binary for your platform.  
2. Extract the binary and place it in a directory included in your `$PATH`
   (like `/usr/local/bin` on Linux/macOS or in a PATH-enabled directory on
   Windows).

## Step 2: Starting the Local Proxy

lueur operates by running a local proxy server. You can route your application’s
traffic through it to simulate network faults. Let’s start a simple latency
scenario:

```bash
lueur run --upstream http://localhost:7070 latency --mean 300
```

!!! tip "For all latency options, use:"
    ```console
    lueur run latency --help
    ```

This command launches the lueur proxy on a local port
(by default, `127.0.0.1:8080`) and injects an average of `300ms` latency into
outgoing requests. You can adjust the `--mean` value to experiment with
different latencies.

!!! failure

    Note, if you see an error with a mesage such as
    `Os { code: 98, kind: AddrInUse, message: "Address already in use" }`, it is
    a signe that another process is listening on the same address.

The `--upstream http://localhost:7070` argument tells lueur to only process
traffic from and to this host.

!!! tip
    Always remember to set the right upstream server address that matches the
    endpoints you are exploring. You can set many `--upstream` arguments.

    Any traffic received by lueur that does not match any of these
    upstream addresses will go through the proxy unaltered.

Once started, the proxy should issue the following message:

```text
Welcome to lueur — Your Resiliency Exploration Tool!

To get started, route your HTTP/HTTPS requests through:
http://127.0.0.1:8080

As you send requests, lueur will simulate network conditions
so you can see how your application copes.

Ready when you are — go ahead and make some requests!
```

Notice how the output tells you the address of the proxy server to use from
your clients.

You are now ==ready to roll!==

## Step 3: Starting a demo application

For the purpose of this tutorial, we will use a demo application built-in
into lueur.

Start the demo application in a different terminal:

```bash
lueur demo run
```

This will start an application and listen for HTTP requests on
`http://localhost:7070`.

This will output the following prelude:

```text

Welcome to lueur, this demo application is here to let you explore lueur's capabilities.

Here are a few examples:

export HTTP_PROXY=http://localhost:8080
export HTTPS_PROXY=http://localhost:8080

curl -x ${HTTP_PROXY} http://127.0.0.1:7070/
curl -x ${HTTP_PROXY} http://127.0.0.1:7070/ping
curl -x ${HTTP_PROXY} http://127.0.0.1:7070/ping/myself
curl -x ${HTTP_PROXY} --json '{"content": "hello"}' http://127.0.0.1:7070/uppercase


```

The demo describes which endpoints are available and how to call them.

First, you can verify the demo is running correctly with `curl`:

```bash
curl http://localhost:7070
```

which should output:

```html
<h1>Hello, World!</h1>
```

Look at the demo application output and you should see the request was served:

```
GET / 200 6.627µs
```

The given timing `6.627µs` represents the duration of the request/response
processing by the demo application for that particular request.

Let's now enrich the `curl` command above to output the time taken from the
client's perspective:

```bash hl_lines="2"
curl \
  -o /dev/null -s -w '{"total_time": %{time_total}}\n' \
  http://localhost:7070/
```

This should display something such as:

```json
{"total_time": 0.000544}
```

The time is displayed in seconds. Here the response took `544µs`.

Let's now move to the next stage, inducing latency impacting the client's
point of view of the time taken to receive a response from the demo application.

## Step 4: Configuring Your Application to Use the Proxy

Now that lueur’s running, configure your application’s HTTP requests to pass
through the proxy.

For example, if you’re using `curl`, you might do:

```bash hl_lines="2"
curl -o /dev/null -s -w '{"total_time": %{time_total}}\n' \
  -x http://127.0.0.1:8080 \
  http://localhost:7070
```

With `-x http://127.0.0.1:8080` set, all requests made via `curl` will flow
through lueur, experiencing the specified latency. By observing your
application’s behavior (whether it’s a command-line tool, a local service, or
a browser hitting a test endpoint), you’ll gain first-hand insight into how
network slowdowns affect it.

!!! tip
    Most of the time, you can set either the `HTTP_PROXY` or `HTTPS_PROXY`
    environment variables to let your client know it needs to go through
    a proxy: `export HTTP_PROXY=http://127.0.0.1:8080`.

Once you have executed that command, you should see a much higher response
time:

```json
{"total_time": 0.339949}
```

We are now above the `300ms` mark as per the configuration of our proxy.

Fantastic, you have now succeeded in altering the perception
your clients would have from your using your application. The only question
remaining is whether or not this is a level that is acceptable by the
organisation.

## Step 5: Observing the Effects

Trigger a few requests from your application. Notice how responses now arrive
slightly delayed. This delay simulates real-world network conditions—exactly
what lueur is here to help you understand and address.

- If your application times out or behaves strangely under these conditions,
  you’ve just uncovered a resilience gap.
- If it gracefully handles delayed responses, congratulations! Your software
  is a step closer to being truly reliable.

## Next Steps

You’ve successfully set up lueur, run your first latency scenario, and routed
traffic through it. What’s next?

- **Try different latency values or other fault injection parameters** to get
  a feel for how your application responds to varied conditions.
- **Explore our [Tutorials](../) further** to learn how to simulate scenarios
  using `.toml` files and generate detailed reports.
- **Dive into [How-To Guides](../../how-to/)** to integrate lueur deeper into
  your workflow, from automated testing to continuous integration.

With this initial setup under your belt, you’re well on your way to embracing
a culture of resilience in your everyday development tasks. Happy experimenting!
