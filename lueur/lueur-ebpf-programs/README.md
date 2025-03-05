# Lueur ebpf program

The ebpf program for lueur is an experimental feature to enable stealth mode
in the lueur proxy.

## Install

To install the programs locally; run the following command:

```bash
cargo +nightly install lueur-ebpf-programs --target=bpfel-unknown-none -Z build-std=core
```
