use std::str::FromStr;
use std::sync::Arc;

use anyhow::Result;
use swiftide::indexing;
use swiftide::indexing::EmbeddedField;
use swiftide::indexing::transformers::ChunkCode;
use swiftide::indexing::transformers::MetadataQACode;
use swiftide::integrations::duckdb::Duckdb;
use swiftide::integrations::fastembed::FastEmbed;
use swiftide::integrations::qdrant::Qdrant;
use swiftide::integrations::treesitter::SupportedLanguages;
use swiftide::query::{self};
use swiftide_core::EmbeddingModel;
use swiftide_core::SimplePrompt;
use swiftide_indexing::loaders::FileLoader;
use swiftide_indexing::transformers::SparseEmbed;
use swiftide_indexing::transformers::embed::Embed;
use tree_sitter::Language;
use tree_sitter::Parser;
use tree_sitter::Query;
use tree_sitter::QueryCursor;
use tree_sitter::StreamingIteratorMut;

use crate::agent::CODE_COLLECTION;
use crate::agent::clients::SupportedLLMClient;
use crate::agent::clients::get_client;

pub struct SnippetComponents {
    pub full: String,
    pub body: String,
}

fn grammar_for_extension(ext: &str) -> Option<Language> {
    match ext {
        "rs" => Some(tree_sitter_rust::LANGUAGE.into()),
        "py" => Some(tree_sitter_python::LANGUAGE.into()),
        "js" => Some(tree_sitter_javascript::LANGUAGE.into()),
        "go" => Some(tree_sitter_go::LANGUAGE.into()),
        "yaml" => Some(tree_sitter_yaml::LANGUAGE.into()),
        // add more as you need…
        _ => None,
    }
}

pub fn extract_function_snippet(
    src: &str,
    ext: &str,
    func_name: &str,
) -> Option<SnippetComponents> {
    let lang = grammar_for_extension(ext)?;

    let mut parser = Parser::new();
    parser.set_language(&lang).ok()?;
    let tree = parser.parse(src, None)?;
    let root = tree.root_node();

    let query = match ext {
        "rs" => {
            r#"
        (function_item
            name: (identifier) @fn_name
            body: (block) @fn_body
        ) @fn_item
        "#
        }

        // ← updated: this now matches *either* a decorated_definition *or* a
        // plain function_definition
        "py" => {
            r#"
        ; decorated
        (decorated_definition
            (function_definition
                name: (identifier) @fn_name
                body: (block) @fn_body
            )
        ) @fn_item

        ; plain
        (function_definition
            name: (identifier) @fn_name
            body: (block) @fn_body
        ) @fn_item
        "#
        }

        "js" | "ts" => {
            r#"
        (function_declaration
            name: (identifier) @fn_name
            body: (statement_block) @fn_body
        ) @fn_item
        "#
        }

        "go" => {
            r#"
        (function_declaration
            name: (identifier) @fn_name
            function_body: (block) @fn_body
        ) @fn_item
        "#
        }

        _ => return None,
    };

    let query = Query::new(&lang, query).ok()?;
    let mut cursor = QueryCursor::new();
    let mut matches = cursor.matches(&query, root, src.as_bytes());

    while let Some(m) = matches.next_mut() {
        let mut names = m.nodes_for_capture_index(0);
        let mut bodies = m.nodes_for_capture_index(1);
        let mut items = m.nodes_for_capture_index(2);

        if let (Some(name_n), Some(body_n), Some(item_n)) =
            (names.next(), bodies.next(), items.next())
        {
            if name_n.utf8_text(src.as_bytes()).ok()? == func_name {
                let start = item_n.start_byte();
                let end = item_n.end_byte();
                let bstart = body_n.start_byte();
                let bend = body_n.end_byte();

                return Some(SnippetComponents {
                    full: src[start..end].to_string(),
                    body: src[bstart..bend].to_string(),
                });
            }
        }
    }

    None
}

pub fn list_functions(src: &str, ext: &str) -> Option<Vec<String>> {
    let lang = grammar_for_extension(ext)?;

    let mut parser = Parser::new();
    parser.set_language(&lang).ok()?;
    let tree = parser.parse(&src, None)?;
    let root = tree.root_node();

    let query_src = match ext {
        "rs" => {
            r#"(
            (function_item name: (identifier) @fn_name)
        )"#
        }
        "py" => {
            r#"(
            (function_definition name: (identifier) @fn_name)
        )"#
        }
        "js" | "ts" => {
            r#"(
            (function_declaration name: (identifier) @fn_name)
        )"#
        }
        "go" => {
            r#"(
            (function_declaration name: (identifier) @fn_name)
        )"#
        }
        _ => return None,
    };

    let query = Query::new(&lang, query_src).ok()?;
    let mut cursor = QueryCursor::new();
    let mut matches = cursor.matches(&query, root, src.as_bytes());

    let mut names = Vec::new();

    while let Some(m) = matches.next_mut() {
        if let Some(node) = m.nodes_for_capture_index(0).next() {
            if let Ok(name) = node.utf8_text(src.as_bytes()) {
                names.push(name.to_string());
            }
        }
    }

    Some(names)
}

pub async fn index(
    source_dir: &str,
    source_lang: &str,
    cache_db_path: &str,
    client_type: SupportedLLMClient,
    prompt_model: &str,
    embed_model: &str,
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

    let qdrant = Qdrant::builder()
        .batch_size(64)
        .vector_size(1536)
        .with_vector(EmbeddedField::Combined)
        .with_sparse_vector(EmbeddedField::Combined)
        .collection_name(CODE_COLLECTION)
        .build()?;

    let chunk_size = 2048;
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
    .then_in_batch(Embed::new(em.clone()).with_batch_size(10))
    .then_in_batch(SparseEmbed::new(fastembed_sparse.clone()))
    .then_store_with(qdrant.clone())
    .run()
    .await?;

    Ok(())
}
