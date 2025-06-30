use std::fmt;
use std::fs;
use std::path::Path;

use anyhow::Result;
use async_trait::async_trait;
use inquire::Select;
use kanal::AsyncSender;
use qdrant_client::qdrant::Filter;
use swiftide::chat_completion::ToolCall;
use swiftide::chat_completion::ToolOutput;
use swiftide::chat_completion::errors::ToolError;
use swiftide::indexing::EmbeddedField;
use swiftide::integrations::fastembed::FastEmbed;
use swiftide::integrations::qdrant;
use swiftide::integrations::qdrant::Qdrant;
use swiftide::integrations::{self};
use swiftide::query::Query;
use swiftide::query::answers;
use swiftide::query::query_transformers;
use swiftide::query::search_strategies::HybridSearch;
use swiftide::query::states;
use swiftide::query::{self};
use swiftide::tool;
use swiftide_agents::Agent;
use swiftide_core::AgentContext;
use swiftide_core::CommandError;
use swiftide_core::CommandOutput;
use swiftide_core::Retrieve;
use swiftide_core::TransformResponse;
use swiftide_macros::Tool;
use tera::Context;

use super::clients::SupportedLLMClient;
use super::meta::Meta;
use crate::agent::CODE_COLLECTION;
use crate::agent::clients::openai::get_client;
use crate::errors::SuggestionError;

fn select_meta(pairs: &Vec<Meta>) -> Result<Meta> {
    let meta: Meta =
        Select::new("Select the OpenAPI operationId to patch:", pairs.to_vec())
            .prompt()?;

    Ok(meta)
}

#[derive(Clone)]
struct OpIdRetriever {
    qdrant: Qdrant,
    opid: String,
}

#[async_trait]
impl Retrieve<HybridSearch<Filter>> for OpIdRetriever {
    async fn retrieve(
        &self,
        strategy: &HybridSearch<Filter>,
        query: Query<states::Pending>,
    ) -> Result<Query<states::Retrieved>> {
        let q = self
            .qdrant
            .retrieve(strategy, query)
            .await
            .map_err(|e| SuggestionError::Retrieval(e.to_string()))?;

        let filtered = q
            .documents()
            .iter()
            .cloned()
            .filter(|doc| {
                doc.metadata()
                    .get("operation_id")
                    .map(|m| m == &self.opid)
                    .unwrap_or(false)
            })
            .collect();

        Ok(q.retrieved_documents(filtered))
    }
}

#[derive(Clone)]
struct InjectCodePrompt {
    template: String,
    source_lang: String,
    opid: String,
    method: String,
    path: String,
    source_dir: String,
}

#[async_trait]
impl TransformResponse for InjectCodePrompt {
    async fn transform_response(
        &self,
        mut q: Query<states::Retrieved>,
    ) -> Result<Query<states::Retrieved>> {
        tracing::debug!("Original query: {}", q.current());

        let node = q.documents().get(0).ok_or_else(|| {
            SuggestionError::Retrieval("No code chunks found".into())
        })?;

        let m = node.metadata();

        let outline =
            m.get("Outline").and_then(|v| v.as_str()).unwrap_or("").to_string();

        let chunk = node.content();

        tracing::debug!("Outline: {}", outline);
        tracing::debug!("Node metadata: {:?}", node.metadata());

        let mut ctx = Context::new();
        ctx.insert("source_lang", &self.source_lang);
        ctx.insert("opid", &self.opid);
        ctx.insert("method", &self.method);
        ctx.insert("path", &self.path);
        ctx.insert("source_dir", &self.source_dir);
        ctx.insert("outline", &outline);
        ctx.insert("chunk", &chunk);
        ctx.insert("idempotent", &is_idempotent(&self.method));
        ctx.insert("function_name", &m.get(&self.opid));

        let source_dir = Path::new(&self.source_dir);

        if self.source_lang == "python" {
            let pkg_source =
                fs::read_to_string(source_dir.join("pyproject.toml"))
                    .unwrap_or_default();
            ctx.insert("package_manager", &pkg_source);
        } else if self.source_lang == "rust" {
            let pkg_source = fs::read_to_string(source_dir.join("Cargo.toml"))
                .unwrap_or_default();
            ctx.insert("package_manager", &pkg_source);
        } else if self.source_lang == "go" {
            let pkg_source = fs::read_to_string(source_dir.join("go.mod"))
                .unwrap_or_default();
            ctx.insert("package_manager", &pkg_source);
        }

        if let Some(filepath) = m.get("path") {
            if let Some(s) = filepath.as_str() {
                let p = Path::new(&s);

                let filename: String = p
                    .file_name()
                    .unwrap()
                    .to_os_string()
                    .into_string()
                    .unwrap();
                let filedir: String =
                    p.parent().unwrap().to_str().unwrap().into();

                ctx.insert("filedir", &filedir);
                ctx.insert("filename", &filename);

                let full_source = fs::read_to_string(
                    Path::new(&filedir).join(filename.clone()),
                )
                .unwrap_or_default();
                ctx.insert("full_source_code", &full_source);
            }
        }

        let rendered: String =
            tera::Tera::one_off(&self.template, &ctx, false)?;

        q.transformed_response(rendered);

        tracing::debug!("Updated query: {}", q.current());

        Ok(q)
    }
}

