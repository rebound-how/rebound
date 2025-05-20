use std::net::SocketAddr;
use std::sync::Arc;

use ::oneshot::Sender;
use axum::body::Body;
use axum::http::Request;
use axum::response::IntoResponse;
use hyper::Method;
use hyper::body::Incoming;
use hyper::server::conn::http1;
use hyper_util::rt::TokioIo;
use tokio::sync::broadcast;
use url::Url;

use crate::errors::ProxyError;
use crate::event::TaskManager;
use crate::proxy::ProxyState;
use crate::resolver::map_localhost_to_nic;

mod forward;
pub mod init;
mod tunnel;

#[tracing::instrument]
async fn handle_new_connection(
    source_addr: SocketAddr,
    req: Request<Body>,
    state: Arc<ProxyState>,
    task_manager: Arc<TaskManager>,
) -> Result<hyper::Response<Body>, ProxyError> {
    let req = req.map(Body::new);

    let method = req.method().clone();
    let scheme = req.uri().scheme_str().unwrap_or("http").to_string();
    let authority: Option<String> =
        req.uri().authority().map(|a| a.as_str().to_string());
    let host_header = req
        .headers()
        .get(axum::http::header::HOST)
        .and_then(|v| v.to_str().ok().map(|s| s.to_string()));

    let path = match req.uri().path_and_query() {
        Some(path) => path.to_string(),
        None => "/".to_string(),
    };

    let upstream = match determine_upstream(
        scheme,
        authority,
        host_header,
        path,
        state.stealth,
    )
    .await
    {
        Ok(url) => url,
        Err(e) => {
            tracing::error!("Failed to determine upstream: {}", e);
            return Err(e);
        }
    };

    let state: Arc<ProxyState> = state.clone();
    let hosts = state.upstream_hosts.load();
    let upstream_host = get_host(&upstream);
    let passthrough = if hosts.contains(&String::from("*")) {
        false
    } else {
        !hosts.contains(&upstream_host)
    };

    let upstream_url: Url = upstream.parse().unwrap();

    let event = if !passthrough {
        task_manager.new_fault_event(upstream_url.to_string()).await.unwrap()
    } else {
        task_manager
            .new_passthrough_event(upstream_url.to_string())
            .await
            .unwrap()
    };

    if !passthrough {
        tracing::debug!("HTTP proxying {}", upstream_url);
    }

    if method == Method::CONNECT {
        let r = tunnel::handle_connect(
            source_addr,
            req,
            state.clone(),
            upstream_url,
            passthrough,
            event.clone(),
        )
        .await;

        let resp = match r {
            Ok(r) => r,
            Err(e) => e.into_response(),
        };
        Ok(resp)
    } else {
        let r = forward::handle_request(
            source_addr,
            req,
            state.clone(),
            upstream_url,
            passthrough,
            event.clone(),
        )
        .await;

        let resp = match r {
            Ok(r) => r,
            Err(e) => e.into_response(),
        };
        Ok(resp)
    }
}

pub async fn run_http_proxy(
    proxy_address: String,
    state: Arc<ProxyState>,
    shutdown_rx: kanal::AsyncReceiver<()>,
    readiness_tx: Sender<()>,
    task_manager: Arc<TaskManager>,
) -> Result<(), ProxyError> {
    let addr: SocketAddr = proxy_address.parse().map_err(|e| {
        ProxyError::Internal(format!(
            "Failed to parse proxy address {}: {}",
            proxy_address, e
        ))
    })?;

    let proxy_listener =
        tokio::net::TcpListener::bind(addr).await.map_err(|e| {
            ProxyError::IoError(std::io::Error::new(
                e.kind(),
                format!("Failed to bind to address {}: {}", addr, e),
            ))
        })?;

    let _ = readiness_tx.send(()).map_err(|e| {
        ProxyError::Internal(format!("Failed to send readiness signal: {}", e))
    });

    loop {
        tokio::select! {
            _ = shutdown_rx.recv() => {
                tracing::info!("Shutdown signal received. Stopping listener.");
                break;
            },
            accept_result = proxy_listener.accept() => {
                match accept_result {
                    Ok((stream, addr)) => {
                        tracing::debug!("Accepted connection from {}", addr);

                        let io = TokioIo::new(stream);
                        let task_manager = task_manager.clone();
                        let state = state.clone();

                        let hyper_service =
                        hyper::service::service_fn(move |request: Request<Incoming>| {
                            handle_new_connection(
                                addr,
                                request.map(Body::new),
                                state.clone(),
                                task_manager.clone()
                            )
                        });

                        tokio::task::spawn(async move {
                            if let Err(err) = http1::Builder::new()
                                .preserve_header_case(true)
                                .title_case_headers(true)
                                .serve_connection(io, hyper_service)
                                .with_upgrades()
                                .await
                            {
                                tracing::error!("Failed to serve connection: {:?}", err);
                            }
                        });
                    }
                    Err(e) => {
                        tracing::error!("Failed to accept connection: {}", e);
                        continue;
                    }
                }
            }
        }
    }

    tracing::debug!("Proxy is now finised, bye bye");

    Ok(())
}

//
// -------------------- Private functions -----------------------------------
//

async fn determine_upstream(
    scheme: String,
    authority: Option<String>,
    host_header: Option<String>,
    path: String,
    stealth: bool,
) -> Result<String, ProxyError> {
    let upstream = if let Some(auth) = authority {
        let mut scheme = scheme;

        if let Some((_, port_str)) = auth.split_once(':') {
            scheme = match port_str {
                "443" => "https".to_string(),
                _ => "http".to_string(),
            };
        };

        format!("{}://{}{}", scheme, auth, path)
    } else if let Some(host_str) = host_header {
        let mut scheme = scheme;
        if let Some((_, port_str)) = host_str.split_once(':') {
            scheme = match port_str {
                "443" => "https".to_string(),
                _ => "http".to_string(),
            };
        };

        let (mut host, port) =
            parse_domain_with_scheme(scheme.as_str(), &host_str);
        if stealth && host.as_str() == "localhost" {
            host = map_localhost_to_nic()
        }
        format!("{}://{}:{}{}", scheme, host, port, path)
    } else {
        return Err(ProxyError::InvalidRequest(
            "Unable to determine upstream target".into(),
        ));
    };

    Ok(upstream)
}

fn parse_domain_with_scheme(scheme: &str, domain: &str) -> (String, String) {
    let default_port = match scheme {
        "https" => "443",
        _ => "80",
    };

    if let Some((host, port_str)) = domain.split_once(':') {
        let port = if port_str.is_empty() { default_port } else { port_str };
        (host.to_string(), port.to_string())
    } else {
        (domain.to_string(), default_port.to_string())
    }
}

fn get_host(upstream_url: &str) -> String {
    let url = Url::parse(upstream_url).unwrap();
    let host = url.host_str().ok_or("Missing host").unwrap().to_string();
    let port = url.port_or_known_default().unwrap();
    format!("{}:{}", host, port)
}
