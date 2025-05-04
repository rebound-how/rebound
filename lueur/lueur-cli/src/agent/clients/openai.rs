use anyhow::Result;
use swiftide::integrations::{self};
use swiftide_core::LanguageModelWithBackOff;

pub fn get_client()
-> Result<LanguageModelWithBackOff<integrations::openai::OpenAI>> {
    let openai_client = integrations::openai::OpenAI::builder()
        .default_embed_model("text-embedding-3-small")
        .default_prompt_model("o4-mini")
        .build()?;

    let llm = LanguageModelWithBackOff::new(openai_client, Default::default());

    Ok(llm)
}
