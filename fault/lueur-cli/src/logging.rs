use std::path::PathBuf;
use std::str::FromStr;
use std::sync::OnceLock;

use opentelemetry::KeyValue;
use opentelemetry::global;
use opentelemetry::trace::TracerProvider;
use opentelemetry_sdk::Resource;
use opentelemetry_sdk::metrics::MeterProviderBuilder;
use opentelemetry_sdk::metrics::PeriodicReader;
use opentelemetry_sdk::metrics::SdkMeterProvider;
use opentelemetry_sdk::trace::RandomIdGenerator;
use opentelemetry_sdk::trace::Sampler;
use opentelemetry_sdk::trace::SdkTracerProvider;
use opentelemetry_semantic_conventions::attribute::SERVICE_VERSION;
use tracing_appender::non_blocking::WorkerGuard;
use tracing_appender::rolling::never;
use tracing_log::LogTracer;
use tracing_opentelemetry::MetricsLayer;
use tracing_opentelemetry::OpenTelemetryLayer;
use tracing_subscriber::EnvFilter;
use tracing_subscriber::Layer;
use tracing_subscriber::Registry;
use tracing_subscriber::layer::SubscriberExt;

fn resource() -> Resource {
    static RESOURCE: OnceLock<Resource> = OnceLock::new();
    RESOURCE
        .get_or_init(|| {
            Resource::builder()
                .with_service_name(env!("CARGO_PKG_NAME"))
                .with_attribute(KeyValue::new(
                    SERVICE_VERSION,
                    env!("CARGO_PKG_VERSION"),
                ))
                .build()
        })
        .clone()
}

// Construct MeterProvider for MetricsLayer
pub fn init_meter_provider() -> SdkMeterProvider {
    let exporter = opentelemetry_otlp::MetricExporter::builder()
        .with_tonic()
        .with_temporality(opentelemetry_sdk::metrics::Temporality::default())
        .build()
        .unwrap();

    let reader = PeriodicReader::builder(exporter)
        .with_interval(std::time::Duration::from_secs(30))
        .build();

    // For debugging in development
    let stdout_reader = PeriodicReader::builder(
        opentelemetry_stdout::MetricExporter::default(),
    )
    .build();

    let meter_provider = MeterProviderBuilder::default()
        .with_resource(resource())
        .with_reader(reader)
        .with_reader(stdout_reader)
        .build();

    global::set_meter_provider(meter_provider.clone());

    meter_provider
}

// Construct TracerProvider for OpenTelemetryLayer
pub fn init_tracer_provider() -> SdkTracerProvider {
    let exporter = opentelemetry_otlp::SpanExporter::builder()
        .with_tonic()
        .build()
        .unwrap();

    SdkTracerProvider::builder()
        // Customize sampling strategy
        .with_sampler(Sampler::ParentBased(Box::new(
            Sampler::TraceIdRatioBased(1.0),
        )))
        .with_id_generator(RandomIdGenerator::default())
        .with_resource(resource())
        .with_batch_exporter(exporter)
        .build()
}

pub fn shutdown_tracer(
    tracer_provider: Option<SdkTracerProvider>,
    meter_provider: Option<SdkMeterProvider>,
) {
    if tracer_provider.is_some() {
        let provider = tracer_provider.unwrap();
        let _ = provider.force_flush();

        if let Err(err) = provider.shutdown() {
            eprintln!("{err:?}");
        }
    }

    if meter_provider.is_some() {
        let provider = meter_provider.unwrap();
        let _ = provider.force_flush();

        if let Err(err) = provider.shutdown() {
            eprintln!("{err:?}");
        }
    }
}

/// Combines logging and tracing/metrics layers into a single subscriber.
///
/// # Arguments
/// - `log_layers`: Layers for logging.
/// - `otel_layer`: Layer for OpenTelemetry tracing.
///
/// # Returns
/// A combined `tracing_subscriber` ready to be set as the global default.
pub fn init_subscriber(
    log_layers: Vec<Box<dyn tracing_subscriber::Layer<Registry> + Send + Sync>>,
    tracer_provider: &Option<SdkTracerProvider>,
    meter_provider: &Option<SdkMeterProvider>,
) -> Result<(), Box<dyn std::error::Error>> {
    //env_logger::init();

    let registry = tracing_subscriber::registry();

    let mut layers = Vec::new();
    layers.extend(log_layers);

    if tracer_provider.is_some() {
        let tracer = tracer_provider.clone().unwrap().tracer("fault");
        let telemetry = OpenTelemetryLayer::new(tracer)
            .with_error_records_to_exceptions(true);
        layers.push(Box::new(telemetry));
    }

    if meter_provider.is_some() {
        let provider = meter_provider.clone().unwrap();
        let metrics = MetricsLayer::new(provider.clone());
        layers.push(Box::new(metrics));
    }

    let subscriber = registry.with(layers);

    tracing::subscriber::set_global_default(subscriber)?;

    // required so the messages from the ebpf programs get logged properly
    LogTracer::init()?;

    Ok(())
}

/// Sets up file and stdout logging layers.
///
/// # Arguments
/// - `log_file`: Optional path to the log file.
/// - `enable_stdout`: Whether to log to stdout.
/// - `log_level`: The desired log level filter (e.g., "debug").
///
/// # Returns
/// A tuple containing optional guards for file and stdout logging layers.
#[allow(clippy::type_complexity)]
pub fn setup_logging(
    log_file: Option<String>,
    enable_stdout: bool,
    log_level: Option<String>,
) -> Result<
    (
        Option<WorkerGuard>,
        Option<WorkerGuard>,
        Vec<Box<dyn tracing_subscriber::Layer<Registry> + Send + Sync>>,
    ),
    Box<dyn std::error::Error>,
> {
    let mut fileguard: Option<WorkerGuard> = None;
    let mut stdoutguard: Option<WorkerGuard> = None;
    let mut layers = Vec::new();

    // fopr instance: "debug,tower_http=debug,otel::tracing=info"
    let log_level = log_level.unwrap_or_else(|| "info".to_string());

    if let Some(log_file) = log_file {
        let path = log_file.as_str();
        let pathbuf = PathBuf::from_str(path).unwrap();
        let file_appender =
            never(pathbuf.parent().unwrap(), pathbuf.file_name().unwrap());

        let (file_non_blocking, file_guard) =
            tracing_appender::non_blocking(file_appender);

        fileguard = Some(file_guard);

        let file_filter = EnvFilter::builder().parse_lossy(log_level.clone());

        let file_layer = tracing_subscriber::fmt::layer()
            .with_file(true)
            .with_line_number(true)
            .with_thread_ids(false)
            .with_target(true)
            .with_writer(file_non_blocking)
            .with_filter(file_filter)
            .boxed();

        layers.push(file_layer);
    }

    if enable_stdout {
        let (stdout_non_blocking, stdout_guard) =
            tracing_appender::non_blocking(std::io::stdout());

        let stdout_filter = EnvFilter::builder().parse_lossy(log_level.clone());

        stdoutguard = Some(stdout_guard);

        let stdout_layer = tracing_subscriber::fmt::layer()
            .compact()
            .with_file(true)
            .with_line_number(true)
            .with_thread_ids(false)
            .with_thread_names(false)
            .with_target(false)
            .with_writer(stdout_non_blocking)
            .with_filter(stdout_filter)
            .boxed();

        layers.push(stdout_layer);
    }

    Ok((fileguard, stdoutguard, layers))
}
