use std::collections::HashMap;
use std::error::Error;
use std::fmt::Write as FmtWrite;
use std::fs::File;
use std::io::BufWriter;
use std::time::Duration;

use chrono::DateTime;
use chrono::Utc;
use colorful::Color;
use colorful::Colorful;
use colorful::ExtraColorInterface;
use prettytable::Table;
use prettytable::row;
use serde::Deserialize;
use serde::Serialize;
use tera::Context;
use tera::Tera;
use tracing::error;

use crate::errors::ScenarioError;
use crate::event::FaultEvent;
use crate::plugin::RemotePluginInfo;
use crate::types::Direction;
use crate::types::FaultConfiguration;

// see https://github.com/serde-rs/serde/issues/1560#issuecomment-1666846833
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum ReportItemExpectationDecision {
    Success,
    Failure,
    #[serde(untagged)]
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReportItemHttpExpectation {
    pub status_code: Option<u16>,
    pub response_time_under: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReportItemHttpResult {
    pub status_code: Option<u16>,
    pub response_time: Option<f64>,
    pub decision: ReportItemExpectationDecision,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum ReportItemExpectation {
    Http {
        wanted: ReportItemHttpExpectation,
        got: Option<ReportItemHttpResult>,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReportItemFault {
    pub event: FaultEvent,
    pub direction: Direction,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReportItemEvent {
    pub event: FaultEvent,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum ReportItemProtocol {
    Http { code: u16, body_length: usize },
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ReportItemMetricsFaults {
    pub url: String,
    pub applied: Option<Vec<ReportItemEvent>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReportItemMetrics {
    pub dns: Vec<DnsTiming>,
    pub protocol: Option<ReportItemProtocol>,
    pub ttfb: f64,
    pub total_time: f64,
    pub faults: Vec<ReportItemMetricsFaults>,
}

impl ReportItemMetrics {
    pub fn new() -> Self {
        ReportItemMetrics {
            dns: Vec::new(),
            ttfb: 0.0,
            total_time: 0.0,
            protocol: None,
            faults: Vec::new(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DnsTiming {
    pub host: String,
    pub duration: f64,
    pub resolved: bool,
}

impl DnsTiming {
    pub fn new() -> Self {
        DnsTiming { host: "".to_string(), duration: 0.0, resolved: false }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReportItemTarget {
    pub address: String,
}

/// Report for a single entry in the scenario
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReportItemResult {
    pub target: ReportItemTarget,
    pub expect: Option<ReportItemExpectation>,
    pub metrics: Option<ReportItemMetrics>, // Metrics collected
    pub faults: Vec<FaultConfiguration>,
    pub errors: Vec<String>, // Errors encountered
    pub total_time: f64,     // Total time in milliseconds
}

/// Final Report for a single entry in the scenario
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReportItem {
    pub title: String,
    #[serde(with = "chrono::serde::ts_microseconds")]
    pub timestamp: DateTime<Utc>,
    pub target: ReportItemTarget,
    pub metrics: Option<ReportItemMetrics>, // Metrics collected
    pub expect: Option<ReportItemExpectation>,
    pub faults: Vec<FaultConfiguration>,
    pub errors: Vec<String>, // Errors encountered
    pub total_time: f64,     // Total time in milliseconds
}

impl ReportItem {
    pub fn new(
        title: String,
        metrics: Option<ReportItemMetrics>,
        result: ReportItemResult,
    ) -> Self {
        ReportItem {
            title: title,
            target: result.target,
            expect: result.expect,
            faults: result.faults,
            metrics,
            errors: result.errors,
            total_time: result.total_time,
            timestamp: Utc::now(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Report {
    pub plugins: Vec<RemotePluginInfo>,
    pub items: Vec<ReportItem>, // Scenario entries report
}

impl Report {
    /// Saves the ScenarioReport to the specified file path in JSON or YAML
    /// format based on file extension.
    ///
    /// # Arguments
    ///
    /// * `path` - The file path where the report should be saved.
    ///
    /// # Returns
    ///
    /// * `Result<(), ScenarioError>` - Returns `Ok(())` if successful, or a
    ///   `ScenarioError` otherwise.
    pub fn save(&self, path: &str) -> Result<(), ScenarioError> {
        let file = File::create(path).map_err(|e| {
            error!("Failed to create report file '{}': {}", path, e);
            ScenarioError::IoError(e)
        })?;
        let writer = BufWriter::new(file);

        if path.ends_with(".json") {
            serde_json::to_writer_pretty(writer, self).map_err(|e| {
                error!("Failed to serialize report to JSON: {}", e);
                ScenarioError::ReportError(e.to_string())
            })?;
        } else if path.ends_with(".yaml") || path.ends_with(".yml") {
            serde_yaml::to_writer(writer, self).map_err(|e| {
                error!("Failed to serialize report to YAML: {}", e);
                ScenarioError::ReportError(e.to_string())
            })?;
        } else {
            let err_msg = "Unsupported report file format. Use .json or .yaml"
                .to_string();
            error!("{}", err_msg);
            return Err(ScenarioError::ReportError(err_msg));
        }

        tracing::info!("Scenario results successfully saved to '{}'.", path);
        Ok(())
    }
}

/// Represents the generated report structured for serialization.
#[derive(Serialize)]
pub struct ReportOutput {
    #[serde(rename(serialize = "details"))]
    table: Vec<TableRow>,
    pub summary: Summary,
    fault_analysis: Vec<FaultAnalysisItem>,
    recommendations: Vec<String>,
}

/// Represents each row in the SLO Impact table.
#[derive(Serialize)]
struct TableRow {
    endpoint: String,
    total_faults: Vec<FaultConfiguration>,
    slo_99_200ms: SloResult,
    slo_95_500ms: SloResult,
    slo_90_1s: SloResult,
    slo_99_1_error: SloResult,
    slo_95_0_5_error: SloResult,
}

/// Represents the result of an SLO evaluation with detailed fields.
#[derive(Serialize, Deserialize, Debug)]
struct SloResult {
    status: String,
    breached: bool,
    breach_amount: Option<f64>,  // e.g., 50.0
    breach_unit: Option<String>, // e.g., "ms", "%"
    #[serde(serialize_with = "serialize_duration_as_milliseconds")]
    breach_time: Option<Duration>, // e.g., "5h 20m 0s/week"
    breach_reason: Option<String>, // e.g., "Error Rate"
}

/// Represents the summary section of the report.
#[derive(Serialize)]
pub struct Summary {
    pub total_tests: usize,
    pub total_failures: usize,
    pub failures_class: String,
}

/// Represents each item in the fault type analysis.
#[derive(Serialize)]
struct FaultAnalysisItem {
    fault_type: String,
    count: usize,
}

/// Trait to capitalize the first letter of a string.
trait Capitalize {
    fn capitalize(&self) -> String;
}

impl Capitalize for String {
    fn capitalize(&self) -> String {
        let mut c = self.chars();
        match c.next() {
            None => String::new(),
            Some(f) => f.to_uppercase().collect::<String>() + c.as_str(),
        }
    }
}

const SLO_METRICS: &[(&str, f64)] = &[
    ("slo_99_200ms", 200.0), // 99% < 200ms
    ("slo_95_500ms", 500.0), // 95% < 500ms
    ("slo_90_1s", 1000.0),   // 90% < 1s
];

const ERROR_RATE_SLOS: &[(&str, f64)] = &[
    ("slo_99_1_error", 1.0),   // 99% < 1% Error Rate
    ("slo_95_0_5_error", 0.5), // 95% < 0.5% Error Rate
];

pub enum OutputFormat {
    Markdown,
    Text,
    Html,
    Json,
    Yaml,
}

/// Generates the report in the specified format and returns it as a String.
///
/// # Arguments
///
/// * `report` - A reference to the Report struct containing test results.
/// * `format` - A reference to the OutputFormat enum specifying the desired
///   format.
///
/// # Returns
///
/// * A `Result<String, Box<dyn std::error::Error>>` containing the formatted
///   report.
pub fn pretty_report(
    report: &ReportOutput,
    format: &OutputFormat,
) -> Result<String, Box<dyn std::error::Error>> {
    match format {
        OutputFormat::Markdown => generate_markdown_report(report),
        OutputFormat::Text => generate_text_report(report),
        OutputFormat::Html => generate_html_report(report),
        OutputFormat::Json => generate_json_report(report),
        OutputFormat::Yaml => generate_yaml_report(report),
    }
}

/// Builds the ReportOutput struct from the raw Report data.
pub fn build_report_output(
    report: &Report,
) -> Result<ReportOutput, Box<dyn std::error::Error>> {
    let mut table_data = Vec::new();

    // Initialize counters for error rate calculations.
    let mut endpoint_request_counts: HashMap<String, usize> = HashMap::new();
    let mut endpoint_error_counts: HashMap<String, usize> = HashMap::new();

    // First pass to count total and error requests per endpoint.
    for item in &report.items {
        let endpoint = &item.target.address;
        *endpoint_request_counts.entry(endpoint.clone()).or_insert(0) += 1;
        match item.expect.as_ref().unwrap() {
            ReportItemExpectation::Http { wanted: _, got } => {
                if got.as_ref().unwrap().decision
                    == ReportItemExpectationDecision::Failure
                {
                    *endpoint_error_counts
                        .entry(endpoint.clone())
                        .or_insert(0) += 1;
                }
            }
        }
    }

    // Iterate over each test item to prepare table rows.
    for item in &report.items {
        let endpoint = &item.target.address;
        let _total_faults = summarize_faults(
            &item.faults,
            &item.metrics.as_ref().unwrap().faults,
        );

        // Evaluate latency-based SLOs.
        let mut slo_results = Vec::new();
        for &(_slo, threshold) in SLO_METRICS {
            let (status, breached, breach_info) =
                evaluate_latency_slo(item, threshold);
            slo_results.push((status, breached, breach_info));
        }

        // Evaluate error rate-based SLOs.
        let total_requests =
            *endpoint_request_counts.get(endpoint).unwrap_or(&0);
        let error_requests = *endpoint_error_counts.get(endpoint).unwrap_or(&0);
        for &(slo, threshold) in ERROR_RATE_SLOS {
            let (status, breached, breach_info) = evaluate_error_rate_slo(
                item,
                threshold,
                total_requests,
                error_requests,
            );
            slo_results.push((status, breached, breach_info));
        }

        // Map SLO results to respective fields.
        let row = TableRow {
            endpoint: endpoint.clone(),
            total_faults: item.faults.clone(),
            slo_99_200ms: match &slo_results[0].2 {
                Some(breach) => SloResult {
                    status: slo_results[0].0.clone(),
                    breached: slo_results[0].1,
                    breach_amount: Some(breach.amount),
                    breach_unit: Some(breach.unit.clone()),
                    breach_time: Some(breach.time),
                    breach_reason: None, // Add if applicable
                },
                None => SloResult {
                    status: slo_results[0].0.clone(),
                    breached: slo_results[0].1,
                    breach_amount: None,
                    breach_unit: None,
                    breach_time: None,
                    breach_reason: None,
                },
            },
            slo_95_500ms: match &slo_results[1].2 {
                Some(breach) => SloResult {
                    status: slo_results[1].0.clone(),
                    breached: slo_results[0].1,
                    breach_amount: Some(breach.amount),
                    breach_unit: Some(breach.unit.clone()),
                    breach_time: Some(breach.time),
                    breach_reason: None,
                },
                None => SloResult {
                    status: slo_results[1].0.clone(),
                    breached: slo_results[0].1,
                    breach_amount: None,
                    breach_unit: None,
                    breach_time: None,
                    breach_reason: None,
                },
            },
            slo_90_1s: match &slo_results[2].2 {
                Some(breach) => SloResult {
                    status: slo_results[2].0.clone(),
                    breached: slo_results[0].1,
                    breach_amount: Some(breach.amount),
                    breach_unit: Some(breach.unit.clone()),
                    breach_time: Some(breach.time),
                    breach_reason: None,
                },
                None => SloResult {
                    status: slo_results[2].0.clone(),
                    breached: slo_results[0].1,
                    breach_amount: None,
                    breach_unit: None,
                    breach_time: None,
                    breach_reason: None,
                },
            },
            slo_99_1_error: match &slo_results[3].2 {
                Some(breach) => SloResult {
                    status: slo_results[3].0.clone(),
                    breached: slo_results[0].1,
                    breach_amount: Some(breach.amount),
                    breach_unit: Some(breach.unit.clone()),
                    breach_time: Some(breach.time),
                    breach_reason: Some("Error Rate".to_string()),
                },
                None => SloResult {
                    status: slo_results[3].0.clone(),
                    breached: slo_results[0].1,
                    breach_amount: None,
                    breach_unit: None,
                    breach_time: None,
                    breach_reason: Some("Error Rate".to_string()),
                },
            },
            slo_95_0_5_error: match &slo_results[4].2 {
                Some(breach) => SloResult {
                    status: slo_results[4].0.clone(),
                    breached: slo_results[0].1,
                    breach_amount: Some(breach.amount),
                    breach_unit: Some(breach.unit.clone()),
                    breach_time: Some(breach.time),
                    breach_reason: Some("Error Rate".to_string()),
                },
                None => SloResult {
                    status: slo_results[4].0.clone(),
                    breached: slo_results[0].1,
                    breach_amount: None,
                    breach_unit: None,
                    breach_time: None,
                    breach_reason: Some("Error Rate".to_string()),
                },
            },
        };

        table_data.push(row);
    }

    let summary = generate_summary(report)?;
    let fault_analysis = analyze_fault_types(report)?;
    let recommendations = generate_fault_recommendations(report);

    Ok(ReportOutput {
        table: table_data,
        summary,
        fault_analysis,
        recommendations,
    })
}

/// Formats the summary section for Markdown output.
fn format_summary_markdown(summary: &Summary) -> String {
    let mut summary_md = String::new();
    writeln!(summary_md, "## Summary").unwrap();
    writeln!(
        summary_md,
        "- **Total Test Cases:** {}",
        summary.total_tests.to_string().cyan().bold()
    )
    .unwrap();
    writeln!(
        summary_md,
        "- **Failures:** {}",
        summary.total_failures.to_string().red().bold()
    )
    .unwrap();

    if summary.total_failures > 0 {
        writeln!(
            summary_md,
            "- {}: Investigate the failed test cases to enhance your application's resilience.",
            "🔍 Recommendation".yellow().bold()
        )
        .unwrap();
    } else {
        writeln!(
            summary_md,
            "- {}: Excellent job! All test cases passed successfully.",
            "🌟 Recommendation".green().bold()
        )
        .unwrap();
    }

    summary_md
}

/// Formats the fault type analysis section for Markdown output.
fn format_fault_analysis_markdown(
    fault_analysis: &Vec<FaultAnalysisItem>,
) -> String {
    let mut analysis_md = String::new();
    writeln!(analysis_md, "## Fault Type Analysis").unwrap();
    for fault in fault_analysis {
        writeln!(
            analysis_md,
            "- **{}** occurred {} times.",
            fault.fault_type.capitalize(),
            fault.count
        )
        .unwrap();
    }
    analysis_md
}

fn generate_markdown_report(
    report_output: &ReportOutput,
) -> Result<String, Box<dyn std::error::Error>> {
    let mut markdown: String = String::new();

    // Add Report Title
    writeln!(markdown, "# Lueur Resilience Test Report\n")?;

    // Add SLO Impact Table Header
    writeln!(
        markdown,
        "| **Endpoint** | **Total Fault Injected** | **SLO: 99% < 200ms** | **SLO: 95% < 500ms** | **SLO: 90% < 1s** | **SLO: 99% < 1% Error Rate** | **SLO: 95% < 0.5% Error Rate** |"
    )?;
    writeln!(
        markdown,
        "|-------------|--------------------------|-----------------------|-----------------------|-----------------------|----------------------------------|-----------------------------------|"
    )?;

    // Iterate over each table row to generate Markdown table rows.
    for row in &report_output.table {
        writeln!(
            markdown,
            "| `{}` | {} | {} | {} | {} | {} | {} |",
            row.endpoint,
            format_faults_markdown(&row.total_faults),
            format_slo_markdown(&row.slo_99_200ms),
            format_slo_markdown(&row.slo_95_500ms),
            format_slo_markdown(&row.slo_90_1s),
            format_slo_markdown(&row.slo_99_1_error),
            format_slo_markdown(&row.slo_95_0_5_error),
        )?;
    }

    // Add Aggregated Summary
    writeln!(markdown, "{}", format_summary_markdown(&report_output.summary))?;

    // Add Fault Type Analysis
    writeln!(
        markdown,
        "{}",
        format_fault_analysis_markdown(&report_output.fault_analysis)
    )?;

    // Add Recommendations
    writeln!(markdown, "\n## Recommendations")?;
    for rec in &report_output.recommendations {
        writeln!(markdown, "- {}", rec)?;
    }

    Ok(markdown)
}

fn format_faults_markdown(faults: &Vec<FaultConfiguration>) -> String {
    let mut list = String::new();

    for f in faults {
        list.push_str(format!("- {}", f).as_str());
    }

    list
}

/// Formats an SLO result for Markdown output.
fn format_slo_markdown(slo: &SloResult) -> String {
    if !slo.breached {
        "✅".to_string()
    } else {
        let amount = slo.breach_amount.unwrap_or(0.0);
        let unit = slo.breach_unit.clone().unwrap_or_default();
        let time = slo.breach_time.map_or("".to_string(), format_duration);
        format!("❌ (+{:.1}{}), {}", amount, unit, time)
    }
}

fn generate_text_report(
    report_output: &ReportOutput,
) -> Result<String, Box<dyn Error>> {
    let mut text: String = String::new();

    // Initialize PrettyTable.
    let mut table = Table::new();
    table.set_titles(row![
        "Endpoint",
        "Total Fault Injected",
        "SLO: 99% < 200ms",
        "SLO: 95% < 500ms",
        "SLO: 90% < 1s",
        "SLO: 99% < 1% Error Rate",
        "SLO: 95% < 0.5% Error Rate"
    ]);
    table.set_format(
        *prettytable::format::consts::FORMAT_NO_BORDER_LINE_SEPARATOR,
    );

    // Iterate over each table row to populate PrettyTable.
    for row in &report_output.table {
        table.add_row(row![
            format!("`{}`", row.endpoint),
            format_faults_text(&row.total_faults),
            format_slo_text(&row.slo_99_200ms),
            format_slo_text(&row.slo_95_500ms),
            format_slo_text(&row.slo_90_1s),
            format_slo_text(&row.slo_99_1_error),
            format_slo_text(&row.slo_95_0_5_error),
        ]);
    }

    // Render the table to a string.
    let table_string = table.to_string();
    text.push_str(&table_string);

    // Add Aggregated Summary
    text.push_str(&format_summary_text(&report_output.summary));

    // Add Fault Type Analysis
    text.push_str(&format_fault_analysis_text(&report_output.fault_analysis));

    // Add Recommendations
    text.push_str("\n## Recommendations\n");
    for rec in &report_output.recommendations {
        writeln!(text, "- {}", rec)?;
    }

    Ok(text)
}

fn format_faults_text(faults: &Vec<FaultConfiguration>) -> String {
    format_faults_markdown(faults)
}

/// Formats an SLO result for Text output.
fn format_slo_text(slo: &SloResult) -> String {
    format_slo_markdown(slo)
}

/// Formats the summary section for Text output.
fn format_summary_text(summary: &Summary) -> String {
    let mut summary_txt = String::new();
    writeln!(summary_txt, "\n## Summary").unwrap();
    writeln!(
        summary_txt,
        "- **Total Test Cases:** {}",
        summary.total_tests.to_string().cyan().bold()
    )
    .unwrap();
    writeln!(
        summary_txt,
        "- **Failures:** {}",
        summary.total_failures.to_string().red().bold()
    )
    .unwrap();

    if summary.total_failures > 0 {
        writeln!(
            summary_txt,
            "- {}: Investigate the failed test cases to enhance your application's resilience.",
            "🔍 Recommendation".yellow().bold()
        )
        .unwrap();
    } else {
        writeln!(
            summary_txt,
            "- {}: Excellent job! All test cases passed successfully.",
            "🌟 Recommendation".green().bold()
        )
        .unwrap();
    }

    summary_txt
}

/// Formats the fault type analysis section for Text output.
fn format_fault_analysis_text(
    fault_analysis: &Vec<FaultAnalysisItem>,
) -> String {
    let mut analysis_txt = String::new();
    writeln!(analysis_txt, "\n## Fault Type Analysis").unwrap();
    for fault in fault_analysis {
        writeln!(
            analysis_txt,
            "- **{}** occurred {} times.",
            fault.fault_type.capitalize(),
            fault.count
        )
        .unwrap();
    }
    analysis_txt
}
fn generate_html_report(
    report_output: &ReportOutput,
) -> Result<String, Box<dyn Error>> {
    // Initialize Tera with an in-memory template.
    let mut tera = Tera::default();

    // Create Tera context.
    let mut context = Context::new();
    context.insert("summary", &report_output.summary);
    context.insert("fault_analysis", &report_output.fault_analysis);
    context.insert("recommendations", &report_output.recommendations);

    // Prepare formatted table data.
    let mut formatted_table = Vec::new();
    for row in &report_output.table {
        formatted_table.push(FormattedHtmlTableRow {
            endpoint: row.endpoint.clone(),
            total_faults: format_faults_html(&row.total_faults),
            slo_99_200ms: format_slo_html(&row.slo_99_200ms),
            slo_95_500ms: format_slo_html(&row.slo_95_500ms),
            slo_90_1s: format_slo_html(&row.slo_90_1s),
            slo_99_1_error: format_slo_html(&row.slo_99_1_error),
            slo_95_0_5_error: format_slo_html(&row.slo_95_0_5_error),
        });
    }

    // Insert the formatted table into the context.
    context.insert("formatted_table", &formatted_table);

    // Render the template.
    let rendered = tera.render_str(r#"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lueur Resilience Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }
        th { background-color: #f2f2f2; }
        .met { color: green; }
        .breached { color: red; }
        .recommendation { font-weight: bold; }
    </style>
</head>
<body>
    <h1>Lueur Resilience Test Report</h1>

    <table>
        <thead>
            <tr>
                <th>Endpoint</th>
                <th>Total Fault Injected</th>
                <th>SLO: 99% &lt; 200ms</th>
                <th>SLO: 95% &lt; 500ms</th>
                <th>SLO: 90% &lt; 1s</th>
                <th>SLO: 99% &lt; 1% Error Rate</th>
                <th>SLO: 95% &lt; 0.5% Error Rate</th>
            </tr>
        </thead>
        <tbody>
            {% for row in formatted_table %}
            <tr>
                <td><code>{{ row.endpoint }}</code></td>
                <td>
                    <ul>
                    {% for fault in formatted_table.total_faults %}
                        <li>{{ fault }}</li>
                    {% endfor %}
                    </ul>
                </td>
                <td class="{{ row.slo_99_200ms.class }}">{{ row.slo_99_200ms.formatted }}</td>
                <td class="{{ row.slo_95_500ms.class }}">{{ row.slo_95_500ms.formatted }}</td>
                <td class="{{ row.slo_90_1s.class }}">{{ row.slo_90_1s.formatted }}</td>
                <td class="{{ row.slo_99_1_error.class }}">{{ row.slo_99_1_error.formatted }}</td>
                <td class="{{ row.slo_95_0_5_error.class }}">{{ row.slo_95_0_5_error.formatted }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <h2>Summary</h2>
    <ul>
        <li><strong>Total Test Cases:</strong> {{ summary.total_tests }}</li>
        <li><strong>Failures:</strong> <span class="{{ summary.failures_class }}">{{ summary.total_failures }}</span></li>
        {% if summary.total_failures > 0 %}
            <li class="recommendation">🔍 Recommendation: Investigate the failed test cases to enhance your application's resilience.</li>
        {% else %}
            <li class="recommendation">🌟 Recommendation: Excellent job! All test cases passed successfully.</li>
        {% endif %}
    </ul>

    <h2>Fault Type Analysis</h2>
    <ul>
        {% for fault in fault_analysis %}
            <li><strong>{{ fault.fault_type }}</strong> occurred {{ fault.count }} times.</li>
        {% endfor %}
    </ul>

    <h2>Recommendations</h2>
    <ul>
        {% for rec in recommendations %}
            <li class="recommendation">{{ rec }}</li>
        {% endfor %}
    </ul>
</body>
</html>
"#, &context)?;

    Ok(rendered)
}

/// Represents a formatted table row for HTML output.
#[derive(Serialize, Deserialize, Debug)]
struct FormattedHtmlTableRow {
    endpoint: String,
    total_faults: Vec<String>,
    slo_99_200ms: FormattedHtmlSlo,
    slo_95_500ms: FormattedHtmlSlo,
    slo_90_1s: FormattedHtmlSlo,
    slo_99_1_error: FormattedHtmlSlo,
    slo_95_0_5_error: FormattedHtmlSlo,
}

/// Represents the formatted SLO result for HTML output.
#[derive(Serialize, Deserialize, Debug)]
struct FormattedHtmlSlo {
    class: String,     // e.g., "met" or "breached"
    formatted: String, // e.g., "✅" or "❌ (+50.0ms), 0h 0m 0.1s"
}

fn format_faults_html(faults: &Vec<FaultConfiguration>) -> Vec<String> {
    let mut list = Vec::new();

    for f in faults {
        list.push(format!("{}", f));
    }

    list
}

/// Formats an SLO result for HTML output with both class and formatted string.
fn format_slo_html(slo: &SloResult) -> FormattedHtmlSlo {
    if !slo.breached {
        FormattedHtmlSlo {
            class: "met".to_string(),
            formatted: "✅".to_string(),
        }
    } else {
        let amount = slo.breach_amount.unwrap_or(0.0);
        let unit = slo.breach_unit.clone().unwrap_or_default();
        let time = slo.breach_time.map_or("".to_string(), format_duration);
        FormattedHtmlSlo {
            class: "breached".to_string(),
            formatted: format!("❌ (+{:.1}{}), {}", amount, unit, time),
        }
    }
}

/// Summarizes all faults injected into an endpoint into a single string.
fn summarize_faults(
    faults: &Vec<FaultConfiguration>,
    _faults_applied: &[ReportItemMetricsFaults],
) -> Vec<String> {
    let mut summary = Vec::new();

    for fault in faults {
        summary.push(format!("{}", fault));
    }

    /*
    // Additional faults.
    for applied_fault in faults_applied {
        let event_type = &applied_fault.computed.event.event_type;
        let delay = applied_fault.computed.event.delay;
        summary.push_str(&format!(
            "; {}: {:.0}{}",
            event_type,
            delay,
            match event_type.to_lowercase().as_str() {
                "bandwidth" => "kbps",
                "packet loss" => "%",
                "jitter" => "ms",
                "latency" => "ms",
                "http errors" => "",
                _ => "",
            }
        ));
    }*/

    summary
}

/// Represents breach details.
struct BreachInfo {
    amount: f64,
    unit: String,
    time: Duration,
    breached_requests: usize,
}

/// Evaluates latency-based SLOs and returns the status and breach details.
fn evaluate_latency_slo(
    item: &ReportItem,
    threshold: f64,
) -> (String, bool, Option<BreachInfo>) {
    match &item.expect {
        Some(expectation) => {
            match expectation {
                ReportItemExpectation::Http { wanted: _, got } => {
                    match got {
                        Some(result) => {
                            let actual_response_time =
                                result.response_time.unwrap_or(0.0);
                            let decision = &result.decision;
                            let breach_amount =
                                actual_response_time - threshold;

                            if decision
                                == &ReportItemExpectationDecision::Success
                            {
                                (format!("{}", "✅".green()), false, None)
                            } else {
                                // Assume each 'failure' corresponds to one
                                // breached request.
                                let breached_requests = 1; // This should be derived from actual data if available
                                let breach_time = estimate_breach_time(
                                    breached_requests,
                                    breach_amount,
                                );
                                (
                                    format!("{}", "❌".red()),
                                    true,
                                    Some(BreachInfo {
                                        amount: breach_amount,
                                        unit: "ms".to_string(),
                                        time: breach_time,
                                        breached_requests,
                                    }),
                                )
                            }
                        }
                        None => ("".to_string(), false, None),
                    }
                }
            }
        }
        None => ("".to_string(), false, None),
    }
}

/// Evaluates error rate-based SLOs and returns the status and breach details.
fn evaluate_error_rate_slo(
    _item: &ReportItem,
    threshold: f64,
    total_requests: usize,
    error_requests: usize,
) -> (String, bool, Option<BreachInfo>) {
    let error_rate = if total_requests > 0 {
        (error_requests as f64 / total_requests as f64) * 100.0
    } else {
        0.0
    };
    let breach_amount = error_rate - threshold;

    if error_rate <= threshold {
        (format!("{}", "✅".green()), false, None)
    } else {
        // Calculate breached requests based on excess error rate.
        let breached_requests = ((error_rate - threshold) / 100.0
            * total_requests as f64)
            .round() as usize;
        let breach_time =
            estimate_breach_time(breached_requests, breach_amount);
        (
            format!("{}", "❌".red()),
            true,
            Some(BreachInfo {
                amount: breach_amount,
                unit: "%".to_string(),
                time: breach_time,
                breached_requests,
            }),
        )
    }
}

fn estimate_breach_time(breached_requests: usize, delta: f64) -> Duration {
    // Calculate total breach time in seconds.
    let breach_seconds = breached_requests as f64 * (delta / 1000.0); // converting ms to seconds

    // Maximum breach time is the total monitoring window (1 week).
    let max_breach_seconds = 7.0 * 24.0 * 60.0 * 60.0; // 604800 seconds

    // Cap breach_seconds to max_breach_seconds.
    let breach_seconds = breach_seconds.max(0.0).min(max_breach_seconds);

    Duration::from_secs_f64(breach_seconds)
}

/// Generates and prints an aggregated summary of the test results.
fn generate_summary(
    report: &Report,
) -> Result<Summary, Box<dyn std::error::Error>> {
    let total_tests = report.items.len();
    let total_failures = report
        .items
        .iter()
        .filter(|item| match item.expect.as_ref().unwrap() {
            ReportItemExpectation::Http { wanted: _, got } => {
                let decision = &got.as_ref().unwrap().decision;
                decision == &ReportItemExpectationDecision::Failure
            }
        })
        .count();

    let failures_class = if total_failures > 0 {
        "breached".to_string()
    } else {
        "met".to_string()
    };

    Ok(Summary { total_tests, total_failures, failures_class })
}

/// Analyzes and counts the occurrences of each fault type.
fn analyze_fault_types(
    report: &Report,
) -> Result<Vec<FaultAnalysisItem>, Box<dyn std::error::Error>> {
    let fault_counts = HashMap::new();

    for _item in &report.items {
        /*let primary_fault = item.faults.fault_type();
        *fault_counts.entry(primary_fault).or_insert(0) += 1;


        for fault_detail in &item.metrics.as_ref().unwrap().faults {
            let additional_fault =
                fault_detail.computed.as_ref().unwrap().event.event_type();
            *fault_counts.entry(additional_fault).or_insert(0) += 1;
        }
        */
    }

    let mut fault_analysis = Vec::new();
    for (fault_type, count) in fault_counts {
        fault_analysis.push(FaultAnalysisItem { fault_type, count });
    }

    Ok(fault_analysis)
}

/// Generates and returns fault-based recommendations based on fault type
/// frequencies.
fn generate_fault_recommendations(report: &Report) -> Vec<String> {
    let fault_counts =
        analyze_fault_types(report).unwrap_or_else(|_| Vec::new());
    let mut recommendations = Vec::new();

    for fault in fault_counts {
        match fault.fault_type.as_str() {
            "latency" if fault.count > 3 => {
                recommendations.push(format!(
                    "{}: High latency issues detected frequently. Consider optimizing network calls or improving service scalability.",
                    "🔧 Recommendation".yellow().bold()
                ));
            }
            "packet loss" if fault.count > 1 => {
                recommendations.push(format!(
                    "{}: Packet loss observed in multiple endpoints. Investigate network stability and routing paths.",
                    "🔧 Recommendation".yellow().bold()
                ));
            }
            "http errors" if fault.count > 1 => {
                recommendations.push(format!(
                    "{}: Frequent HTTP errors detected. Review error handling and server configurations.",
                    "🔧 Recommendation".yellow().bold()
                ));
            }
            "bandwidth" if fault.count > 2 => {
                recommendations.push(format!(
                    "{}: Bandwidth limitations impacting multiple endpoints. Consider upgrading network infrastructure or optimizing data transfer.",
                    "🔧 Recommendation".yellow().bold()
                ));
            }
            "jitter" if fault.count > 2 => {
                recommendations.push(format!(
                    "{}: Jitter affecting endpoint performance. Implement measures to stabilize network latency.",
                    "🔧 Recommendation".yellow().bold()
                ));
            }
            _ => {}
        }
    }

    if recommendations.is_empty() {
        recommendations.push(
            "No specific recommendations based on fault types.".to_string(),
        );
    }

    recommendations
}

/// Generates a JSON-formatted report.
fn generate_json_report(
    report_output: &ReportOutput,
) -> Result<String, Box<dyn std::error::Error>> {
    let json = serde_json::to_string_pretty(report_output)?;
    Ok(json)
}

/// Generates a YAML-formatted report.
fn generate_yaml_report(
    report_output: &ReportOutput,
) -> Result<String, Box<dyn std::error::Error>> {
    let yaml = serde_yaml::to_string(report_output)?;
    Ok(yaml)
}

/// Serializes `Duration` to float milliseconds (e.g., 5.33).
fn serialize_duration_as_milliseconds<S>(
    duration: &Option<Duration>,
    serializer: S,
) -> Result<S::Ok, S::Error>
where
    S: serde::Serializer,
{
    match duration {
        Some(dur) => {
            let milliseconds = dur.as_millis_f64();
            serializer.serialize_f64(milliseconds)
        }
        None => serializer.serialize_none(),
    }
}

/// Formats `Duration` into a human-readable string (e.g., "5h 20m 0.1s").
fn format_duration(dur: Duration) -> String {
    let hours = dur.as_secs() / 3600;
    let minutes = (dur.as_secs() % 3600) / 60;
    let seconds = dur.as_secs() % 60;
    let nanos = dur.subsec_nanos();
    if nanos > 0 {
        format!(
            "{}h {}m {:.1}s",
            hours,
            minutes,
            dur.as_secs_f64() - hours as f64 * 3600.0 - minutes as f64 * 60.0
        )
    } else {
        format!("{}h {}m {}s", hours, minutes, seconds)
    }
}
