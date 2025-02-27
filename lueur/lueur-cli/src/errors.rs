use axum::Json;
use axum::response::IntoResponse;
use axum::response::Response;
use hyper::StatusCode;
use serde_json::json;
use thiserror::Error;

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

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("gRPC error: {0}")]
    GrpcError(#[from] tonic::Status),

    #[error("RPC call error to '{0}' during '{1}': {2}")]
    RpcCallError(String, String, String),

    #[error("RPC connection error to '{0}': {1}")]
    RpcConnectionError(String, String),

    /// Represents invalid request errors.
    #[error("Invalid request: {0}")]
    InvalidRequest(String),

    #[error("Other error: {0}")]
    Other(String),

    #[error("Internal error: {0}")]
    Internal(String),
}

impl IntoResponse for ProxyError {
    fn into_response(self) -> Response {
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
        };

        // Convert the JSON error message and status code into a response
        (status, Json(error_message)).into_response()
    }
}

#[derive(Error, Debug)]
pub enum ScenarioError {
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("Report error: {0}")]
    ReportError(String),

    #[error("Request error: {0}")]
    UriParseError(#[from] url::ParseError),

    #[error("Failed to read file {0}: {1}")]
    ReadError(String, #[source] std::io::Error),

    #[error("Failed to parse YAML in file {0}: {1}")]
    ParseError(String, #[source] serde_yaml::Error),

    #[error("WalkDir error: {0}")]
    WalkDirError(String),
}
