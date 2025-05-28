use std::fmt;
use std::fmt::Display;
use std::fs;
use std::sync::Arc;

use anyhow::Result;
use chrono::Utc;
use kanal::AsyncSender;
use pulldown_cmark::Event;
use pulldown_cmark::HeadingLevel;
use pulldown_cmark::Options;
use pulldown_cmark::Parser;
use pulldown_cmark::Tag;
use pulldown_cmark::TagEnd;
use pulldown_cmark_to_cmark::cmark;
use serde::Deserialize;
use serde::Serialize;
use swiftide::indexing::EmbeddedField;
use swiftide::integrations::qdrant::Qdrant;
use swiftide::integrations::{self};
use swiftide::query::answers;
use swiftide::query::query_transformers;
use swiftide::query::{self};
use swiftide_core::EmbeddingModel;
use swiftide_core::SimplePrompt;
use tera::Context;

use super::CODE_COLLECTION;
use super::clients::SupportedLLMClient;
use super::clients::get_client;
use crate::report;
use crate::report::types::Report;
use crate::report::types::ReportFormat;

pub async fn analyze(
    report: &Report,
    role: &ReportReviewRole,
    sender: AsyncSender<ReviewEvent>,
    client_type: SupportedLLMClient,
    prompt_model: &str,
    embed_model: &str,
) -> Result<ReportReviews> {
    let mut advices = Vec::new();

    let md = report::render::render(report, ReportFormat::Markdown);

    let llm = get_client(client_type, prompt_model, embed_model)?;

    // upcast for later calls
    let sp: Arc<dyn SimplePrompt> = llm.clone();
    let em: Arc<dyn EmbeddingModel> = llm.clone();

    let qdrant: Qdrant = Qdrant::builder()
        .batch_size(50)
        .vector_size(1536)
        .with_vector(EmbeddedField::Combined)
        .with_sparse_vector(EmbeddedField::Combined)
        .collection_name(CODE_COLLECTION)
        .build()?;

    let _ = qdrant.create_index_if_not_exists().await?;

    // we carry a multiple shots analysis for better advices
    // each shot response is injected into the next shot
    let shots = [
        ReviewEventPhase::Summary,
        ReviewEventPhase::Deepdive,
        ReviewEventPhase::Causes,
        ReviewEventPhase::Recommendations,
        ReviewEventPhase::Risks,
        ReviewEventPhase::Executive,
    ];

    let mut previous = String::new();
    for phase in shots.iter() {
        sender
            .send(ReviewEvent {
                phase: phase.clone(),
                advice: previous.clone(),
            })
            .await?;

        let mut ctx = Context::new();
        ctx.insert("role", &role.to_string());
        ctx.insert("report", &md);
        if !previous.is_empty() {
            ctx.insert("previous_advice", &previous);
        }
        let template = match phase {
            ReviewEventPhase::Summary => {
                include_str!("prompts/report-summary.md")
            }
            ReviewEventPhase::Deepdive => {
                include_str!("prompts/report-slo-deepdive.md")
            }
            ReviewEventPhase::Causes => {
                include_str!("prompts/report-causes.md")
            }
            ReviewEventPhase::Recommendations => {
                include_str!("prompts/report-recommendations.md")
            }
            ReviewEventPhase::Risks => include_str!("prompts/report-risks.md"),
            ReviewEventPhase::Executive => {
                include_str!("prompts/report-executive.md")
            }
            other => return Err(anyhow::anyhow!("Unknown shot: {}", other)),
        };
        let q: String = tera::Tera::one_off(template, &ctx, false)?;

        let pipeline = query::Pipeline::default()
            .then_transform_query(
                query_transformers::GenerateSubquestions::from_client(
                    sp.clone(),
                ),
            )
            .then_transform_query(query_transformers::Embed::from_client(
                em.clone(),
            ))
            .then_retrieve(qdrant.clone())
            .then_answer(answers::Simple::from_client(sp.clone()));

        let resp = pipeline.query(q).await?;
        let advice = normalize_markdown(&resp.answer().to_string())?;
        advices.push(ReportAdvice {
            role: role.clone(),
            phase: phase.clone(),
            advice: advice.clone(),
        });
        previous = advice;
    }

    sender
        .send(ReviewEvent {
            phase: ReviewEventPhase::Completed,
            advice: "".to_string(),
        })
        .await?;

    Ok(ReportReviews { advices })
}

#[derive(
    clap::ValueEnum, Clone, Debug, Serialize, Deserialize, Eq, PartialEq,
)]
#[serde(rename_all = "lowercase")]
pub enum ReportReviewRole {
    Developer,
    Sre,
}

#[derive(Debug, Clone)]
pub struct ReportAdvice {
    pub role: ReportReviewRole,
    pub phase: ReviewEventPhase,
    pub advice: String,
}

#[derive(Debug, Clone)]
pub struct ReportReviews {
    pub advices: Vec<ReportAdvice>,
}

