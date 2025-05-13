use std::sync::Arc;

use anyhow::Result;
use serde::Deserialize;
use serde::Serialize;
use swiftide_core::SimplePrompt;

pub(crate) mod ollama;
pub(crate) mod openai;
pub(crate) mod openrouter;

#[derive(
    clap::ValueEnum, Clone, Copy, Debug, Serialize, Deserialize, Eq, PartialEq,
)]
#[serde(rename_all = "lowercase")]
pub enum SupportedLLMClient {
    OpenAI,
    OpenRouter,
    Ollama,
}

pub fn get_client(
    llm: SupportedLLMClient,
    prompt_model: &str,
    embed_model: &str,
) -> Result<Arc<dyn SimplePrompt>> {
    match llm {
        SupportedLLMClient::OpenAI => {
            Ok(Arc::new(openai::get_client(prompt_model, embed_model)?))
        }
        SupportedLLMClient::OpenRouter => {
            Ok(Arc::new(openrouter::get_client(prompt_model, embed_model)?))
        }
        SupportedLLMClient::Ollama => {
            Ok(Arc::new(ollama::get_client(prompt_model, embed_model)?))
        }
    }
}
