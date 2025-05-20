use anyhow::Result;
use swiftide::integrations::{self};
use swiftide_core::LanguageModelWithBackOff;

// embed "Losspost/stella_en_1.5b_v5"
// prompt "JollyLlama/GLM-4-32B-0414-Q4_K_M"
pub fn get_client(
    prompt_model: &str,
    embed_model: &str,
) -> Result<LanguageModelWithBackOff<integrations::ollama::Ollama>> {
    tracing::debug!(
        "Creating Ollama client with prompt model {} and embed model {}",
        prompt_model,
        embed_model
    );
    let ollama_client = integrations::ollama::Ollama::builder()
        .default_embed_model(embed_model)
        .default_prompt_model(prompt_model)
        .build()?;

    let llm = LanguageModelWithBackOff::new(ollama_client, Default::default());

    Ok(llm)
}
