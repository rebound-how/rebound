use anyhow::Result;
use rmcp::ServiceExt;
use rmcp::transport::stdio;

use crate::agent::clients::SupportedLLMClient;

pub(crate) mod code;
pub(crate) mod tools;

pub async fn run(
    llm_type: SupportedLLMClient,
    prompt_model: &str,
    embed_model: &str,
    embed_model_dim: u64,
) -> Result<()> {
    let fault_agent: tools::FaultMCP = tools::FaultMCP::new(
        llm_type,
        prompt_model,
        embed_model,
        embed_model_dim,
    );
    let service = fault_agent.serve(stdio()).await?;
    match service.waiting().await? {
        rmcp::service::QuitReason::Cancelled => {
            println!("MCP server was cancelled")
        }
        rmcp::service::QuitReason::Closed => println!("MCP server was closed"),
    }

    Ok(())
}