#[derive(Tool, Clone)]
#[tool(
    description = "Given an operationId, method & path, returns a unified diff suggestion for the operation id code handler"
)]
pub struct InjectCode {
    pub meta: Meta,
    pub prompt_model: String,
    pub embed_model: String,
    pub embed_model_dim: u64,
    pub source_dir: String,
    pub source_lang: String,
    pub advices_path: Option<String>,
    pub sender: AsyncSender<CodeReviewEvent>,
}

/// Tool to inject the context of a match code document into the query's context
impl InjectCode {
    pub fn new_with_models(
        prompt_model: &str,
        embed_model: &str,
        embed_model_dim: u64,
        source_dir: &str,
        source_lang: &str,
        meta: Meta,
        advices_path: Option<String>,
        sender: AsyncSender<CodeReviewEvent>,
    ) -> Self {
        InjectCode {
            meta,
            prompt_model: prompt_model.to_string(),
            embed_model: embed_model.to_string(),
            embed_model_dim: embed_model_dim,
            source_dir: source_dir.to_string(),
            source_lang: source_lang.to_string(),
            advices_path,
            sender,
        }
    }

    pub async fn inject_code(
        &self,
        agent_context: &dyn AgentContext,
    ) -> Result<ToolOutput, ToolError> {
        tracing::debug!(
            "Patch tool {} {}",
            self.prompt_model,
            self.embed_model
        );
        let llm = get_client(&self.prompt_model, &self.embed_model)?;

        let fastembed_sparse = FastEmbed::try_default_sparse()?;
        //let fastembed = FastEmbed::try_default()?;

        let search_strategy =
            HybridSearch::default().with_top_n(10).with_top_k(5).to_owned();

        let qdrant: Qdrant = Qdrant::builder()
            .batch_size(50)
            .vector_size(self.embed_model_dim)
            .with_vector(EmbeddedField::Combined)
            .with_sparse_vector(EmbeddedField::Combined)
            .collection_name(CODE_COLLECTION)
            .build()?;

        let retriever = OpIdRetriever {
            qdrant: qdrant.clone(),
            opid: self.meta.opid.to_string().clone(),
        };

        let inject = InjectCodePrompt {
            template: include_str!(
                "prompts/change-suggestion_idempotent_transient-network-error.md"
            )
            .to_string(),
            source_lang: self.source_lang.to_string(),
            opid: self.meta.opid.to_string(),
            method: self.meta.method.to_string(),
            path: self.meta.path.to_string(),
            source_dir: self.source_dir.to_string()
        };

        let pipeline =
            query::Pipeline::from_search_strategy(search_strategy.clone())
                .then_transform_query(query_transformers::Embed::from_client(
                    llm.clone(),
                ))
                .then_transform_query(
                    query_transformers::SparseEmbed::from_client(
                        fastembed_sparse.clone(),
                    ),
                )
                .then_retrieve(retriever)
                .then_transform_response(inject)
                .then_answer(answers::Simple::from_client(llm.clone()));

        let mut ctx = Context::new();
        ctx.insert("source_lang", &self.source_lang);
        ctx.insert("opid", &self.meta.opid);
        ctx.insert("method", &self.meta.method);
        ctx.insert("path", &self.meta.path);
        ctx.insert("source_dir", &self.source_dir);
        ctx.insert("idempotent", &is_idempotent(&self.meta.method));

        if let Some(advices_report) = self.advices_path.clone() {
            let p = Path::new(&advices_report);
            if p.exists() {
                let report = fs::read_to_string(p).unwrap_or_default();
                ctx.insert("advices", &report);
            }
        }

        let tpl = include_str!("prompts/change-base-query.md").to_string();

        let q: String =
            tera::Tera::one_off(&tpl, &ctx, false).map_err(|e| {
                ToolError::ExecutionFailed(CommandError::NonZeroExit(
                    CommandOutput { output: e.to_string() },
                ))
            })?;

        let reply = pipeline.query(q).await?;
        let reviews = reply.answer();

        let review = reviews.to_string();

        self.sender
            .send(CodeReviewEvent {
                phase: CodeReviewEventPhase::Completed,
                review: CodeReviewAnalysis { analysis: review.clone() },
            })
            .await
            .map_err(|e| {
                ToolError::ExecutionFailed(CommandError::NonZeroExit(
                    CommandOutput { output: e.to_string() },
                ))
            })?;

        Ok(ToolOutput::Text(review))
    }
}

