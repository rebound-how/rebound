use std::error::Error;

use anyhow::Result;
use duckdb;
use swiftide::indexing;
use swiftide::indexing::LanguageModelWithBackOff;
use swiftide::indexing::loaders::FileLoader;
use swiftide::indexing::transformers::ChunkCode;
use swiftide::indexing::transformers::Embed;
use swiftide::indexing::transformers::MetadataQACode;
use swiftide::integrations::duckdb::Duckdb;
use swiftide::integrations::qdrant::Qdrant;
use swiftide::integrations::{self};

use crate::errors::SuggestionError;

pub async fn index(
    source_dir: &str,
    source_lang: &str,
    cache_db_path: &str,
) -> Result<()> {
    let openai_client = integrations::openai::OpenAI::builder()
        .default_embed_model("text-embedding-3-small")
        .default_prompt_model("gpt-4o-mini")
        .build()?;

    let openai_client =
        LanguageModelWithBackOff::new(openai_client, Default::default());

    let duckdb_client = Duckdb::builder()
        .connection(duckdb::Connection::open(cache_db_path).unwrap())
        .build()
        .unwrap();

    let chunk_size = 2048;

    indexing::Pipeline::from_loader(
        FileLoader::new(source_dir).with_extensions(&["py"]),
    )
    .filter_cached(duckdb_client)
    .then(indexing::transformers::OutlineCodeTreeSitter::try_for_language(
        source_lang,
        Some(chunk_size),
    )?)
    .then(MetadataQACode::new(openai_client.clone()))
    .then_chunk(ChunkCode::try_for_language_and_chunk_size(
        source_lang,
        10..chunk_size,
    )?)
    //.then(TagOpId { ids: op_ids })
    .then(indexing::transformers::CompressCodeOutline::new(
        openai_client.clone(),
    ))
    .then_in_batch(Embed::new(openai_client.clone()).with_batch_size(10))
    .then_store_with(
        Qdrant::builder()
            .batch_size(64)
            .vector_size(1536)
            .collection_name("swiftide-examples")
            .build()?,
    )
    .run()
    .await?;
    Ok(())
}
