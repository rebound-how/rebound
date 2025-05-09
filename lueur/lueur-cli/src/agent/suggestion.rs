use std::error::Error;
use std::fs;
use std::io;
use std::path::Path;

use anyhow::Result;
use anyhow::anyhow;
use async_trait::async_trait;
use diffy::Patch;
use diffy::PatchFormatter;
use inquire::Select;
use swiftide::chat_completion::ToolOutput;
use swiftide::chat_completion::errors::ToolError;
use swiftide::indexing::EmbeddedField;
use swiftide::indexing::LanguageModelWithBackOff;
use swiftide::integrations::fastembed::FastEmbed;
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
impl Retrieve<HybridSearch> for OpIdRetriever {
    async fn retrieve(
        &self,
        strategy: &HybridSearch,
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
            let pkg_source = fs::read_to_string(source_dir.join("pyproject.toml")).unwrap_or_default();
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

                let full_source = fs::read_to_string(Path::new(&filedir).join(filename.clone())).unwrap_or_default();
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
    pub source_dir: String,
    pub source_lang: String,
}

impl InjectCode {
    pub fn new_with_models(
        prompt_model: &str,
        embed_model: &str,
        source_dir: &str,
        source_lang: &str,
        meta: Meta,
    ) -> Self {
        InjectCode {
            meta,
            prompt_model: prompt_model.to_string(),
            embed_model: embed_model.to_string(),
            source_dir: source_dir.to_string(),
            source_lang: source_lang.to_string(),
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
            .vector_size(3072)
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

        let tpl = include_str!("prompts/change-base-query.md").to_string();

        let q: String =
            tera::Tera::one_off(&tpl, &ctx, false).map_err(|e| {
                ToolError::ExecutionFailed(CommandError::NonZeroExit(
                    CommandOutput { output: e.to_string() },
                ))
            })?;

        let reply = pipeline.query(q).await?;
        let proposed = reply.answer();

        tracing::debug!("{}", proposed);

        let source_dir_path = Path::new(&self.source_dir);
        let mut files_changes =
            parse_model_suggested_diff(proposed, source_dir_path).map_err(|e| {
                ToolError::ExecutionFailed(CommandError::NonZeroExit(
                    CommandOutput { output: e.to_string() },
                ))
            })?;

        tracing::debug!("Files changed {:?}", files_changes);

        let review_tpl = include_str!("prompts/change-review.md").to_string();

        for fc in files_changes.iter_mut() {
            let mut filename = fc.old_path.replace("a/", "");

            if filename == "/dev/null" {
                filename = fc.new_path.replace("b/", "");
                fc.old_path = format!("a/{}", filename);
            }

            let path = format!(
                "{}/{}",
                self.source_dir,
                filename
            );

            tracing::debug!("File to change Path: {}", path);

            let review_pipeline =
                query::Pipeline::default()
                .then_transform_query(query_transformers::Embed::from_client(
                    llm.clone(),
                ))
                .then_transform_query(
                    query_transformers::SparseEmbed::from_client(
                        fastembed_sparse.clone(),
                    ),
                )
                .then_retrieve(qdrant.clone())
                .then_answer(answers::Simple::from_client(llm.clone()));

            
            let mut ctx = Context::new();
            
            let full_source = fs::read_to_string(Path::new(&path)).unwrap_or_default();
            ctx.insert("full_source_code", &full_source);
            ctx.insert("proposed_change", &fc.as_diff_string().map_err(ToolError::from)?);

            let q: String = tera::Tera::one_off(&review_tpl, &ctx, false).map_err(|e| {
                ToolError::ExecutionFailed(CommandError::NonZeroExit(
                    CommandOutput { output: e.to_string() },
                ))
            })?;

            let resp = review_pipeline.query(q).await?;

            println!("{}", resp.answer());

            /* let file_content = std::fs::read_to_string(&path).map_err(|e| {
                ToolError::ExecutionFailed(CommandError::NonZeroExit(
                    CommandOutput { output: e.to_string() },
                ))
            })?;

            // llms aren't very smart overall, so you need to align their
            // response with reality
            realign_hunks(&file_content, &mut fc.hunks);

            tracing::debug!("Realigned hunks: {:?}", fc.hunks);
            */
        }

        let mut full_diff = String::new();
        for fc in files_changes {
            full_diff.push_str(&fc.as_diff_string().map_err(ToolError::from)?);
        }


        println!("{}", full_diff);

        Ok(ToolOutput::Text(full_diff))
    }
}

fn create_agent(
    meta: Meta,
    source_lang: &str,
    source_dir: &str,
    client_type: SupportedLLMClient,
    prompt_model: &str,
    reasoning_model: &str,
    embed_model: &str,
) -> Result<Agent> {
    let llm = get_client(prompt_model, embed_model)?;

    let prompt = format!(
        "You are a senior software engineer and you are looking at improvine reliability and resilience from for HTTP opid={} method={} path={} source_dir={} source_lang={}",
        meta.opid, meta.method, meta.path, source_dir, source_lang
    );

    let agent = Agent::builder()
        .llm(&llm)
        .tools([InjectCode::new_with_models(
            reasoning_model,
            embed_model,
            source_dir,
            source_lang,
            meta,
        )])
        .system_prompt(prompt)
        .on_new_message(move |_ctx, msg| {
            let fragment = msg.to_string();
            Box::pin(async move { Ok(()) })
        })
        .build()?;

    Ok(agent)
}

pub async fn review_source(
    metas: &Vec<Meta>,
    source_lang: &str,
    source_dir: &str,
    client_type: SupportedLLMClient,
    prompt_model: &str,
    reasoning_model: &str,
    embed_model: &str,
) -> Result<()> {
    let meta = select_meta(metas)?;

    let mut agent = create_agent(
        meta,
        source_lang,
        source_dir,
        client_type,
        prompt_model,
        reasoning_model,
        embed_model,
    )?;
    agent.run_once().await?;

    Ok(())
}

pub fn is_idempotent(method: &str) -> bool {
    matches!(method, "GET" | "PUT" | "DELETE" | "HEAD" | "OPTIONS")
}

/// Represents a diff for a single file.
#[derive(Debug, Clone)]
pub struct FileDiff {
    pub old_path: String,
    pub new_path: String,
    pub hunks: Vec<Hunk>,
}

impl FileDiff {
    /// Render back to a colored unified‐diff string.
    pub fn as_diff_string(&self) -> Result<String> {
        let mut text = String::new();
        text += &format!("--- {}\n", self.old_path);
        text += &format!("+++ {}\n", self.new_path);
        for h in &self.hunks {
            text += &format!("{}\n", h.header);
            for ln in &h.lines {
                text += &format!("{}\n", ln);
            }
        }
        let patch = Patch::from_str(&text)
            .map_err(|e| SuggestionError::InvalidHunk(e.to_string()))?;
        let fmt = PatchFormatter::new().with_color();
        Ok(fmt.fmt_patch(&patch).to_string())
    }
}

/// Represents a single hunk within a file diff.
#[derive(Debug, Clone)]
pub struct Hunk {
    pub header: String,    // e.g. "@@ -1,4 +1,5 @@"
    pub lines: Vec<String>,// including leading ' ', '+' or '-'
    pub orig_start: usize,
    pub orig_count: usize,
    pub new_start: usize,
    pub new_count: usize,
}

/// A parser that **ignores** any header ranges from the LLM and instead
/// always locates each hunk by searching the file’s content.
pub fn parse_model_suggested_diff(
    diff: &str,
    source_dir: &Path,
) -> Result<Vec<FileDiff>, SuggestionError> {
    let mut result = Vec::new();
    let mut lines = diff.lines().peekable();

    while let Some(line) = lines.next() {
        if !line.starts_with("--- ") {
            continue;
        }
        let raw_old = line[4..].trim();
        let raw_new = lines
            .next()
            .ok_or_else(|| SuggestionError::InvalidHunk("Missing +++".into()))?;
        if !raw_new.starts_with("+++ ") {
            return Err(SuggestionError::InvalidHunk(format!(
                "Bad +++ line: {}",
                raw_new
            )));
        }

        // Load file for anchoring (skip /dev/null)
        let file_txt = if raw_old != "/dev/null" {
            let rel = raw_old.strip_prefix("a/").unwrap_or(raw_old);
            fs::read_to_string(source_dir.join(rel)).unwrap_or_default()
        } else {
            String::new()
        };
        let file_lines: Vec<&str> = file_txt.lines().collect();

        let mut hunks = Vec::new();
        while let Some(&peek) = lines.peek() {
            if !peek.starts_with("@@ ") {
                break;
            }
            // skip raw header
            let raw_header = lines.next().unwrap();

            // strip trailing code to capture any inline context
            let mut extra_ctx = None;
            if let Some(idx) = raw_header.rfind("@@") {
                let tail = raw_header[idx+2..].trim();
                if !tail.is_empty() {
                    extra_ctx = Some(format!(" {}", tail));
                }
            }

            // collect hunk lines
            let mut body = Vec::new();
            if let Some(ctx) = extra_ctx.take() {
                body.push(ctx);
            }
            while let Some(&l) = lines.peek() {
                if l.starts_with("@@ ") || l.starts_with("--- ") {
                    break;
                }
                let ln = lines.next().unwrap().to_string();
                let t = ln.trim();
                if t.starts_with("```") || t.chars().all(|c| c=='`') {
                    continue;
                }
                if t.is_empty() {
                    body.push(" ".into());
                } else {
                    body.push(ln);
                }
            }

            // find first context line (body entry starting with ' ')
            let orig_start = body.iter()
                .find_map(|l| if l.starts_with(' ') {
                    Some(l.trim_start_matches(' '))
                } else { None })
                .and_then(|anchor| {
                    file_lines.iter()
                        .position(|&fl| fl.contains(anchor))
                        .map(|i| i+1)
                })
                .unwrap_or(1);  // fallback to line 1

            // new_start = orig_start (we assume no file‐length shift before hunk)
            let new_start = orig_start;

            // recompute counts
            let orig_count = body.iter().filter(|l| l.starts_with(' ') || l.starts_with('-')).count();
            let new_count  = body.iter().filter(|l| l.starts_with(' ') || l.starts_with('+')).count();

            let header = format!("@@ -{},{} +{},{} @@", orig_start, orig_count, new_start, new_count);

            hunks.push(Hunk {
                header,
                lines:      body,
                orig_start,
                orig_count,
                new_start,
                new_count,
            });
        }

        result.push(FileDiff {
            old_path: raw_old.to_string(),
            new_path: raw_new[4..].trim().to_string(),
            hunks,
        });
    }

    Ok(result)
}
/// Parse "-12,5" or "+7" into (start, count).
fn parse_range(s: &str) -> Result<(usize, usize), Box<dyn Error>> {
    let s = s.trim_start_matches('-').trim_start_matches('+');
    let mut it = s.split(',');
    let start: usize = it.next().ok_or("missing start")?.parse()?;
    let count: usize = it.next().unwrap_or("1").parse()?;
    Ok((start, count))
}

/// Adjust each hunk’s header to match the actual `file` contents:
/// 1) prefer a context line (` ` prefix) as anchor  
/// 2) otherwise, use the first non-empty `+`/`-` line stripped of its prefix
pub fn realign_hunks(file: &str, hunks: &mut [Hunk]) {
    let lines: Vec<&str> = file.lines().collect();
    for hunk in hunks.iter_mut() {
        let maybe_anchor = hunk
            .lines
            .iter()
            .find_map(|l| {
                if l.starts_with(' ') {
                    Some(l.trim_start_matches(' '))
                } else {
                    None
                }
            })
            .or_else(|| {
                hunk.lines.iter().find_map(|l| {
                    if let Some(rest) = l.strip_prefix('+').or_else(|| l.strip_prefix('-')) {
                        let txt = rest.trim();
                        if !txt.is_empty() {
                            return Some(txt);
                        }
                    }
                    None
                })
            });

        if let Some(anchor) = maybe_anchor {
            for (idx, &line) in lines.iter().enumerate() {
                if line.contains(anchor) {
                    let new_orig = idx + 1;
                    let delta = new_orig as isize - hunk.orig_start as isize;
                    hunk.orig_start = new_orig;
                    hunk.new_start = ((hunk.new_start as isize) + delta) as usize;
                    hunk.header = format!(
                        "@@ -{},{} +{},{} @@",
                        hunk.orig_start, hunk.orig_count, hunk.new_start, hunk.new_count
                    );
                    break;
                }
            }
        }
    }
}
