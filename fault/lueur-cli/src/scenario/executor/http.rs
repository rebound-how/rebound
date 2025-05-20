use std::error::Error;
use std::net::SocketAddr;
use std::pin::Pin;
use std::sync::Arc;
use std::task::Context;
use std::task::Poll;
use std::time::Duration;

use arc_swap::ArcSwap;
use bytes::Bytes;
use bytes::BytesMut;
use http::Extensions;
use hyper_util::client::legacy::connect::Connected;
use hyper_util::client::legacy::connect::Connection as HyperConnection;
use hyper_util::client::legacy::connect::HttpInfo;
use pin_project::pin_project;
use reqwest::Client;
use reqwest::RequestBuilder;
use tokio::time::Instant;
use tokio_stream::Stream;
use tokio_stream::StreamExt;
use tower::Layer;
use tower::Service;
use uuid::Uuid;

use crate::errors::ScenarioError;
use crate::scenario::event::ScenarioItemLifecycle;
use crate::scenario::types::ItemMetrics;
use crate::scenario::types::ItemProtocol;
use crate::scenario::types::ScenarioGlobalConfig;
use crate::scenario::types::ScenarioItemCall;

// Define a custom stream wrapper to measure TTFB
#[pin_project]
struct TimingStream<S> {
    #[pin]
    inner: S,
    pub first_byte_time: Option<Instant>,
}

impl<S> TimingStream<S> {
    fn new(inner: S) -> Self {
        Self { inner, first_byte_time: None }
    }
}

impl<S> Stream for TimingStream<S>
where
    S: Stream<Item = Result<Bytes, reqwest::Error>> + Unpin,
{
    type Item = Result<Bytes, reqwest::Error>;

    fn poll_next(
        self: Pin<&mut Self>,
        cx: &mut Context<'_>,
    ) -> Poll<Option<Self::Item>> {
        let this = self.project();
        match this.inner.poll_next(cx) {
            Poll::Ready(Some(Ok(bytes))) => {
                if this.first_byte_time.is_none() {
                    let now = Instant::now();
                    *this.first_byte_time = Some(now);
                }
                Poll::Ready(Some(Ok(bytes)))
            }
            other => other,
        }
    }
}

pub async fn execute_request(
    call: ScenarioItemCall,
    global_config: Option<ScenarioGlobalConfig>,
    proxy_address: String,
    addr_id_map: Arc<scc::HashMap<String, Uuid>>,
    id_events_map: Arc<scc::HashMap<Uuid, ScenarioItemLifecycle>>,
) -> Result<ItemMetrics, ScenarioError> {
    // atomic structure holding the local/remote addresses for the connection
    let addresses = Arc::new(ArcSwap::from_pointee(Addresses::new()));
    let log_layer = LoggingConnectorLayer { addresses: addresses.clone() };

    let client = Arc::new(
        reqwest::Client::builder()
            .proxy(reqwest::Proxy::http(&proxy_address).unwrap())
            .connector_layer(log_layer)
            .build()
            .map_err(|e| ScenarioError::HTTPError(e.to_string()))?,
    );

    let reqwest_request = build_request(&client, &call, global_config)?
        .build()
        .map_err(|e| ScenarioError::HTTPError(e.to_string()))?;

    let mut errored = false;
    let mut timed_out = false;
    let mut buffer = BytesMut::new();
    let mut dns_timing = Vec::new();
    let mut faults = Vec::new();

    let conn_start = Instant::now();
    let ttfb_start = conn_start.clone();

    let response = client.execute(reqwest_request).await;

    let response = match response {
        Ok(r) => Some(r),
        Err(e) => {
            if e.is_timeout() {
                tracing::warn!("Request timed out");
                timed_out = true;
            }

            tracing::error!("Error while receiving bytes: {}", e);
            errored = true;
            None
        }
    };

    let mut metrics = ItemMetrics::new();

    if let Some(response) = response {
        let status = response.status();
        let stream = response.bytes_stream();
        let timing_stream = TimingStream::new(stream);

        futures::pin_mut!(timing_stream);
        while let Some(chunk) = timing_stream.next().await {
            match chunk {
                Ok(bytes) => {
                    buffer.extend_from_slice(&bytes);
                }
                Err(e) => {
                    if e.is_timeout() {
                        tracing::warn!("Request timed out");
                        timed_out = true;
                        break;
                    }

                    tracing::error!("Error while receiving bytes: {}", e);
                    errored = true;
                    break;
                }
            }
        }

        metrics.total_time = conn_start.elapsed().as_millis_f64();

        let ttfb_time;
        if let Some(ttfb) = timing_stream.first_byte_time {
            ttfb_time = ttfb.elapsed();
        } else {
            ttfb_time = ttfb_start.elapsed();
        }

        let body_bytes = buffer.freeze();
        let body_length = body_bytes.len();

        metrics.protocol =
            Some(ItemProtocol::Http { code: status.as_u16(), body_length });
        metrics.ttfb = ttfb_time.as_millis_f64();
    } else {
        metrics.total_time = conn_start.elapsed().as_millis_f64();
    }

    // because I need a response to access the local client address
    // this is only valid when the requests didn't fail. I want to try
    // hyper to always retrieve the local address
    let addr = addresses.load();
    if let Some(local) = addr.local {
        let local_addr = local.to_string();
        if let Some(event_id) =
            addr_id_map.read_async(&local_addr, |_, v| *v).await
        {
            if let Some((_, event)) =
                id_events_map.remove_async(&event_id).await
            {
                dns_timing = event.dns_timing;
                faults = vec![event.faults.as_metrics_faults()];
            }
        }
    }

    metrics.dns = dns_timing;
    metrics.faults = faults;
    metrics.timed_out = timed_out;
    metrics.errored = errored;

    Ok(metrics)
}

