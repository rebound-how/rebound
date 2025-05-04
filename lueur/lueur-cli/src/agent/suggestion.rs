use std::error::Error;
use std::path::Path;

use anyhow::Result;
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
use swiftide_agents::Agent;
use swiftide_core::AgentContext;
use swiftide_core::CommandError;
use swiftide_core::CommandOutput;
use swiftide_core::Retrieve;
use swiftide_core::TransformResponse;
use swiftide_macros;
use tera::Context;

use super::meta::Meta;
use crate::agent::CODE_COLLECTION;
use crate::agent::clients::openai::get_client;
use crate::errors::SuggestionError;
use crate::report::types::Report;

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
        let mut q = self
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
    lang: String,
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
        let node = q.documents().get(0).ok_or_else(|| {
            SuggestionError::Retrieval("No code chunks found".into())
        })?;

        let m = node.metadata();

        let outline =
            m.get("outline").and_then(|v| v.as_str()).unwrap_or("").to_string();

        let chunk = node.content();

        println!("{}", outline);
        println!("{:?}", node.metadata());

        let mut ctx = Context::new();
        ctx.insert("lang", &self.lang);
        ctx.insert("opid", &self.opid);
        ctx.insert("method", &self.method);
        ctx.insert("path", &self.path);
        ctx.insert("source_dir", &self.source_dir);
        ctx.insert("outline", &outline);
        ctx.insert("chunk", &chunk);
        ctx.insert("idempotent", &is_idempotent(&self.method));
        ctx.insert("function_name", &m.get(&self.opid));

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
            }
        }

        let rendered: String =
            tera::Tera::one_off(&self.template, &ctx, false)?;

        q.transformed_response(rendered);

        Ok(q)
    }
}

#[swiftide_macros::tool(
    description = "Given an operationId, method & path, returns a unified diff suggestion for the operation id code handler",
    param(name = "opid", description = "OpenAPI operation identifier"),
    param(name = "method", description = "HTTP request method"),
    param(
        name = "path",
        description = "Request path matched to the operation"
    ),
    param(
        name = "source_dir",
        description = "Base directory of the repository source"
    )
)]
async fn propose_patch_tool(
    _context: &dyn AgentContext,
    opid: &str,
    method: &str,
    path: &str,
    source_dir: &str,
) -> Result<ToolOutput, ToolError> {
    let llm = get_client()?;

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
        opid: opid.to_string().clone(),
    };

    let inject = InjectCodePrompt {
        template: include_str!(
            "prompts/change-suggestion_idempotent_transient-network-error.md"
        )
        .to_string(),
        lang: "python".into(),
        opid: opid.to_string(),
        method: method.to_string(),
        path: path.to_string(),
        source_dir: source_dir.to_string(),
    };

    let pipeline =
        query::Pipeline::from_search_strategy(search_strategy.clone())
            .then_transform_query(
                query_transformers::GenerateSubquestions::from_client(
                    llm.clone(),
                ),
            )
            .then_transform_query(query_transformers::Embed::from_client(
                llm.clone(),
            ))
            .then_transform_query(query_transformers::SparseEmbed::from_client(
                fastembed_sparse.clone(),
            ))
            .then_retrieve(retriever)
            .then_transform_response(inject)
            .then_answer(answers::Simple::from_client(llm.clone()));

    let reply = pipeline.query("").await?;
    let proposed = reply.answer();
    println!("{}", proposed);

    let mut files_changes =
        parse_model_suggested_diff(proposed).map_err(|e| {
            ToolError::ExecutionFailed(CommandError::NonZeroExit(
                CommandOutput { output: e.to_string() },
            ))
        })?;

    println!("{:?}", files_changes);

    for fc in files_changes.iter_mut() {
        let path = format!("{}/{}", source_dir, fc.old_path.replace("a/", ""));
        println!("{}", path);
        let file_content = std::fs::read_to_string(&path).map_err(|e| {
            ToolError::ExecutionFailed(CommandError::NonZeroExit(
                CommandOutput { output: e.to_string() },
            ))
        })?;

        // llms aren't very smart overall, so you need to align their response
        // with reality
        realign_hunks(&file_content, &mut fc.hunks);

        println!(
            "Generated diff hunks: {} {:?} {}",
            path,
            fc.hunks,
            fc.as_diff_string()?
        );
    }

    let mut full_diff = String::new();
    for fc in files_changes {
        full_diff.push_str(&fc.as_diff_string().map_err(ToolError::from)?);
    }

    println!("{}", full_diff);

    Ok(ToolOutput::Text(full_diff))
}

