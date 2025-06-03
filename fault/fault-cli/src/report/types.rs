use std::fmt;
use std::fs;

use anyhow::Result;
use serde::Deserialize;
use serde::Serialize;

use super::render;
#[cfg(feature = "discovery")]
use crate::discovery::types::Resource;
use crate::scenario::types::ScenarioItemCall;
use crate::scenario::types::ScenarioItemCallOpenAPIMeta;
use crate::scenario::types::ScenarioItemCallStrategy;
use crate::scenario::types::ScenarioItemExpectation;
use crate::types::FaultConfiguration;

pub enum ReportFormat {
    Text,
    Markdown,
    Html,
    Json,
    Yaml,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Report {
    #[serde(with = "chrono::serde::ts_microseconds")]
    pub start_time: chrono::DateTime<chrono::Utc>,
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    pub scenario_summaries: Vec<ScenarioSummary>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioSummary {
    pub title: String,
    pub description: String,
    #[serde(with = "chrono::serde::ts_microseconds")]
    pub scenario_start_time: chrono::DateTime<chrono::Utc>,

    pub item_count: usize,
    pub total_duration_ms: f64,

    pub item_summaries: Vec<ItemSummary>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemSummary {
    pub url: String,
    pub call: ScenarioItemCall,
    pub faults: Vec<FaultConfiguration>,
    pub strategy_mode: ScenarioItemCallStrategy,
    pub expectation: Option<ScenarioItemExpectation>,
    pub meta: Option<ScenarioItemCallOpenAPIMeta>,
    pub run_overview: Vec<RunOverview>,
    pub slo_impact_table: Vec<SloImpactRow>,
    pub failure_count: usize,
    pub error_count: usize,
    pub final_status: ItemStatus,

    #[cfg(any(feature = "discovery", feature = "injection"))]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub resources: Option<Vec<Resource>>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct LatencyPercentile {
    pub percentile: f64,
    pub latency: f64,
    pub count: usize,
}

impl LatencyPercentile {
    pub fn new(percentile: f64, latency: f64, count: usize) -> Self {
        Self { percentile, latency, count }
    }
}

/// For a single iteration or load-run
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RunOverview {
    pub iteration: Option<usize>,
    pub requests_count: usize,
    pub latency_percentiles: Vec<LatencyPercentile>,
    pub min_latency: f64,
    pub max_latency: f64,
    pub failure_count: usize,
    pub error_count: usize,
    pub total_time: f64, // in seconds
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ItemStatus {
    Pass,
    Fail,
    Unknown,
}

impl fmt::Display for ItemStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ItemStatus::Pass => write!(f, "Passed"),
            ItemStatus::Fail => write!(f, "Failed"),
            ItemStatus::Unknown => write!(f, "-"),
        }
    }
}

/// For each SLO declared, how close we are
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SloImpactRow {
    pub title: String,
    pub pass: bool,
    /// e.g. “–150ms buffer” or “+40ms over threshold”
    pub margin_text: String,
    /// Possibly how many calls are over threshold
    pub calls_over_threshold: usize,
    pub calls_over_threshold_percent: f64,

    pub objective: f64,
    pub threshold: f64,
    pub unit: String,
}

impl Report {
    pub fn save(&self, path: &str) -> Result<String> {
        let md = render::render(&self, ReportFormat::Markdown);
        fs::write(path, md.clone())?;
        Ok(md)
    }
}
