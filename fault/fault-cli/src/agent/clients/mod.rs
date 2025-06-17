use std::sync::Arc;

use anyhow::Result;
use serde::Deserialize;
use serde::Serialize;
use swiftide::integrations;
use swiftide_core::ChatCompletion;
use swiftide_core::DynClone;
use swiftide_core::EmbeddingModel;
use swiftide_core::LanguageModelWithBackOff;
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

impl Default for SupportedLLMClient {
    fn default() -> Self {
        SupportedLLMClient::OpenAI
    }
}

pub trait LLM:
    ChatCompletion
    + SimplePrompt
    + EmbeddingModel
    + Send
    + Sync
    + std::fmt::Debug
    + DynClone
{
}

impl<T> LLM for T where
    T: ChatCompletion
        + SimplePrompt
        + EmbeddingModel
        + Send
        + Sync
        + std::fmt::Debug
        + DynClone
{
}

pub fn get_client(
    llm: SupportedLLMClient,
    prompt_model: &str,
    embed_model: &str,
) -> Result<Arc<dyn LLM>> {
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

pub fn get_llm_client(
    llm: SupportedLLMClient,
    prompt_model: &str,
    embed_model: &str,
) -> Result<Box<dyn ChatCompletion>> {
    match llm {
        SupportedLLMClient::OpenAI => {
            Ok(Box::new(openai::get_client(prompt_model, embed_model)?))
        }
        SupportedLLMClient::OpenRouter => {
            Ok(Box::new(openrouter::get_client(prompt_model, embed_model)?))
        }
        SupportedLLMClient::Ollama => {
            Ok(Box::new(ollama::get_client(prompt_model, embed_model)?))
        }
    }
}
