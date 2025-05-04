use std::fmt;

use anyhow::Result;
use swiftide::indexing::EmbeddedField;
use swiftide::integrations::qdrant::Qdrant;
use swiftide::integrations::{self};
use swiftide::query::answers;
use swiftide::query::query_transformers;
use swiftide::query::{self};

use super::CODE_COLLECTION;
use super::clients::openai::get_client;
use crate::report::types::Report;

pub async fn analyze(report: &Report) -> Result<ReportReviews> {
    let llm = get_client()?;

    let qdrant = Qdrant::builder()
        .batch_size(50)
        .vector_size(3072)
        .with_vector(EmbeddedField::Combined)
        .with_sparse_vector(EmbeddedField::Combined)
        .collection_name(CODE_COLLECTION)
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

    let mut advices = Vec::new();

    let reply= pipeline.query(format!("You are a seasoned {}. Provide actionable insight based on this resilience report.", ReportReviewRole::Developer)).await?;
    advices.push(ReportAdvice {
        role: ReportReviewRole::Developer,
        advice: reply,
    });

    let pipeline = query::Pipeline::default()
        .then_transform_query(
            query_transformers::GenerateSubquestions::from_client(llm.clone()),
        )
        .then_transform_query(query_transformers::Embed::from_client(
            llm.clone(),
        ))
        .then_retrieve(qdrant.clone())
        .then_answer(answers::Simple::from_client(llm.clone()));

    let reply = pipeline.query(format!("You are a seasoned {}. Provide actionable insight based on this resilience report.", ReportReviewRole::Sre)).await?;
    advices.push(ReportAdvice {
        role: ReportReviewRole::Developer,
        advice: reply,
    });

    Ok(ReportReviews { advices })
}

pub enum ReportReviewRole {
    Developer,
    Sre,
}

pub struct ReportAdvice {
    pub role: ReportReviewRole,
    pub advice: query::Query<query::states::Answered>,
}

pub struct ReportReviews {
    pub advices: Vec<ReportAdvice>,
}

impl fmt::Display for ReportReviewRole {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ReportReviewRole::Developer => write!(f, "Developer"),
            ReportReviewRole::Sre => write!(f, "SRE"),
        }
    }
}
