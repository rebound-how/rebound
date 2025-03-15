# Lueur eBPF Programs

The ebpf program for lueur is an experimental feature to enable stealth mode
in the lueur proxy.

## Install

To install the programs locally; run the following command:

```bash
cargo +nightly install lueur-ebpf-programs --target=bpfel-unknown-none -Z build-std=core
```

You will need to install the [lueur-cli](https://crates.io/crates/lueur-cli)
to use these programs.

Please refer to the
[documentation](https://lueur.dev/how-to/proxy/stealth/configure-stealth-mode/)
for more details.
