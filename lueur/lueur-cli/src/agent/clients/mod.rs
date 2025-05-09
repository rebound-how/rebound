use serde::Deserialize;
use serde::Serialize;

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
