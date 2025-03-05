use std::env;
use std::fmt;
use std::time::Instant;

use axum::Router;
use axum::body::Body;
use axum::extract::Json;
use axum::extract::Request;
use axum::http::StatusCode;
use axum::middleware;
use axum::response::Html;
use axum::response::IntoResponse;
use axum::response::Response;
use axum::routing::get;
use axum::routing::post;
use axum_tracing_opentelemetry::middleware::OtelAxumLayer;
use axum_tracing_opentelemetry::middleware::OtelInResponseLayer;
use futures::future::join_all;
use reqwest::ClientBuilder;
use serde::Deserialize;
use serde::Serialize;
use tokio::signal;
use tower::ServiceBuilder;
use tower_http::trace::TraceLayer;

use crate::cli::DemoConfig;
use crate::errors::DemoError;

pub async fn run(config: DemoConfig) -> Result<(), DemoError> {
    let mut router = Router::new();
    router = router.route("/", get(index));
    router = router.route("/ping/myself", get(ping_myself));
    router = router.route("/uppercase", post(upper));
    router = router.route("/ping", get(ping_remote));
    router = router.route("/multi", get(multi));
    router = router.layer(OtelInResponseLayer);
    router = router.layer(OtelAxumLayer::default());
    router = router.layer(
        ServiceBuilder::new()
            .layer(middleware::from_fn(logging_middleware))
            .layer(TraceLayer::new_for_http()),
    );

    // run it
    let bind_to = format!("{}:{}", config.address, config.port);
    let listener = tokio::net::TcpListener::bind(bind_to).await.unwrap();
    tracing::debug!("listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, router)
        .with_graceful_shutdown(shutdown_signal())
        .await
        .unwrap();

    Ok(())
}

async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c().await.expect("failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("failed to install signal handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {},
        _ = terminate => {},
    }
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

    println!("{} {} {} {:?}", method, path, status, duration);

    response
}

/*
Handlers
*/

#[derive(Serialize, Deserialize, Debug)]
struct Message {
    content: String,
}

impl fmt::Display for Message {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.content)
    }
}

#[derive(Serialize, Deserialize)]
struct Pong {
    content: serde_json::Value,
    duration: String,
}

#[tracing::instrument]
async fn index() -> Html<&'static str> {
    Html("<h1>Hello, World!</h1>")
}

#[tracing::instrument]
async fn upper(Json(message): Json<Message>) -> Json<Message> {
    let upper = message.content.to_uppercase();
    Json(Message { content: upper })
}

#[tracing::instrument]
async fn ping_myself() -> axum::response::Response<Body> {
    let builder = make_builder();
    let client = builder.build().unwrap();

    let start = Instant::now();
    let response = client.get("http://127.0.0.1:7070/").send().await.unwrap();

    let status = response.status();
    let _body = response.text().await.unwrap();

    let duration = start.elapsed();

    tracing::info!("took {:?}", duration);

    if status != 200 {
        tracing::warn!("Downstream dependency returned {}", status);
        return (StatusCode::INTERNAL_SERVER_ERROR, "Something went wrong...")
            .into_response();
    }

    Html("<h1>Hello, World!</h1>").into_response()
}

#[tracing::instrument]
async fn ping_remote() -> Json<Pong> {
    let builder = make_builder();

    let client = builder.build().unwrap();

    let start = Instant::now();
    let response =
        client.get("https://postman-echo.com/get").send().await.unwrap();

    let status = response.status();
    if status != 200 {
        tracing::warn!("Downstream dependency returned {}", status);
    }

    let body = response.json::<serde_json::Value>().await.unwrap();

    let duration = start.elapsed();

    Json(Pong { content: body, duration: duration.as_millis_f64().to_string() })
}

#[tracing::instrument]
async fn multi() -> Json<Pong> {
    let builder = make_builder();

    let client = builder.build().unwrap();

    let urls = ["https://www.example.com/", "https://postman-echo.com/get"];

    let start = Instant::now();

    let fetches = urls.iter().map(|&url| {
        let client = &client;
        async move {
            let response = client.get(url).send().await?;
            let status = response.status();
            let body = response.text().await?;
            Ok::<(String, u16, usize, String), reqwest::Error>((
                url.to_string(),
                status.as_u16(),
                body.len(),
                body,
            ))
        }
    });

    // Execute all fetches concurrently
    let results = join_all(fetches).await;

    // Process the results
    for result in results {
        match result {
            Ok((url, status, length, _body)) => {
                println!(
                    "URL: {}\nStatus: {}\nResponse Length: {}\n",
                    url, status, length
                );
            }
            Err(e) => {
                eprintln!("Error fetching URL: {}", e);
            }
        }
    }

    let duration = start.elapsed();

    Json(Pong {
        content: "".into(),
        duration: duration.as_millis_f64().to_string(),
    })
}

fn make_builder() -> ClientBuilder {
    let mut builder = reqwest::Client::builder();

    // http proxy
    builder = match env::var("HTTP_PROXY") {
        Ok(addr) => {
            tracing::debug!("Injecting http proxy {}", addr);
            builder.proxy(reqwest::Proxy::http(addr).unwrap())
        }
        Err(_) => builder,
    };

    // https proxy
    builder = match env::var("HTTPS_PROXY") {
        Ok(addr) => {
            tracing::debug!("Injecting https proxy {}", addr);
            builder.proxy(reqwest::Proxy::https(addr).unwrap())
        }
        Err(_) => builder,
    };

    builder
}
