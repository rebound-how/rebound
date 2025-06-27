use std::net::IpAddr;
use std::net::SocketAddr;
use std::time::Instant;

use anyhow::Result;
use axum::Router;
use axum::body::Body;
use axum::extract::Json;
use axum::extract::Request;
use axum::middleware;
use axum::response::Response;
use axum::routing::post;
use axum_tracing_opentelemetry::middleware::OtelAxumLayer;
use axum_tracing_opentelemetry::middleware::OtelInResponseLayer;
use http::StatusCode;
use local_ip_address::local_ip;
use serde::Deserialize;
use serde::Serialize;
use tower::ServiceBuilder;
use tower_http::trace::TraceLayer;

use crate::errors::APIServiceError;
#[cfg(all(feature = "injection", feature = "scenario"))]
use crate::inject::event::EventLifecycle;
#[cfg(feature = "scenario")]
use crate::scenario::types::ItemResult;

pub fn get_api_service_address(api_addr: &Option<String>) -> Result<String> {
    if let Some(addr) = api_addr {
        let socket_addr: SocketAddr = addr.parse()?;
        let mut sock_proxy_ip = socket_addr.ip();
        let proxy_port = socket_addr.port();

        if sock_proxy_ip.is_unspecified() {
            sock_proxy_ip = local_ip()?;
        }

        Ok(format!("{}:{}", sock_proxy_ip.to_string(), proxy_port))
    } else {
        let sock_proxy_ip = local_ip()?;
        Ok(format!("{}:7900", sock_proxy_ip.to_string()))
    }
}

pub async fn run(
    address: String,
    shutdown_rx: kanal::AsyncReceiver<()>,
) -> Result<(), APIServiceError> {
    let mut router = Router::new();
    #[cfg(feature = "scenario")]
    {
        router = router.route("/scenario/results", post(new_results));
    }
    #[cfg(all(feature = "injection", feature = "scenario"))]
    {
        router = router.route("/injection/events", post(new_event));
    }
    router = router.layer(OtelInResponseLayer);
    router = router.layer(OtelAxumLayer::default());
    router = router.layer(
        ServiceBuilder::new()
            .layer(middleware::from_fn(logging_middleware))
            .layer(TraceLayer::new_for_http()),
    );

    // run it
    let listener = tokio::net::TcpListener::bind(&address).await.unwrap();
    tracing::info!(
        "fault API service listening on {}",
        listener.local_addr().unwrap()
    );
    axum::serve(listener, router)
        .with_graceful_shutdown(shutdown_signal(shutdown_rx))
        .await
        .unwrap();

    Ok(())
}

async fn shutdown_signal(shutdown_rx: kanal::AsyncReceiver<()>) {
    let _ = shutdown_rx.recv().await;
    tracing::info!("Shutdown signal received. Stopping API service.");
}

/*
Middlewares
*/
async fn logging_middleware(
    req: Request<Body>,
    next: axum::middleware::Next,
) -> Response {
    let start = Instant::now();

    let method = req.method().clone();
    let path = req.uri().path().to_string();
    let response = next.run(req).await;
    let status = response.status().as_u16();
    let duration = start.elapsed();

    tracing::info!("Received: {} {} {} {:?}", method, path, status, duration);

    response
}

/*
Models
*/
#[derive(Serialize, Deserialize)]
struct ScenarioResultResponse {}

/*
Handlers
*/

#[cfg(feature = "scenario")]
#[tracing::instrument]
#[axum::debug_handler]
async fn new_results(
    Json(result): Json<ItemResult>,
) -> Json<ScenarioResultResponse> {
    Json(ScenarioResultResponse {})
}

#[cfg(all(feature = "injection", feature = "scenario"))]
#[tracing::instrument]
#[axum::debug_handler]
async fn new_event(
    Json(event): Json<EventLifecycle>,
) -> Json<ScenarioResultResponse> {
    Json(ScenarioResultResponse {})
}

/*
Client
*/
#[cfg(feature = "scenario")]
pub async fn send_result(api_addr: &str, result: &ItemResult) -> Result<()> {
    let client = reqwest::Client::new();
    let _ = client
        .post(format!("{}/scenario/results", api_addr))
        .json(&result)
        .send()
        .await?;

    Ok(())
}

#[cfg(all(feature = "injection", feature = "scenario"))]
pub async fn forward_event(
    api_addr: &str,
    event: &EventLifecycle,
) -> Result<()> {
    let client = reqwest::Client::new();
    let response = client
        .post(format!("{}/scenario/events", api_addr))
        .json(&event)
        .send()
        .await?;

    if response.status() != StatusCode::OK {
        tracing::error!(
            "Failed to forward event back to remote API {}",
            api_addr
        );
    }

    Ok(())
}