fn create_agent(
    meta: Meta,
    source_lang: &str,
    source_dir: &str,
    advices_path: Option<String>,
    client_type: SupportedLLMClient,
    prompt_model: &str,
    reasoning_model: &str,
    embed_model: &str,
    embed_model_dim: u64,
    sender: AsyncSender<CodeReviewEvent>,
) -> Result<Agent> {
    let llm = get_client(prompt_model, embed_model)?;

    let prompt = format!(
        "You are a senior software engineer and you are looking at improving reliability and resilience for HTTP opid={} method={} path={} source_dir={} source_lang={}",
        meta.opid, meta.method, meta.path, source_dir, source_lang
    );

    let agent = Agent::builder()
        .llm(&llm)
        .tools([InjectCode::new_with_models(
            reasoning_model,
            embed_model,
            embed_model_dim,
            source_dir,
            source_lang,
            meta,
            advices_path,
            sender,
        )])
        .system_prompt(prompt)
        .on_new_message(move |_ctx, msg| {
            //let fragment = msg.to_string();
            Box::pin(async move { Ok(()) })
        })
        .build()?;

    Ok(agent)
}

pub async fn review_source(
    metas: &Vec<Meta>,
    source_lang: &str,
    source_dir: &str,
    advices_path: Option<String>,
    client_type: SupportedLLMClient,
    prompt_model: &str,
    reasoning_model: &str,
    embed_model: &str,
    embed_model_dim: u64,
    sender: AsyncSender<CodeReviewEvent>,
) -> Result<()> {
    let meta = select_meta(metas)?;

    let mut agent = create_agent(
        meta,
        source_lang,
        source_dir,
        advices_path,
        client_type,
        prompt_model,
        reasoning_model,
        embed_model,
        embed_model_dim,
        sender,
    )?;
    agent.run_once().await?;

    Ok(())
}

pub fn is_idempotent(method: &str) -> bool {
    matches!(method, "GET" | "PUT" | "DELETE" | "HEAD" | "OPTIONS")
}

#[derive(Debug, Clone, PartialEq)]
pub enum CodeReviewEventPhase {
    Completed,
}

impl fmt::Display for CodeReviewEventPhase {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            CodeReviewEventPhase::Completed => write!(f, "completed"),
        }
    }
}

impl CodeReviewEventPhase {
    pub fn long_form(&self) -> String {
        match self {
            CodeReviewEventPhase::Completed => {
                "Completed code review".to_string()
            }
        }
    }
}

#[derive(Debug, Clone)]
pub struct CodeReviewAnalysis {
    pub analysis: String,
}

impl CodeReviewAnalysis {
    pub fn save(&self, path: &str) -> Result<()> {
        fs::write(path, self.analysis.clone())?;
        Ok(())
    }
}

#[derive(Debug, Clone)]
pub struct CodeReviewEvent {
    pub phase: CodeReviewEventPhase,
    pub review: CodeReviewAnalysis,
}

impl CodeReviewEvent {
    pub fn save_analysis(&self, path: &str) -> Result<()> {
        Ok(self.review.save(path)?)
    }
}
