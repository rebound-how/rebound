use anyhow::Result;
use swiftide::integrations::{self};
use swiftide_core::LanguageModelWithBackOff;

pub fn get_client(
    prompt_model: &str,
    embed_model: &str,
) -> Result<LanguageModelWithBackOff<integrations::openai::OpenAI>> {
    tracing::debug!(
        "Creating OpenAI client with prompt model {} and embed model {}",
        prompt_model,
        embed_model
    );
    let openai_client = integrations::openai::OpenAI::builder()
        .default_embed_model(embed_model)
        .default_prompt_model(prompt_model)
        .build()?;

    let llm = LanguageModelWithBackOff::new(openai_client, Default::default());

    Ok(llm)
}
