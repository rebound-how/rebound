use anyhow::Result;
use swiftide::integrations::{self};
use swiftide_core::LanguageModelWithBackOff;

pub fn get_client()
-> Result<LanguageModelWithBackOff<integrations::ollama::Ollama>> {
    let ollama_client = integrations::ollama::Ollama::builder()
        .default_embed_model("Losspost/stella_en_1.5b_v5")
        .default_prompt_model("JollyLlama/GLM-4-32B-0414-Q4_K_M")
        .build()?;

    let llm = LanguageModelWithBackOff::new(ollama_client, Default::default());

    Ok(llm)
}
