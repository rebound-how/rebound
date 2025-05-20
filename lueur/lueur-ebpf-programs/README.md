# fault eBPF Programs

The ebpf program for fault is an experimental feature to enable stealth mode
in the fault proxy.

## Install

To install the programs locally; run the following command:

```bash
cargo +nightly install fault-ebpf-programs --target=bpfel-unknown-none -Z build-std=core
```

You will need to install the [fault-cli](https://crates.io/crates/fault-cli)
to use these programs.

Please refer to the
[documentation](https://fault.dev/how-to/proxy/stealth/configure-stealth-mode/)
for more details.