fn build_request(
    client: &Arc<Client>,
    call: &ScenarioItemCall,
    global_config: Option<ScenarioGlobalConfig>,
) -> Result<RequestBuilder, ScenarioError> {
    let mut url = call.url.clone();

    if let Some(gc) = global_config.clone() {
        if let Some(http) = gc.http {
            if let Some(paths) = http.paths {
                for (key, value) in paths.segments.iter() {
                    let segment = &format!("{{{}}}", key);
                    url = url.replace(segment, value);
                }
            }
        }
    }

    let mut req_builder = client.request(
        reqwest::Method::from_bytes(call.method.as_bytes())
            .map_err(|_| ScenarioError::HTTPMethodError(call.method.clone()))?,
        &url,
    );

    if let Some(gc) = global_config {
        if let Some(http) = gc.http {
            if let Some(headers) = http.headers {
                for (key, value) in headers.iter() {
                    req_builder = req_builder.header(key, value);
                }
            }
        }
    }

    if let Some(headers) = &call.headers {
        for (key, value) in headers.iter() {
            req_builder = req_builder.header(key, value);
        }
    }

    if let Some(body) = &call.body {
        req_builder = req_builder.body(body.clone());
    }

    if let Some(timeout) = &call.timeout {
        req_builder = req_builder.timeout(Duration::from_millis(*timeout));
    }

    Ok(req_builder)
}

/// The following is a tad far fetched but I couldn't think of a better way.
/// When the client sends a request, even though we are in the same process as
/// the proxy, we need a way to fetch the proxy's fault events for this exact
/// request. We could try to add a Header but this forces the proxy to be made
/// aware of our need and that feels too much of a leaky implementation detail
/// for my liking.
///
/// So the approach I chose for now is to use the client's local address
/// as a way to lookup the proxy's events (the proxy records the source address
/// and maps it to its internal events).
///
/// Then came the next issue. reqwest itself is rather constraint in what it
/// selects to expose. While the  client's local address can be fetched , it
/// can only be done so on the response  object. That object isn't available
/// when the request errored. Which is more or less the whole point of network
/// fault injection. For instance, with a blockhole fault, we trigger the
/// request timeout and thus never see the response.
///
/// Luckily, we could attach the connect layer to reqwest and capture the
/// information directly from tower instead, just before reqwest decides to
/// trigger the error.
///
/// I chose to use an atomic value to pass the addresses around because they
/// are much faster than mutexes and appropriate here.

#[derive(Clone)]
pub struct Addresses {
    pub local: Option<SocketAddr>,
    pub remote: Option<SocketAddr>,
}

impl Addresses {
    pub fn new() -> Self {
        Addresses { local: None, remote: None }
    }
}

#[derive(Clone)]
pub struct LoggingConnectorLayer {
    pub addresses: Arc<ArcSwap<Addresses>>,
}

impl<S> Layer<S> for LoggingConnectorLayer {
    type Service = LoggingConnector<S>;

    fn layer(&self, inner: S) -> Self::Service {
        LoggingConnector { inner, addresses: self.addresses.clone() }
    }
}

#[derive(Clone)]
pub struct LoggingConnector<S> {
    inner: S,
    addresses: Arc<ArcSwap<Addresses>>,
}

impl<S, Req, ConnType, E> Service<Req> for LoggingConnector<S>
where
    // S must be able
    // to take a Req
    // and yield some
    // ConnType
    S: Service<Req, Response = ConnType, Error = E>
        + Clone
        + Send
        + Sync
        + 'static,
    S::Future: Send + 'static,
    // The ConnType must implement Hyper’s Connection trait
    ConnType: HyperConnection + Send + 'static,
    // Its error must be convertible to a boxed error (as Reqwest expects)
    E: Into<Box<dyn Error + Send + Sync>> + 'static,
    Req: Send + 'static,
{
    type Response = ConnType;
    type Error = E;
    type Future = Pin<Box<dyn Future<Output = Result<ConnType, E>> + Send>>;

    fn poll_ready(
        &mut self,
        cx: &mut Context<'_>,
    ) -> Poll<Result<(), Self::Error>> {
        self.inner.poll_ready(cx)
    }

    fn call(&mut self, req: Req) -> Self::Future {
        // see https://docs.rs/tower-service/latest/tower_service/trait.Service.html#be-careful-when-cloning-inner-services
        let clone = self.inner.clone();
        let mut inner = std::mem::replace(&mut self.inner, clone);

        let addresses = self.addresses.clone();

        Box::pin(async move {
            let conn = inner.call(req).await?;

            // HyperConnection::connected() gives us a `Connected` from which
            // we can extract both local_addr() and remote_addr().
            let info: Connected = conn.connected();

            let mut ext = Extensions::new();
            info.get_extras(&mut ext);

            if let Some(http_info) = ext.get::<HttpInfo>() {
                let local = http_info.local_addr();
                let remote = http_info.remote_addr();

                addresses.store(Arc::new(Addresses {
                    local: Some(local.clone()),
                    remote: Some(remote.clone()),
                }));
            }

            Ok(conn)
        })
    }
}
