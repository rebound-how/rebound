use std::str::FromStr;
use std::sync::Arc;

use anyhow::Result;
use async_trait::async_trait;
use duckdb;
use serde_json::json;
use similar_string::find_best_similarity;
use swiftide::indexing;
use swiftide::indexing::EmbeddedField;
use swiftide::indexing::loaders::FileLoader;
use swiftide::indexing::transformers::ChunkCode;
use swiftide::indexing::transformers::MetadataQACode;
use swiftide::indexing::transformers::SparseEmbed;
use swiftide::indexing::transformers::metadata_refs_defs_code::NAME_DEFINITIONS;
use swiftide::indexing::transformers::metadata_refs_defs_code::NAME_REFERENCES;
use swiftide::integrations::duckdb::Duckdb;
use swiftide::integrations::fastembed::FastEmbed;
use swiftide::integrations::qdrant::Qdrant;
use swiftide::integrations::treesitter::SupportedLanguages;
use swiftide::integrations::{self};
use swiftide::query::query_transformers;
use swiftide_core::EmbeddingModel;
use swiftide_core::SimplePrompt;
use swiftide_core::Transformer;
use swiftide_core::WithBatchIndexingDefaults;
use swiftide_core::WithIndexingDefaults;
use swiftide_indexing::transformers::Embed;

use super::CODE_COLLECTION;
use super::clients::SupportedLLMClient;
use super::meta::Meta;
use crate::agent::clients::get_client;

pub async fn index(
    source_dir: &str,
    source_lang: &str,
    metas: &Vec<Meta>,
    cache_db_path: &str,
    client_type: SupportedLLMClient,
    prompt_model: &str,
    embed_model: &str,
    embed_model_dim: u64,
) -> Result<()> {
    let lang = SupportedLanguages::from_str(source_lang)?;

    let llm = get_client(client_type, prompt_model, embed_model)?;

    let sp: Arc<dyn SimplePrompt> = llm.clone();
    let em: Arc<dyn EmbeddingModel> = llm.clone();

    let duckdb_client = Duckdb::builder()
        .connection(duckdb::Connection::open(cache_db_path).unwrap())
        .build()
        .unwrap();

    let fastembed_sparse = FastEmbed::try_default_sparse()?;
    //let fastembed = FastEmbed::try_default()?;

    let qdrant = Qdrant::builder()
        .batch_size(64)
        .vector_size(embed_model_dim)
        .with_vector(EmbeddedField::Combined)
        .with_sparse_vector(EmbeddedField::Combined)
        .collection_name(CODE_COLLECTION)
        .build()?;

    let chunk_size = 2048;
    let opids = metas.iter().map(|m| m.opid.clone()).collect::<Vec<String>>();
    let exts = lang.file_extensions();

    indexing::Pipeline::from_loader(
        FileLoader::new(source_dir).with_extensions(exts),
    )
    .filter_cached(duckdb_client)
    .then(indexing::transformers::OutlineCodeTreeSitter::try_for_language(
        source_lang,
        Some(chunk_size),
    )?)
    .then(MetadataQACode::new(sp.clone()))
    .then_chunk(ChunkCode::try_for_language_and_chunk_size(
        source_lang,
        10..chunk_size,
    )?)
    .then(indexing::transformers::CompressCodeOutline::new(sp.clone()))
    .then(indexing::transformers::MetadataRefsDefsCode::try_from_language(
        source_lang,
    )?)
    .then(TagOpId::new(opids))
    .then_in_batch(Embed::new(em.clone()).with_batch_size(10))
    .then_in_batch(SparseEmbed::new(fastembed_sparse.clone()))
    .then_store_with(qdrant.clone())
    .run()
    .await?;

    Ok(())
}

#[derive(Clone)]
pub struct TagOpId {
    pub opids: Vec<String>,
    concurrency: Option<usize>,
}

impl TagOpId {
    pub fn new(opids: Vec<String>) -> Self {
        Self { opids, concurrency: None }
    }

    #[must_use]
    pub fn with_concurrency(mut self, concurrency: usize) -> Self {
        self.concurrency = Some(concurrency);
        self
    }
}

impl WithBatchIndexingDefaults for TagOpId {}
impl WithIndexingDefaults for TagOpId {}

#[async_trait]
impl Transformer for TagOpId {
    async fn transform_node(
        &self,
        mut node: indexing::Node,
    ) -> Result<indexing::Node> {
        /*if let Some(outline) = node.metadata.get("Outline") {
            println!("{:?}", outline);
        }*/
        if let Some(v) = node.metadata.get(NAME_DEFINITIONS) {
            match v.clone() {
                tera::Value::String(s) => {
                    let defs: Vec<&str> = s.split(",").collect();
                    for opid in &self.opids {
                        match find_best_similarity(opid, &defs) {
                            Some((m, score)) => {
                                tracing::debug!(
                                    "Matched {} with {} score {}",
                                    opid,
                                    m,
                                    score
                                );
                                node.metadata.insert(opid, m);
                                node.metadata
                                    .insert("operation_id", json!(opid));
                                break;
                            }
                            None => {}
                        }
                    }
                }
                _ => {}
            };
        }
        /*if let Some(refs) = node.metadata.get(NAME_REFERENCES) {
            println!("{:?}", refs);
        }*/

        tracing::debug!("Node {:?}", node);

        Ok(node)
    }

    fn concurrency(&self) -> Option<usize> {
        self.concurrency
    }
}