fn create_agent(meta: Meta, source_dir: &str) -> Result<Agent> {
    let client = integrations::openai::OpenAI::builder()
        .default_prompt_model("gpt-4o-mini")
        .build()?;

    let llm = LanguageModelWithBackOff::new(client, Default::default());

    let prompt = format!(
        "You are a senior software engineer and you are looking at improvine reliability and resilience from for HTTP opid={} method={} path={} source_dir={}",
        meta.opid, meta.method, meta.path, source_dir
    );

    let agent = Agent::builder()
        .llm(&llm)
        .tools([propose_patch_tool()])
        .system_prompt(prompt)
        .on_new_message(move |_ctx, msg| {
            let fragment = msg.to_string();
            Box::pin(async move {
                // Stream each assistant chunk immediately
                println!("{fragment}");
                Ok(())
            })
        })
        .build()?;

    Ok(agent)
}

pub async fn make(
    report: &Report,
    metas: &Vec<Meta>,
    source_dir: &str,
) -> Result<()> {
    let meta = select_meta(metas)?;

    let mut agent = create_agent(meta, source_dir)?;
    agent.run_once().await?;

    /*
    let change = strip_change(reply.answer());

    println!("{}", change);

    let patch = Patch::from_str(&change)?;
    let fmt = PatchFormatter::new().with_color();

    println!("Suggested patch for `{opid}`:");
    print!("{}", fmt.fmt_patch(&patch));

    let branch = "changes";
    let message = "feat(reliability) Improve reliability";

    apply_patch(&source_dir, &change, &branch, &message)?;
    */
    Ok(())
}

pub fn is_idempotent(method: &str) -> bool {
    matches!(method, "GET" | "PUT" | "DELETE" | "HEAD" | "OPTIONS")
}

fn strip_change(change: &str) -> &str {
    let change = change.trim();
    let change = change.strip_prefix("```").unwrap_or(change);
    let change = change.strip_suffix("```").unwrap_or(change);
    let change = if let Some(pos) = change.find("--- ") {
        &change[pos..]
    } else {
        change
    };
    let change = change.trim();

    change
}

/// Represents a diff for a single file.
#[derive(Debug, Clone)]
pub struct FileDiff {
    pub old_path: String,
    pub new_path: String,
    pub hunks: Vec<Hunk>,
}

impl FileDiff {
    pub fn as_diff_string(&self) -> Result<String> {
        // Build unified diff string
        let mut text = String::new();
        text.push_str(&format!(
            "--- {}
",
            self.old_path
        ));
        text.push_str(&format!(
            "+++ {}
",
            self.new_path
        ));
        for h in &self.hunks {
            text.push_str(&format!(
                "{}
",
                h.header
            ));
            for line in &h.lines {
                text.push_str(&format!(
                    "{}
",
                    line
                ));
            }
        }
        let patch = Patch::from_str(&text)?;
        let fmt = PatchFormatter::new().with_color();
        let patch = format!("{}", fmt.fmt_patch(&patch));
        Ok(patch)
    }
}

/// Represents a single hunk within a file diff.
#[derive(Debug, Clone)]
pub struct Hunk {
    /// The hunk header, e.g., "@@ -1,4 +1,5 @@"
    pub header: String,
    /// The lines belonging to this hunk (including leading '+', '-', ' ')
    pub lines: Vec<String>,
    pub orig_start: usize,
    pub orig_count: usize,
    pub new_start: usize,
    pub new_count: usize,
}

