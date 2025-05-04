use anyhow::Result;
use swiftide::integrations::{self};
use swiftide_core::LanguageModelWithBackOff;

pub fn get_client()
-> Result<LanguageModelWithBackOff<integrations::open_router::OpenRouter>> {
    let or_client = integrations::open_router::OpenRouter::builder()
        .default_prompt_model("anthropic/claude-3.7-sonnet:thinking")
        .build()?;

    let llm = LanguageModelWithBackOff::new(or_client, Default::default());

    Ok(llm)
}
