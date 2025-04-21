use super::types::Report;
use super::types::ReportFormat;

pub(crate) mod markdown;

pub fn render(report: &Report, format: ReportFormat) -> String {
    match format {
        ReportFormat::Text => todo!(),
        ReportFormat::Markdown => markdown::render(report),
        ReportFormat::Html => todo!(),
        ReportFormat::Json => todo!(),
        ReportFormat::Yaml => todo!(),
    }
}
