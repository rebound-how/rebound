# Lueur Proxy CLI

lueur is here to help you uncover and address resiliency issues early in your
development cycle. By easily injecting network faults into your application’s
daily workflows, lueur encourages you to shift resiliency concerns to the left,
long before reaching production. The result: more confident engineering teams
and applications that gracefully handle the unexpected.

At its core, lueur acts as a local proxy you can route traffic through, giving
you fine-grained control over conditions like latency, jitter, and faults.
Rather than waiting until late-stage testing or worse, customer reports, you
can quickly see how your application responds when the network isn’t perfect.

**Why lueur?**

- **Speed:** Quickly stand up a local test environment with minimal setup.
- **Simplicity:** Just a few commands let you inject latency or run complex
  scenarios—no steep learning curve required.
- **Extensibility:** Tweak parameters, plug into automated tests, and integrate
  with your existing CI/CD pipelines.
- **Insight:** Generate structured reports that help pinpoint issues and
  identify ways to improve resiliency.

## Install

The lueur proxy is installed as follows:

```bash
cargo +nightly install lueur-cli
```

If you want to enable ebpf support (highly experimental and likely broken):

```bash
cargo +nightly install lueur-cli --features stealth
```

## Run

Once installed, you can start a latency fault inkjection proxy (for instance):

```bash
lueur run --with-latency --latency-mean 300 --latency-direction ingress --upstream localhost:9090
```

This is will inject `300ms` (mean) latency on network coming back from the
host `localhost:9090`.

