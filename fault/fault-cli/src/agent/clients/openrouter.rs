use anyhow::Result;
use swiftide::integrations::{self};
use swiftide_core::LanguageModelWithBackOff;

pub fn get_client(
    prompt_model: &str,
    embed_model: &str,
) -> Result<LanguageModelWithBackOff<integrations::open_router::OpenRouter>> {
    tracing::debug!(
        "Creating OpenRouter client with prompt model {} and embed model {}",
        prompt_model,
        embed_model
    );

    let or_client = integrations::open_router::OpenRouter::builder()
        // OpenRouter doesn't have embedding models so this is moot
        //.default_embed_model(embed_model)
        .default_prompt_model(prompt_model)
        .build()?;

    let llm = LanguageModelWithBackOff::new(or_client, Default::default());

    Ok(llm)
}
