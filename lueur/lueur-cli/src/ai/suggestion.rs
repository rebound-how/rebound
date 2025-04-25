use std::error::Error;
use std::fmt;

use anyhow::Result;
use diffy::Patch;
use diffy::PatchFormatter;
use inquire::Select;
use inquire::Text;
use swiftide::indexing::LanguageModelWithBackOff;
use swiftide::indexing::transformers::Embed;
use swiftide::integrations::qdrant::Qdrant;
use swiftide::integrations::{self};
use swiftide::prompt::Prompt;
use swiftide::query::answers;
use swiftide::query::answers::Simple;
use swiftide::query::query_transformers;
use swiftide::query::{self};
use tera::Context;

use crate::errors::SuggestionError;
use crate::report::types::Report;

pub async fn make(report: &Report, source_dir: &str) -> Result<()> {
    let mut pairs = Vec::<Meta>::new();

    for scenario in &report.scenario_summaries {
        for item in &scenario.item_summaries {
            if let Some(meta) = &item.meta {
                if let Some(opid) = &meta.operation_id {
                    let m = Meta {
                        method: item.call.method.clone(),
                        opid: opid.clone(),
                        path: item.call.url.clone(),
                    };

                    if !pairs.contains(&m) {
                        pairs.push(m);
                    }
                }
            }
        }
    }

    let pair: Meta =
        Select::new("Select th OpenAPI operationId to patch:", pairs)
            .prompt()?;
    let opid = pair.opid;
    let method = pair.method;
    let path = pair.path;
    let idem = is_idempotent(&method);

    let client = integrations::openai::OpenAI::builder()
        .default_embed_model("text-embedding-3-small")
        .default_prompt_model("gpt-4o-mini")
        .build()?;

    let llm = LanguageModelWithBackOff::new(client, Default::default());

    let qdrant = Qdrant::builder()
        .batch_size(50)
        .vector_size(3072)
        .collection_name("swiftide-examples")
        .build()?;

    let pipeline = query::Pipeline::default()
        .then_transform_query(
            query_transformers::GenerateSubquestions::from_client(llm.clone()),
        )
        .then_transform_query(query_transformers::Embed::from_client(
            llm.clone(),
        ))
        .then_retrieve(qdrant.clone())
        .then_answer(answers::Simple::from_client(llm.clone()));

    let mut prompt: Prompt = include_str!(
        "prompts/change-suggestion_idempotent_transient-network-error.md"
    )
    .into();

    let mut ctx = Context::new();
    ctx.insert("lang", "python");
    ctx.insert("opid", &opid);
    ctx.insert("path", &path);
    ctx.insert("method", &method);
    if idem {
        ctx.insert("idempotent", "yes");
    } else {
        ctx.insert("idempotent", "no");
    }

    prompt = prompt.with_context(ctx);

    let q = prompt.render()?;

    tracing::debug!("Prompt, {}", q);

    let reply = pipeline.query(q).await?;

    let mut files_changes = parse_model_suggested_diff(&reply.answer())?;

    for fc in files_changes.iter_mut() {
        let path = format!("{}/{}", source_dir, fc.old_path.replace("a/", ""));
        let file_content = std::fs::read_to_string(&path)?;

        // llms aren't very smart overall, so you need to align their response
        // with reality
        realign_hunks(&file_content, &mut fc.hunks);

        tracing::debug!(
            "Generated diff hunks: {} {:?} {}",
            path,
            fc.hunks,
            fc.as_diff_string()?
        );
    }

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


#[derive(Debug, Clone, PartialEq)]
pub struct Meta {
    pub method: String,
    pub opid: String,
    pub path: String,
}

impl fmt::Display for Meta {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} [{} {}]", self.opid, self.method, self.path)
    }
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

fn apply_patch(
    source_dir: &str,
    diff: &str,
    branch: &str,
    message: &str,
) -> anyhow::Result<()> {
    use std::fs;
    use std::process::Command;
    // 1. Write diff to temp file
    let patch_file = &format!("{}/lueur_patch.diff", source_dir);
    fs::write(patch_file, diff)?;

    // 2. Create and switch to new branch
    Command::new("git")
        .current_dir(source_dir)
        .args(&["checkout", "-b", branch])
        .status()?;

    // 3. Apply patch and stage changes
    Command::new("git")
        .current_dir(source_dir)
        .args(&["apply", "--index", patch_file])
        .status()?;

    // 4. Commit changes
    Command::new("git")
        .current_dir(source_dir)
        .args(&["commit", "-m", message])
        .status()?;

    // 5. Clean up
    let _ = fs::remove_file(patch_file);

    Ok(())
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
