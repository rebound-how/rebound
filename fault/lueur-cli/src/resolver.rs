use std::net::SocketAddr;
use std::sync::Arc;
use std::time::Instant;

use hickory_resolver::TokioResolver;
use local_ip_address::local_ip;
use reqwest::dns::Addrs;
use reqwest::dns::Resolve;
use reqwest::dns::Resolving;
use tokio::sync::Mutex;
use tokio::sync::RwLock;

use crate::event::ProxyTaskEvent;
use crate::report::types::DnsTiming;

/// Custom DNS Resolver that measures DNS resolution time and records it.
#[derive(Clone, Debug)]
pub struct TimingResolver {
    pub resolver: Arc<RwLock<TokioResolver>>,
    timing: Arc<Mutex<DnsTiming>>,
    event: Box<dyn ProxyTaskEvent>,
}

impl TimingResolver {
    /// Creates a new `TimingResolver` with the given report.
    pub fn new(
        timing: Arc<Mutex<DnsTiming>>,
        event: Box<dyn ProxyTaskEvent>,
    ) -> Self {
        // Initialize the resolver with default system configuration.
        let resolver = TokioResolver::builder_tokio().unwrap().build();

        TimingResolver {
            resolver: Arc::new(RwLock::new(resolver)),
            timing,
            event,
        }
    }
}

impl Resolve for TimingResolver {
    fn resolve(&self, hostname: reqwest::dns::Name) -> Resolving {
        let self_clone = self.clone();
        let timing = self.timing.clone();

        Box::pin(async move {
            let host = hostname.as_str();
            let resolver = self_clone.resolver.read().await;
            let start_time = Instant::now();
            let lookup = resolver.lookup_ip(host).await?;
            let duration = start_time.elapsed().as_millis_f64();
            let domain = host.to_string();

            {
                let mut timing_lock = timing.lock().await;
                timing_lock.host = domain.clone();
                timing_lock.duration = duration;
                timing_lock.resolved = true;
            }
            let ips = lookup.into_iter().collect::<Vec<_>>();
            let addrs: Addrs =
                Box::new(ips.into_iter().map(|addr| SocketAddr::new(addr, 0)));

            let _ = self_clone.event.on_resolved(domain.clone(), duration);

            Ok(addrs)
        })
    }
}

pub fn map_localhost_to_nic() -> String {
    local_ip().unwrap().to_string()
}
