use axum::Json;
use axum::body::Body;
use axum::http;
use axum::response::IntoResponse;
use axum::response::Response;
use hyper::StatusCode;
use serde::Deserialize;
use serde::Serialize;
use serde_json::json;
use thiserror::Error;
use tonic::Status;

#[derive(Error, Debug)]
pub enum DemoError {}

#[derive(Error, Debug)]
pub enum ProxyError {
    #[error("Invalid configuration: {0}")]
    InvalidConfiguration(String),

    #[error("Network error: {0}")]
    NetworkError(#[from] reqwest::Error),

    #[error("Hyper error: {0}")]
    HyperError(#[from] hyper::Error),

    #[error("Axum error: {0}")]
    AxumError(#[from] axum::http::Error),

    #[error("HttpHeaderNameError error: {0}")]
    HttpHeaderNameError(#[from] http::header::InvalidHeaderName),

    #[error("HttpHeaderValueError error: {0}")]
    HttpHeaderValueError(#[from] http::header::InvalidHeaderValue),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("gRPC error: {0}")]
    GrpcError(#[from] tonic::Status),

    #[error("aborting processing now")]
    GrpcAbort(Response<Vec<u8>>),

    #[error("RPC call error to '{0}' during '{1}': {2}")]
    RpcCallError(String, String, Status),

    #[error("RPC connection error to '{0}': {1}")]
    RpcConnectionError(String, String),

    /// Represents invalid request errors.
    #[error("Invalid request: {0}")]
    InvalidRequest(String),

    #[error("Other error: {0}")]
    Other(String),

    #[error("Internal error: {0}")]
    Internal(String),

    #[error("rust tls error: {0}")]
    TlsError(#[from] tokio_rustls::rustls::Error),
}

impl IntoResponse for ProxyError {
    fn into_response(self) -> Response<Body> {
        // Define the status code and error message based on the error variant
        let (status, error_message) = match self {
            ProxyError::InvalidConfiguration(msg) => (
                StatusCode::BAD_REQUEST,
                json!({ "error": format!("Invalid Configuration: {}", msg) }),
            ),
            ProxyError::NetworkError(err) => (
                StatusCode::BAD_GATEWAY,
                json!({ "error": format!("Network Error: {}", err) }),
            ),
            ProxyError::HyperError(err) => (
                StatusCode::BAD_GATEWAY,
                json!({ "error": format!("Hyper Error: {}", err) }),
            ),
            ProxyError::IoError(err) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                json!({ "error": format!("IO Error: {}", err) }),
            ),
            ProxyError::GrpcError(err) => (
                StatusCode::BAD_GATEWAY,
                json!({ "error": format!("gRPC Error: {}", err) }),
            ),
            ProxyError::RpcCallError(plugin, method, msg) => (
                StatusCode::BAD_REQUEST,
                json!({
                    "error": format!("RPC Call Error in plugin '{}', method '{}': {}", plugin, method, msg)
                }),
            ),
            ProxyError::RpcConnectionError(plugin, msg) => (
                StatusCode::BAD_GATEWAY,
                json!({
                    "error": format!("RPC Connection Error to plugin '{}': {}", plugin, msg)
                }),
            ),
            ProxyError::InvalidRequest(msg) => (
                StatusCode::BAD_REQUEST,
                json!({ "error": format!("Invalid Request: {}", msg) }),
            ),
            ProxyError::Other(msg) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                json!({ "error": format!("Other Error: {}", msg) }),
            ),
            ProxyError::Internal(msg) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                json!({ "error": format!("Internal Server Error: {}", msg) }),
            ),
            ProxyError::HttpHeaderNameError(invalid_header_name) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                json!({ "error": format!("Invalid HTTP header name: {}", invalid_header_name) }),
            ),
            ProxyError::HttpHeaderValueError(invalid_header_value) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                json!({ "error": format!("Invalid HTTP header value: {}", invalid_header_value) }),
            ),
            ProxyError::AxumError(..) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                json!({ "error": format!("Invalid Axum body value") }),
            ),
            ProxyError::GrpcAbort(..) => todo!(),
            ProxyError::TlsError(error) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                json!({ "error": format!("Tls error") }),
            ),
        };

        // Convert the JSON error message and status code into a response
        (status, Json(error_message)).into_response()
    }
}

#[cfg(feature = "scenario")]
#[derive(Clone, Error, Debug, Serialize, Deserialize)]
pub enum ScenarioError {
    #[error("IO error: {0}")]
    IoError(String),

    #[error("Report error: {0}")]
    ReportError(String),

    #[error("Failed to read file {0}: {1}")]
    ReadError(String, String),

    #[error("Failed to parse YAML in file {0}: {1}")]
    ParseError(String, String),

    #[error("WalkDir error: {0}")]
    WalkDirError(String),

    #[error("Invalid HTTP method header: {0}")]
    HTTPMethodError(String),

    #[error("HTTP error: {0}")]
    HTTPError(String),

    #[error("Missing OpenAPI version")]
    MissingOpenAPIVersion(),

    #[error("Unsupported OpenAPI version: {0}")]
    UnsupportedOpenAPIVersion(String),

    #[error("Failed to parse OpenAPI: {0}")]
    OpenAPIParsingError(String),

    #[error("Expected a directory to store multiple scenarios")]
    ExpectedDirectoryError(),
}

#[derive(Error, Debug)]
pub enum SchedulingError {
    #[error(
        "Fraction-based time spec ('{0}') used but no --duration provided.\nHint: Please specify a duration (e.g., --duration=10s) when using fraction-based time specs."
    )]
    MissingDuration(String),

    #[error(
        "Unknown key ('{0}') used in schedule.\nHint: Only `start` and `duration` are allowed."
    )]
    UnknownKey(String),

    #[error("Time spec ('{0}') could not be parsed.")]
    FailedParsing(String),

    #[error("Invalid time fraction ('{0}') in time spec.")]
    InvalidFraction(String),
}

#[derive(Error, Debug)]
pub enum SuggestionError {
    #[error("Invalid diff hunk: {0}")]
    InvalidHunk(String),

    #[error("Failed to retrieve: {0}")]
    Retrieval(String),
}

#[derive(Error, Debug)]
pub enum APIServiceError {}
