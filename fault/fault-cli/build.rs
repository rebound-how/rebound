#[cfg(all(target_os = "linux", feature = "stealth-auto-build"))]
use anyhow::anyhow;
#[cfg(all(target_os = "linux", feature = "stealth-auto-build"))]
use aya_build::cargo_metadata;

fn main() -> anyhow::Result<()> {
    tonic_build::configure()
        .build_server(true)
        .build_client(true)
        .compile_protos(
            &["src/plugin/rpc/protos/plugin.proto"],
            &["src/plugin/rpc"],
        )?;

    // Only build the eBPF package if we're on Linux.
    #[cfg(all(target_os = "linux", feature = "stealth-auto-build"))]
    {
        let cargo_metadata::Metadata { packages, .. } =
            cargo_metadata::MetadataCommand::new().no_deps().exec()?;

        let ebpf_package = packages
            .into_iter()
            .find(|cargo_metadata::Package { name, .. }| {
                name == "fault-ebpf-programs"
            })
            .ok_or_else(|| anyhow!("fault-ebpf-programs package not found"))?;
        let _ = aya_build::build_ebpf([ebpf_package]);
    }

    Ok(())
}
