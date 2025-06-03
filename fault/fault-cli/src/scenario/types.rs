use std::collections::BTreeMap;
use std::collections::HashMap;
use std::fmt;
use std::fs::File;
use std::io::BufWriter;
use std::time::Duration;

use chrono::DateTime;
use chrono::Utc;
use regex::Regex;
use serde::Deserialize;
use serde::Serialize;
use url::Url;

#[cfg(feature = "discovery")]
use crate::discovery::types::Resource;
use crate::errors::ScenarioError;
use crate::event::FaultEvent;
use crate::report::types::LatencyPercentile;
use crate::types::Direction;
use crate::types::DnsTiming;
use crate::types::FaultConfiguration;

///
/// Scenario description structures

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioItemExpectation {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub status: Option<u16>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub response_time_under: Option<f64>, // ms
    #[serde(skip_serializing_if = "Option::is_none")]
    pub all_slo_are_valid: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioItemCall {
    pub method: String, // HTTP method (e.g., GET, POST)
    pub url: String,    // Target URL
    #[serde(skip_serializing_if = "Option::is_none")]
    pub headers: Option<HashMap<String, String>>, // Optional headers
    #[serde(skip_serializing_if = "Option::is_none")]
    pub body: Option<String>, // Optional request body
    #[serde(skip_serializing_if = "Option::is_none")]
    pub timeout: Option<u64>, // Optional timeout in ms to fail the request
    #[serde(skip_serializing_if = "Option::is_none")]
    pub meta: Option<ScenarioItemCallOpenAPIMeta>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioItemCallOpenAPIMeta {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub operation_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioItemSLO {
    #[serde(alias = "type")]
    pub slo_type: String,
    pub title: String,
    pub objective: f64,
    pub threshold: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioItemProxySettings {
    pub disable_http_proxies: bool,
    pub proxies: Vec<String>,
}

#[cfg(feature = "discovery")]
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "platform", rename_all = "lowercase")]
pub enum ScenarioItemRunsOn {
    Kubernetes {
        ns: String,
        service: String,
        #[serde(skip_serializing_if = "Option::is_none")]
        image: Option<String>,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioItemContext {
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub upstreams: Vec<String>,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub faults: Vec<FaultConfiguration>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub strategy: Option<ScenarioItemCallStrategy>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub slo: Option<Vec<ScenarioItemSLO>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub proxy: Option<ScenarioItemProxySettings>,

    #[cfg(feature = "discovery")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub runs_on: Option<ScenarioItemRunsOn>,
}

impl ScenarioItemContext {
    pub fn faults_to_environment_variables(&self) -> BTreeMap<String, String> {
        let mut map = BTreeMap::<String, String>::default();

        for f in &self.faults {
            let vars = &mut f.to_environment_variables();
            map.append(vars);
        }

        if let Some(strategy) = &self.strategy {
            match strategy {
                ScenarioItemCallStrategy::Repeat { .. } => {}
                ScenarioItemCallStrategy::Load { duration, .. } => {
                    map.insert(
                        "FAULT_PROXY_DURATION".to_string(),
                        duration.to_string(),
                    );
                }
                ScenarioItemCallStrategy::Single {} => {}
            }
        }

        map
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "mode", rename_all = "lowercase")]
pub enum ScenarioItemCallStrategy {
    Repeat {
        #[serde(skip_serializing_if = "Option::is_none")]
        failfast: Option<bool>,
        step: f64,
        count: usize,
        #[serde(skip_serializing_if = "Option::is_none")]
        wait: Option<f64>,
        #[serde(skip_serializing_if = "Option::is_none")]
        add_baseline_call: Option<bool>,
    },

    Load {
        duration: String,
        clients: usize,
        rps: usize,
    },

    Single {},
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ScenarioItemCallStrategyMode {
    Repeat,
}

impl Default for ScenarioItemCallStrategyMode {
    fn default() -> Self {
        Self::Repeat
    }
}

impl fmt::Display for ScenarioItemCallStrategyMode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ScenarioItemCallStrategyMode::Repeat => write!(f, "repeat"),
        }
    }
}

/// A single entry in the scenario
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioItem {
    pub call: ScenarioItemCall,
    pub context: ScenarioItemContext,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub expect: Option<ScenarioItemExpectation>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HTTPPathsConfig {
    #[serde(skip_serializing_if = "HashMap::is_empty")]
    pub segments: HashMap<String, String>,
}

/// Global HTTP configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioHTTPGlobalConfig {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub headers: Option<HashMap<String, String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub paths: Option<HTTPPathsConfig>,
}

/// Global configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioGlobalConfig {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub http: Option<ScenarioHTTPGlobalConfig>,
}

impl ScenarioGlobalConfig {
    pub fn from_url(url: &str) -> anyhow::Result<Option<Self>> {
        let re = Regex::new(r"^\{([^/]+)\}$").unwrap();
        let mut segments = HashMap::new();

        for part in url.split('/') {
            if let Some(cap) = re.captures(part) {
                segments.insert(cap[1].to_string(), String::new());
            }
        }

        if segments.is_empty() {
            return Ok(None);
        }

        let http = Some(ScenarioHTTPGlobalConfig {
            headers: None,
            paths: Some(HTTPPathsConfig { segments }),
        });

        Ok(Some(ScenarioGlobalConfig { http }))
    }
}

/// The overall scenario containing multiple entries
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Scenario {
    pub title: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    pub items: Vec<ScenarioItem>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub config: Option<ScenarioGlobalConfig>,
}

///
/// Scenario results structures

// see https://github.com/serde-rs/serde/issues/1560#issuecomment-1666846833
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum ItemExpectationDecision {
    Success,
    Failure,
    #[serde(untagged)]
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemHttpExpectation {
    pub status_code: Option<u16>,
    pub response_time_under: Option<f64>,
    pub all_slo_are_valid: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemHttpResult {
    pub status_code: Option<u16>,
    pub response_time: Option<f64>,
    pub all_slo_are_valid: Option<bool>,
    pub decision: ItemExpectationDecision,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum ItemExpectation {
    Http { wanted: ItemHttpExpectation, got: Option<ItemHttpResult> },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemFault {
    pub event: FaultEvent,
    pub direction: Direction,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemEvent {
    pub event: FaultEvent,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum ItemProtocol {
    Http { code: u16, body_length: usize },
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ItemMetricsFaults {
    pub url: String,
    pub applied: Option<Vec<ItemEvent>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemMetrics {
    pub dns: Vec<DnsTiming>,
    pub protocol: Option<ItemProtocol>,
    pub ttfb: f64,
    pub total_time: f64,
    pub faults: Vec<ItemMetricsFaults>,
    pub errored: bool,
    pub timed_out: bool,
}

impl ItemMetrics {
    pub fn new() -> Self {
        ItemMetrics {
            dns: Vec::new(),
            ttfb: 0.0,
            total_time: 0.0,
            protocol: None,
            faults: Vec::new(),
            errored: false,
            timed_out: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemTarget {
    pub address: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemResultData {
    #[serde(with = "chrono::serde::ts_microseconds")]
    pub start: DateTime<Utc>,
    pub expect: Option<ItemExpectation>,
    pub metrics: Option<ItemMetrics>, // Metrics collected
    pub faults: Vec<FaultConfiguration>,
    pub errors: Vec<ScenarioError>, // Errors encountered
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemResult {
    pub target: ItemTarget,
    pub results: Vec<ItemResultData>,
    pub requests_count: usize,
    pub failure_counts: usize,
    pub total_time: Duration,

    #[cfg(feature = "discovery")]
    #[serde(skip_serializing_if = "Option::is_none")]
    pub resources: Option<Vec<Resource>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenarioResult {
    pub scenario: Scenario,
    pub results: Vec<ItemResult>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScenariosResults {
    #[serde(with = "chrono::serde::ts_seconds")]
    pub start: DateTime<Utc>,

    #[serde(with = "chrono::serde::ts_seconds")]
    pub end: DateTime<Utc>,

    pub results: Vec<ScenarioResult>,
}

impl ScenariosResults {
    pub fn save(&self, path: &str) -> Result<(), ScenarioError> {
        let file = File::create(path).map_err(|e| {
            tracing::error!("Failed to create report file '{}': {}", path, e);
            ScenarioError::IoError(e.to_string())
        })?;
        let writer = BufWriter::new(file);

        if path.ends_with(".json") {
            serde_json::to_writer_pretty(writer, self).map_err(|e| {
                tracing::error!("Failed to serialize report to JSON: {}", e);
                ScenarioError::ReportError(e.to_string())
            })?;
        } else if path.ends_with(".yaml") || path.ends_with(".yml") {
            serde_yaml::to_writer(writer, self).map_err(|e| {
                tracing::error!("Failed to serialize report to YAML: {}", e);
                ScenarioError::ReportError(e.to_string())
            })?;
        } else {
            let err_msg = "Unsupported report file format. Use .json or .yaml"
                .to_string();
            tracing::error!("{}", err_msg);
            return Err(ScenarioError::ReportError(err_msg));
        }

        tracing::info!("Scenario results successfully saved to '{}'.", path);
        Ok(())
    }
}

impl ItemResult {
    pub fn latencies(&self) -> Vec<f64> {
        self.results
            .iter()
            .filter_map(|i| i.metrics.clone())
            .map(|m| m.total_time)
            .collect()
    }

    pub fn latency_percentile(
        &self,
        percent: f64,
        latencies: &Vec<f64>,
    ) -> LatencyPercentile {
        let n = latencies.len() as f64;
        let p = percent / 100.0;

        // R6 formula:
        //    h = (n + 1) * p
        let h = (n + 1.0) * p;
        let j = h.floor();
        let g = h - j;
        let j_i = j as isize; // may be 0 .. n+1

        let latency = match j_i {
            // if h <= 1, take the minimum
            j if j < 1 => latencies[0],
            // if h >= n, take the maximum
            j if j as usize >= latencies.len() => {
                latencies[latencies.len() - 1]
            }
            // otherwise interpolate between sorted[j-1] and sorted[j]
            _ => {
                let lo = latencies[(j_i - 1) as usize];
                let hi = latencies[j_i as usize];
                lo * (1.0 - g) + hi * g
            }
        };

        // count = ceil(h)
        let count = h.ceil().clamp(1.0, n).round() as usize;

        LatencyPercentile::new(percent, latency, count)
    }

    /// Inspired by Python statistics module
    /// Compute R-6 quantiles for p25, p50, p75, p95, p99 over the input slice.
    /// https://en.wikipedia.org/wiki/Quantile#Estimating_quantiles_from_a_sample
    /// Expects a sorted latencies array
    /// Returns a Vec of LatencyPercentile in ascending percentile order.
    pub fn latency_percentiles(
        &self,
        latencies: Vec<f64>,
    ) -> Vec<LatencyPercentile> {
        if latencies.is_empty() {
            return Vec::new();
        }

        let mut out = Vec::with_capacity(5);
        let targets = [25.0, 50.0, 75.0, 95.0, 99.0];

        for &perc in &targets {
            out.push(self.latency_percentile(perc, &latencies));
        }

        out
    }
}
