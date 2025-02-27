use anyhow::Context as _;
#[cfg(target_os = "linux")]
use anyhow::anyhow;

#[cfg(target_os = "linux")]
use aya_build::cargo_metadata;

fn main() -> anyhow::Result<()> {
    tonic_build::configure()
        .build_server(true)
        .build_client(true)
        .compile_protos(&["src/plugin/rpc/protos/service.proto"], &[
            "src/plugin/rpc",
        ])?;

    // Only build the eBPF package if we're on Linux.
    #[cfg(target_os = "linux")]
    {
        let cargo_metadata::Metadata { packages, .. } =
            cargo_metadata::MetadataCommand::new()
                .no_deps()
                .exec()
                .context("MetadataCommand::exec")?;
    
        let ebpf_package = packages
            .into_iter()
            .find(|cargo_metadata::Package { name, .. }| {
                name == "lueur-ebpf-programs"
            })
            .ok_or_else(|| anyhow!("lueur-ebpf-programs package not found"))?;
       let _ = aya_build::build_ebpf([ebpf_package]);
    }

    Ok(())
}
