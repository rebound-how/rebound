use anyhow::Result;
use swiftide::integrations::fastembed::FastEmbed;
use swiftide::integrations::{self};
use swiftide_core::LanguageModelWithBackOff;

pub trait Embed {
    fn get_embed(
        &self,
    ) -> Result<swiftide_indexing::transformers::embed::Embed>;
}

impl Embed for LanguageModelWithBackOff<integrations::open_router::OpenRouter> {
    fn get_embed(
        &self,
    ) -> Result<swiftide_indexing::transformers::embed::Embed> {
        Ok(swiftide_indexing::transformers::embed::Embed::new(
            FastEmbed::builder().batch_size(10).build()?,
        ))
    }
}

impl Embed for LanguageModelWithBackOff<integrations::openai::OpenAI> {
    fn get_embed(
        &self,
    ) -> Result<swiftide_indexing::transformers::embed::Embed> {
        Ok(swiftide_indexing::transformers::embed::Embed::new(self.clone())
            .with_batch_size(10))
    }
}

impl Embed for LanguageModelWithBackOff<integrations::ollama::Ollama> {
    fn get_embed(
        &self,
    ) -> Result<swiftide_indexing::transformers::embed::Embed> {
        Ok(swiftide_indexing::transformers::embed::Embed::new(self.clone())
            .with_batch_size(10))
    }
}
