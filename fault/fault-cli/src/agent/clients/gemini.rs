use anyhow::Result;
use swiftide::integrations::{self};
use swiftide_core::LanguageModelWithBackOff;

pub fn get_client(
    prompt_model: &str,
    embed_model: &str,
) -> Result<LanguageModelWithBackOff<integrations::gemini::Gemini>> {
    tracing::debug!(
        "Creating Gemini client with prompt model {} and embed model {}",
        prompt_model,
        embed_model
    );
    let gemini_client = integrations::gemini::Gemini::builder()
        // We can't handle Gemini embedding model yet
        //.default_embed_model(embed_model)
        .default_prompt_model(prompt_model)
        .build()?;

    let llm = LanguageModelWithBackOff::new(gemini_client, Default::default());

    Ok(llm)
}