impl ReportReviews {
    pub fn save(&self, path: &str) -> Result<String> {
        let md = self.stitch()?;
        fs::write(path, md.clone())?;
        Ok(md)
    }

    pub fn stitch(&self) -> Result<String> {
        let mut stitched = String::new();
        let mut executive = String::new();

        for advice in self.advices.iter() {
            if advice.phase == ReviewEventPhase::Executive {
                executive.push_str(&advice.advice);
                continue;
            }

            stitched.push_str("\n\n");
            stitched.push_str(&advice.advice);
        }

        let mut md = String::new();
        md.push_str(&format!("# fault resilience report analysis"));

        md.push_str("\n\n");
        let toc = generate_toc(&stitched);
        md.push_str(&toc);
        md.push_str("\n\n---\n\n");
        md.push_str(&executive);
        md.push_str("\n\n");
        md.push_str(&stitched);
        md.push_str("\n\n---\n\n");
        md.push_str(&format!("Generated on {}\n\n", Utc::now().to_string()));

        Ok(md)
    }
}

impl fmt::Display for ReportReviewRole {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ReportReviewRole::Developer => write!(f, "Developer"),
            ReportReviewRole::Sre => write!(f, "SRE"),
        }
    }
}

impl ReportReviewRole {
    pub fn from_str(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "developer" => Some(ReportReviewRole::Developer),
            "sre" => Some(ReportReviewRole::Sre),
            _ => None,
        }
    }
}

impl Default for ReportReviewRole {
    fn default() -> Self {
        Self::Developer
    }
}

fn generate_toc(input: &str) -> String {
    let opts = Options::all();
    let parser: Parser<'_> = Parser::new_ext(input, opts);

    // Collect (level, text) for each heading
    let mut headings = Vec::new();
    let mut in_header = false;
    let mut lvl = 0;
    let mut buf = String::new();

    // locate all H2/H3 to build a TOC
    for ev in parser {
        match ev {
            Event::Start(tag) => match tag {
                Tag::Heading { level, .. }
                    if (level == HeadingLevel::H2
                        || level == HeadingLevel::H3) =>
                {
                    in_header = true;
                    lvl = level as usize;
                    buf.clear();
                }
                _ => {}
            },
            Event::End(tag) => match tag {
                TagEnd::Heading(level, ..)
                    if (level == HeadingLevel::H2
                        || level == HeadingLevel::H3) =>
                {
                    in_header = false;
                    headings.push((lvl, buf.clone()));
                }
                _ => {}
            },
            Event::Text(t) if in_header => buf.push_str(&t),
            _ => {}
        }
    }

    // Build the TOC string
    let mut toc = String::from("## Table of Contents\n\n");
    for (level, text) in headings {
        let indent = "  ".repeat(level - 2);
        let anchor = text
            .to_lowercase()
            .chars()
            .filter(|c| c.is_alphanumeric() || c.is_whitespace() || *c == '-')
            .map(|c| if c.is_whitespace() { '-' } else { c })
            .collect::<String>();
        toc.push_str(&format!("{indent}- [{text}](#{anchor})\n"));
    }
    toc.push('\n');
    toc
}

fn normalize_markdown(input: &str) -> Result<String> {
    let opts = Options::all();
    let parser: Parser<'_> = Parser::new_ext(&input, opts);

    let mut buf = String::with_capacity(input.len() + 1024);
    cmark(parser, &mut buf)?;

    Ok(buf)
}

#[derive(Debug, Clone, PartialEq)]
pub enum ReviewEventPhase {
    Summary,
    Deepdive,
    Causes,
    Recommendations,
    Risks,
    Executive,
    Completed,
}

impl fmt::Display for ReviewEventPhase {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ReviewEventPhase::Summary => write!(f, "summary"),
            ReviewEventPhase::Deepdive => write!(f, "deepdive"),
            ReviewEventPhase::Causes => write!(f, "Causes"),
            ReviewEventPhase::Recommendations => write!(f, "recommendations"),
            ReviewEventPhase::Risks => write!(f, "risks"),
            ReviewEventPhase::Executive => write!(f, "executive"),
            ReviewEventPhase::Completed => write!(f, "completed"),
        }
    }
}

impl ReviewEventPhase {
    pub fn long_form(&self) -> String {
        match self {
            ReviewEventPhase::Summary => "Building report summary".to_string(),
            ReviewEventPhase::Deepdive => "Exploring SLO results".to_string(),
            ReviewEventPhase::Causes => {
                "Considering potential causes candidates".to_string()
            }
            ReviewEventPhase::Recommendations => {
                "Crafting actionable recommendations".to_string()
            }
            ReviewEventPhase::Risks => "Deriving risks".to_string(),
            ReviewEventPhase::Executive => {
                "Creating executive summary".to_string()
            }
            ReviewEventPhase::Completed => "Completed analysis".to_string(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct ReviewEvent {
    pub phase: ReviewEventPhase,
    pub advice: String,
}
