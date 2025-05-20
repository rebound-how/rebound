use anyhow::Result;
use swiftide::integrations::{self};
use swiftide::query::query_transformers;
use swiftide_core::LanguageModelWithBackOff;

pub trait Embed {
    fn get_embed(&self) -> Result<query_transformers::Embed>;
}

impl Embed for LanguageModelWithBackOff<integrations::openai::OpenAI> {
    fn get_embed(&self) -> Result<query_transformers::Embed> {
        Ok(query_transformers::Embed::from_client(self.clone()))
    }
}

impl Embed for LanguageModelWithBackOff<integrations::ollama::Ollama> {
    fn get_embed(&self) -> Result<query_transformers::Embed> {
        Ok(query_transformers::Embed::from_client(self.clone()))
    }
}