// We cannot trust llm output as-is
// So we parse what it gave us and try to reconstruct the diff
// with appropriate hunk blocks.
// There are likely many corner cases where this might fail...
pub fn parse_model_suggested_diff(
    diff: &str,
) -> Result<Vec<FileDiff>, SuggestionError> {
    let mut files = Vec::new();

    // iterators are great things
    let mut lines = diff.lines().peekable();

    while let Some(line) = lines.next() {
        if line.starts_with("--- ") {
            // ignore "--- "
            let old_path = line[4..].trim().to_string();
            let next = lines.next().ok_or(SuggestionError::InvalidHunk(
                "Unexpected end after --- line".to_string(),
            ))?;

            if !next.starts_with("+++ ") {
                return Err(SuggestionError::InvalidHunk(format!(
                    "Expected +++ after ---, found: {}",
                    next
                )));
            }
            // ignore "+++ "
            let new_path = next[4..].trim().to_string();

            let mut hunks = Vec::new();

            while let Some(&peek) = lines.peek() {
                // next hunk
                if !peek.starts_with("@@ ") {
                    break;
                }

                if let Some(header_line) = lines.find(|l| l.starts_with("@@ "))
                {
                    let header = header_line.to_string();
                    let parts: Vec<&str> =
                        header.trim_matches('@').trim().split(' ').collect();

                    let (orig_start, _) = parse_range(parts.get(0).ok_or(
                        SuggestionError::InvalidHunk(
                            "Missing orig range".to_string(),
                        ),
                    )?)
                    .map_err(|e| SuggestionError::InvalidHunk(e.to_string()))?;

                    let (new_start, _) = parse_range(parts.get(1).ok_or(
                        SuggestionError::InvalidHunk(
                            "Missing new range".to_string(),
                        ),
                    )?)
                    .map_err(|e| SuggestionError::InvalidHunk(e.to_string()))?;

                    let mut hunk_lines = Vec::new();
                    while let Some(&l) = lines.peek() {
                        if l.starts_with("@@ ") || l.starts_with("--- ") {
                            break;
                        }
                        let next_line = lines.next().unwrap().to_string();
                        let trimmed = next_line.trim();
                        // Skip markdown fences or stray backtick-only lines
                        if trimmed.starts_with("```")
                            || trimmed.chars().all(|c| c == '`')
                        {
                            continue;
                        }
                        hunk_lines.push(next_line);
                    }

                    // recalculate the actual line counts
                    let orig_count = hunk_lines
                        .iter()
                        .filter(|l| l.starts_with(' ') || l.starts_with('-'))
                        .count();
                    let new_count = hunk_lines
                        .iter()
                        .filter(|l| l.starts_with(' ') || l.starts_with('+'))
                        .count();

                    hunks.push(Hunk {
                        header,
                        lines: hunk_lines,
                        orig_start,
                        orig_count,
                        new_start,
                        new_count,
                    });
                } else {
                    break;
                }
            }
            files.push(FileDiff { old_path, new_path, hunks });
        }
    }
    Ok(files)
}

fn parse_range(s: &str) -> Result<(usize, usize), Box<dyn Error>> {
    let s = s.trim_start_matches('-').trim_start_matches('+');
    let mut it = s.split(',');
    let start: usize = it.next().ok_or("Missing start")?.parse()?;
    let count: usize = it.next().unwrap_or("1").parse()?;
    Ok((start, count))
}

/// Attempts to adjust hunk headers to match actual file lines.
/// For each hunk, finds the best matching offset in `file_contents` based
/// on the first non-add/remove context line, and updates `orig_start` and
/// `new_start` accordingly.
pub fn realign_hunks(file: &str, hunks: &mut [Hunk]) {
    let lines: Vec<&str> = file.lines().collect();
    for hunk in hunks.iter_mut() {
        // find a context line (starting with ' ')
        if let Some(context_line) =
            hunk.lines.iter().find(|l| l.starts_with(' '))
        {
            let context = context_line.trim_start_matches(' ');
            // search for context in file lines
            for (idx, &line) in lines.iter().enumerate() {
                if line.trim() == context.trim() {
                    // adjust original start to this 1-based index
                    let new_orig = idx + 1;
                    let delta = new_orig as isize - hunk.orig_start as isize;
                    hunk.orig_start = new_orig;
                    // apply same delta to new_start
                    hunk.new_start =
                        ((hunk.new_start as isize) + delta) as usize;
                    // rebuild header string
                    hunk.header = format!(
                        "@@ -{},{} +{},{} @@",
                        hunk.orig_start,
                        hunk.orig_count,
                        hunk.new_start,
                        hunk.new_count
                    );
                    break;
                }
            }
        }
    }
}
