# Getting Started with <span class="f">fault</span>

Welcome to <span class="f">fault</span>! Your new ally in exploring and understanding the impact of
these petty network issues on your application.
In this brief tutorial, we’ll help you get up and running with <span class="f">fault</span> so that you
can start experimenting with network faults and latency right from your own
environment.

By the end of this tutorial, you’ll have:

- Installed <span class="f">fault</span> on your machine.
- Started a local proxy to simulate network conditions.
- Started a local demo application for learning purpose
- Made your first request through the proxy, observing how latency affects the
  application.

Let’s get started!

## Prerequisites

Before diving in, make sure you have the following:

- **A supported operating system:** fault runs smoothly on most modern Linux,
  macOS, and Windows systems.

!!! note

    Enabled features may vary on each platform, you may look at the
    [features matrix](../how-to/install.md#features-matrix)
    to understand which are available based on your system. For the
    purpose of this tutorial, all platforms are good to go!

## Step 1: Installation

If you haven’t installed <span class="f">fault</span> yet, please follow the
[installation guide](../how-to/install.md).

## Step 2: Starting the Local Proxy

<span class="f">fault</span> operates by running a local proxy server. You can route your application’s
traffic through it to simulate network faults. Let’s start a simple latency
scenario:

```bash
fault run --upstream http://localhost:7070 --with-latency --latency-mean 300
```

This command launches the <span class="f">fault</span> proxy on a local port
(by default, `127.0.0.1:3180`) and injects an average of `300ms` latency into
outgoing requests. You can adjust the `--latency-mean` value to experiment with
different latencies.

The `--upstream http://localhost:7070` argument tells fault to only process
traffic from and to this host.

!!! failure

    Note, if you see an error with a mesage such as
    `Os { code: 98, kind: AddrInUse, message: "Address already in use" }`, it is
    a signe that another process is listening on the same address.

!!! tip
    Always remember to set the right upstream server address that matches the
    endpoints you are exploring. You can set many `--upstream` arguments.

    Any traffic received by fault that does not match any of these
    upstream addresses will go through the proxy unaltered.

Once started, the proxy should issue the following message:

<img srcset="/assets/images/run-default.svg" src="/assets/images/run-default.webp">

Notice how the output tells you the address of the proxy server to use from
your clients.

You are now ==ready to roll!==

## Step 3: Starting a demo application

For the purpose of this tutorial, we will use a demo application built-in
into <span class="f">fault</span>.

Start the demo application in a different terminal:

```bash
fault demo run
```

This will start an application and listen for HTTP requests on
`http://localhost:7070`.

This will output the following prelude:

<img srcset="/assets/images/demo-default.svg" src="/assets/images/demo-default.webp">


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
curl -I -o /dev/null -s \
  -w "Connected IP: %{remote_ip}:%{remote_port}\nTotal time: %{time_total}s\n" \
  http://localhost:7070
```

This should display something such as:

```text
Connected IP: 127.0.0.1:7070
Total time: 0.000239s
```

The time is displayed in seconds. Here the response took `239µs`.

Let's now move to the next stage, inducing latency impacting the client's
point of view of the time taken to receive a response from the demo application.

## Step 4: Configuring Your Application to Use the Proxy

Now that <span class="f">fault</span>'s running, configure your application's
HTTP requests to pass through the proxy.

For example, if you're using `curl`, you might do:

```bash hl_lines="3"
curl -I -o /dev/null -s \
  -w "Connected IP: %{remote_ip}:%{remote_port}\nTotal time: %{time_total}s\n" \
  -x http://127.0.0.1:3180 \
  http://localhost:7070
```

With `-x http://127.0.0.1:3180` set, all requests made via `curl` will flow
through fault, experiencing the specified latency. By observing your
application’s behavior (whether it’s a command-line tool, a local service, or
a browser hitting a test endpoint), you’ll gain first-hand insight into how
network slowdowns affect it.

!!! tip
    Most of the time, you can set either the `HTTP_PROXY` or `HTTPS_PROXY`
    environment variables to let your client know it needs to go through
    a proxy: `export HTTP_PROXY=http://127.0.0.1:3180`.

Once you have executed that command, you should see a much higher response
time:

```json
Connected IP: 127.0.0.1:3180
Total time: 0.333350s
```

We are now above the `300ms` mark as per the configuration of our proxy.

Fantastic, you have now succeeded in altering the perception
your clients would have from your using your application. The only question
remaining is whether or not this is a level that is acceptable by the
organisation.

## Step 5: Observing the Effects

Trigger a few requests from your application. Notice how responses now arrive
slightly delayed. This delay simulates real-world network conditions.

- If your application times out or behaves strangely under these conditions,
  you’ve just uncovered a resilience gap.
- If it gracefully handles delayed responses, congratulations! Your software
  is a step closer to being truly reliable.

## Next Steps

You’ve successfully set up <span class="f">fault</span>, run your first latency
scenario, and routed traffic through it. What’s next?

- **Try different latency values or other fault injection parameters** to get
  a feel for how your application responds to varied conditions.
- **Explore our [Scenario Tutorial](./real-impact-use-case.md)** to learn how to
  simulate scenarios using files and generate detailed reports.
- **Dive into [How-To Guides](../../how-to/)** to integrate
- <span class="f">fault</span> deeper into your workflow, from automated
- testing to continuous integration.

With this initial setup under your belt, you’re well on your way to embracing
a culture of resilience in your everyday development tasks. Happy experimenting!
