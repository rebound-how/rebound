//! Auto-generate rich test scenarios from OpenAPI endpoints.
//!
//! * We keep templates **in-code** (MiniJinja) so no external files are
//!   required.
//! * Each template targets a different real-world failure mode (latency,
//!   jitter, packet-loss, bandwidth, DNS, HTTP-errors, black-hole).
//! * For every **GET** operation in the spec we render **all** templates, so a
//!   single OpenAPI file yields a comprehensive test matrix.

#[cfg(feature = "openapi")]
use std::fs;
use std::fs::File;
use std::io::BufWriter;
use std::io::Write;
use std::path::Path;

use anyhow::Result;
use minijinja::Environment;
use minijinja::context;
use percent_encoding::percent_decode_str;
use serde::Serialize;
use serde_yaml;
use url::Url;

use super::types::ParsedSpec;
use super::v30x;
use super::v31x;
use crate::errors::ScenarioError;
use crate::scenario::Scenario;
use crate::scenario::generator::types::Api;
use crate::scenario::types::ScenarioGlobalConfig;

// ──────────────────────────────────────────────────────────────────────────────
// Template definitions
// ──────────────────────────────────────────────────────────────────────────────

/// 1. Sudden one-off, high latency spike (client side)
const T_LATENCY_SPIKE: &str = r#"---
title: "Single high-latency spike (client ingress)"
description: "A single 800ms spike simulates jitter buffer underrun / GC pause on client network stack."
{% if config %}config:
  {{ config }}
{% endif %}
items:
  - call:
      method: {{ method }}
      url: "{{ url }}"
      {% if method in ["POST", "PUT"] %}headers:
        content-type: "application/json"
      {% endif %}
      {% if body %}body: '{{ body }}'{% endif %}
      meta:
        operation_id: {{ opid }}
    context:
      upstreams: [ "{{ upstream }}" ]
      faults:
        - type: latency
          side: client
          direction: ingress
          mean: 800
          stddev: 100
    expect: { status: 200 }
"#;

/// 2. Stair-step latency growth over 5 iterations
const T_GRADUAL_LATENCY: &str = r#"---
title: "Stair-step latency growth (5 x 100 ms)"
description: "Latency increases 100 ms per call; emulate slow congestion build-up or head-of-line blocking."
{% if config %}config:
  {{ config }}
{% endif %}
items:
  - call:
      method: {{ method }}
      url: "{{ url }}"
      {% if method in ["POST", "PUT"] %}headers:
        content-type: "application/json"
      {% endif %}
      {% if body %}body: '{{ body }}'{% endif %}
      meta:
        operation_id: {{ opid }}
    context:
      upstreams: [ "{{ upstream }}" ]
      faults:
        - type: latency
          side: client
          direction: ingress
          mean: 100
          stddev: 30
      strategy:
        mode: repeat
        step: 100   # +100 ms per iteration
        count: 5
        add_baseline_call: true
    expect: { status: 200 }
"#;

/// 3. Periodic latency pulses within a 10-second load window
const T_PERIODIC_PULSES: &str = r#"---
title: "Periodic 150-250 ms latency pulses during load"
description: "Three latency bursts at 10-40-70% of a 10s window; good for P95 drift tracking."
{% if config %}config:
  {{ config }}
{% endif %}
items:
  - call:
      method: {{ method }}
      url: "{{ url }}"
      {% if method in ["POST", "PUT"] %}headers:
        content-type: "application/json"
      {% endif %}
      {% if body %}body: '{{ body }}'{% endif %}
      meta:
        operation_id: {{ opid }}
    context:
      upstreams: [ "{{ upstream }}" ]
      faults:
        - { type: latency, mean: 150, period: "start:10%,duration:15%" }
        - { type: latency, mean: 250, period: "start:40%,duration:15%" }
        - { type: latency, mean: 150, period: "start:70%,duration:15%" }
      strategy: { mode: load, duration: 10s, clients: 3, rps: 2 }
      slo:
        - { type: latency, title: "P95 < 300ms", objective: 95, threshold: 300 }
        - { type: error,  title: "P99 < 1% errors", objective: 99, threshold: 1 }
    expect: { all_slo_are_valid: true }
"#;

/// 4. Short burst packet-loss (egress)
const T_PACKET_LOSS: &str = r#"---
title: "5% packet loss for 4s"
description: "Simulates flaky Wi-Fi or cellular interference."
{% if config %}config:
  {{ config }}
{% endif %}
items:
  - call:
      method: {{ method }}
      url: "{{ url }}"
      {% if method in ["POST", "PUT"] %}headers:
        content-type: "application/json"
      {% endif %}
      {% if body %}body: '{{ body }}'{% endif %}
      timeout: 500
      meta:
        operation_id: {{ opid }}
    context:
      upstreams: [ "{{ upstream }}" ]
      faults:
        - type: packetloss
          direction: egress
          period: "start:30%,duration:40%"
    expect: { status: 200, response_time_under: 100.0 }
"#;

/// 5. High jitter on server side
const T_JITTER: &str = r#"---
title: "High jitter (±80ms @ 8Hz)"
description: "Emulates bursty uplink, measuring buffering robustness."
{% if config %}config:
  {{ config }}
{% endif %}
items:
  - call:
      method: {{ method }}
      url: "{{ url }}"
      {% if method in ["POST", "PUT"] %}headers:
        content-type: "application/json"
      {% endif %}
      {% if body %}body: '{{ body }}'{% endif %}
      meta:
        operation_id: {{ opid }}
    context:
      upstreams: [ "{{ upstream }}" ]
      faults:
        - type: jitter
          side: server
          direction: ingress
          amplitude: 80
          frequency: 8
    expect: { status: 200 }
"#;

/// 6. Constrained bandwidth (512 KBps) for entire test
const T_BANDWIDTH: &str = r#"---
title: "512 KBps bandwidth cap"
description: "Models throttled 3G link; validates handling of large payloads."
{% if config %}config:
  {{ config }}
{% endif %}
items:
  - call:
      method: {{ method }}
      url: "{{ url }}"
      {% if method in ["POST", "PUT"] %}headers:
        content-type: "application/json"
      {% endif %}
      {% if body %}body: '{{ body }}'{% endif %}
      meta:
        operation_id: {{ opid }}
    context:
      upstreams: [ "{{ upstream }}" ]
      faults:
        - { type: bandwidth, rate: 512, unit: KBps, direction: ingress }
      strategy: { mode: load, duration: 15s, clients: 2, rps: 1 }
      slo:
        - { type: latency, title: "P95 < 300ms", objective: 95, threshold: 300 }
        - { type: error,  title: "P99 < 1% errors", objective: 99, threshold: 1 }
    expect: { status: 200 }
"#;

/// 7. Intermittent HTTP 500 responses (5 % probability)
const T_HTTP_500: &str = r#"---
title: "Random 500 errors (5% of calls)"
description: "Backend flakiness under load; ensures retry / circuit-breaker logic."
{% if config %}config:
  {{ config }}
{% endif %}
items:
  - call:
      method: {{ method }}
      url: "{{ url }}"
      {% if method in ["POST", "PUT"] %}headers:
        content-type: "application/json"
      {% endif %}
      {% if body %}body: '{{ body }}'{% endif %}
      meta:
        operation_id: {{ opid }}
    context:
      upstreams: [ "{{ upstream }}" ]
      faults:
        - { type: httperror, status_code: 500, probability: 0.05 }
      strategy: { mode: load, duration: 8s, clients: 5, rps: 4 }
      slo:
        - { type: latency, title: "P95 < 300ms", objective: 95, threshold: 300 }
        - { type: error,  title: "P99 < 1% errors", objective: 99, threshold: 1 }
    expect: { response_time_under: 100.0 }
"#;

/// 8. Complete blackhole for a brief window
const T_BLACKHOLE: &str = r#"---
title: "Full black-hole for 1s"
description: "Simulates router drop / Pod eviction causing 100% packet loss for a second."
{% if config %}config:
  {{ config }}
{% endif %}
items:
  - call:
      method: {{ method }}
      url: "{{ url }}"
      {% if method in ["POST", "PUT"] %}headers:
        content-type: "application/json"
      {% endif %}
      {% if body %}body: '{{ body }}'{% endif %}
      timeout: 500
      meta:
        operation_id: {{ opid }}
    context:
      upstreams: [ "{{ upstream }}" ]
      faults:
        - { type: blackhole, direction: egress, period: "start:45%,duration:10%" }
      strategy: { mode: load, duration: 10s, clients: 2, rps: 3 }
      slo:
        - { type: latency, title: "P95 < 300ms", objective: 95, threshold: 300 }
        - { type: error,  title: "P99 < 1% errors", objective: 99, threshold: 1 }
"#;

fn env_with_templates(
    env: &mut Environment,
    user_dir: Option<&Path>,
) -> Result<()> {
    env.add_template("latency_spike", T_LATENCY_SPIKE).unwrap();
    env.add_template("gradual_latency", T_GRADUAL_LATENCY).unwrap();
    env.add_template("periodic_pulses", T_PERIODIC_PULSES).unwrap();
    env.add_template("packet_loss", T_PACKET_LOSS).unwrap();
    env.add_template("jitter", T_JITTER).unwrap();
    env.add_template("bandwidth", T_BANDWIDTH).unwrap();
    env.add_template("http_500", T_HTTP_500).unwrap();
    env.add_template("blackhole", T_BLACKHOLE).unwrap();

    if let Some(dir) = user_dir {
        for entry in fs::read_dir(dir)? {
            let path = entry?.path();
            if path.is_file() {
                match path.extension().and_then(|s| s.to_str()) {
                    Some("yml") | Some("yaml") => {
                        let name = path
                            .file_stem()
                            .unwrap()
                            .to_string_lossy()
                            .into_owned();
                        let content = fs::read_to_string(&path)?;
                        env.add_template_owned(name, content)?;
                    }
                    _ => {}
                }
            }
        }
    }
    Ok(())
}

// List template names once to avoid duplication
const TEMPLATE_NAMES: &[&str] = &[
    "latency_spike",
    "gradual_latency",
    "periodic_pulses",
    "packet_loss",
    "jitter",
    "bandwidth",
    "http_500",
    "blackhole",
];

pub fn generate_scenarios(
    spec: &Api,
    user_dir: Option<&Path>,
) -> Result<Vec<Scenario>> {
    let mut env = Environment::new();
    env_with_templates(&mut env, user_dir)?;
    let mut scenarios = Vec::new();

    let base = spec
        .servers
        .first()
        .cloned()
        .unwrap_or_else(|| "http://localhost".to_string());

    for api_op in &spec.operations {
        let url = format!("{}{}", base, api_op.path);
        let config: String =
            serde_yaml::to_string(&ScenarioGlobalConfig::from_url(&url)?)?
                .trim_start_matches("---\n")
                .to_string();
        let ctx = context! { config => config, method => api_op.method.to_string(), url => url, body => api_op.body, upstream => base, opid => api_op.operation_id };
        for n in TEMPLATE_NAMES {
            tracing::debug!("Generate scenario {} with context {}", n, ctx);
            let rendered = env.get_template(n)?.render(ctx.clone())?;
            scenarios.push(serde_yaml::from_str::<Scenario>(&rendered)?);
        }
    }
    Ok(scenarios)
}

/// Load an OpenAPI YAML/JSON from the local filesystem and generate scenarios.
pub fn build_from_file(
    path: &str,
    template_dir: Option<&Path>,
) -> Result<Vec<Scenario>> {
    let raw = std::fs::read_to_string(path)?;
    let spec = load_yaml_by_version(&raw)?;

    generate_scenarios(&spec, template_dir)
}

/// Fetch an OpenAPI document over HTTP(S) using Reqwest and generate scenarios.
pub async fn build_from_url(
    url: &str,
    template_dir: Option<&Path>,
) -> Result<Vec<Scenario>> {
    let response = reqwest::get(url).await?;
    let resp = reqwest::get(url).await?;
    let body = resp.text().await?;

    let spec = if response
        .headers()
        .get(reqwest::header::CONTENT_TYPE)
        .and_then(|ct| ct.to_str().ok())
        .map(|ct| ct.contains("json"))
        .unwrap_or(false)
    {
        load_json_by_version(&body)?
    } else {
        load_yaml_by_version(&body)?
    };

    generate_scenarios(&spec, template_dir)
}

fn load_yaml_by_version(spec: &String) -> Result<Api, ScenarioError> {
    let v: serde_yaml::Value = serde_yaml::from_str(&spec)
        .map_err(|e| ScenarioError::OpenAPIParsingError(e.to_string()))?;

    let parsed = ParsedSpec { json: None, yaml: Some(v.clone()) };

    let ver = v
        .get("openapi")
        .and_then(serde_yaml::Value::as_str)
        .ok_or_else(|| ScenarioError::MissingOpenAPIVersion())?;

    if ver.starts_with("3.0") {
        return Ok(v30x::load_v3(&parsed)
            .map_err(|e| ScenarioError::OpenAPIParsingError(e.to_string()))?);
    } else if ver.starts_with("3.1") {
        return Ok(v31x::load_v31(&parsed)
            .map_err(|e| ScenarioError::OpenAPIParsingError(e.to_string()))?);
    }

    Err(ScenarioError::UnsupportedOpenAPIVersion(ver.to_string()))
}

fn load_json_by_version(spec: &String) -> Result<Api, ScenarioError> {
    let v: serde_json::Value = serde_json::from_str(&spec)
        .map_err(|e| ScenarioError::OpenAPIParsingError(e.to_string()))?;

    let parsed = ParsedSpec { yaml: None, json: Some(v.clone()) };

    let ver = v
        .get("openapi")
        .and_then(serde_json::Value::as_str)
        .ok_or_else(|| ScenarioError::MissingOpenAPIVersion())?;

    if ver.starts_with("3.0") {
        return Ok(v30x::load_v3(&parsed)
            .map_err(|e| ScenarioError::OpenAPIParsingError(e.to_string()))?);
    } else if ver.starts_with("3.1") {
        return Ok(v31x::load_v31(&parsed)
            .map_err(|e| ScenarioError::OpenAPIParsingError(e.to_string()))?);
    }

    Err(ScenarioError::UnsupportedOpenAPIVersion(ver.to_string()))
}

pub fn save(
    scenarios: &Vec<Scenario>,
    path: &str,
    split: bool,
) -> Result<usize, ScenarioError> {
    let mut count = 0usize;

    let p = Path::new(path);
    if split && !p.is_dir() {
        return Err(ScenarioError::ExpectedDirectoryError());
    } else if !split {
        save_batch(scenarios, path)?;

        let mut seen: Vec<String> = Vec::<String>::new();
        for s in scenarios {
            let url = s.items[0].call.url.clone();
            if !seen.contains(&url) {
                seen.push(url);
                count += 1;
            }
        }
    } else {
        let mut batch = Vec::new();
        let mut current_url = "".to_string();

        for s in scenarios {
            let url = s.items[0].call.url.clone();
            if !current_url.is_empty() && url != current_url {
                let url_path = Url::parse(&current_url).map_err(|_| {
                    ScenarioError::IoError("failed to parse url".to_string())
                })?;

                let decoded =
                    percent_decode_str(url_path.path().trim_start_matches('/'))
                        .decode_utf8_lossy();
                let key = decoded.replace('/', "_");

                let fpath = format!("{}.yaml", key);

                save_batch(
                    &batch,
                    &format!("{}", p.join(fpath).as_os_str().display()),
                )?;

                batch.clear();
                current_url = url;
                count += 1;
            } else if current_url.is_empty() {
                current_url = url;
            }

            batch.push(s.clone());
        }
    }

    Ok(count)
}

fn save_batch(
    scenarios: &Vec<Scenario>,
    path: &str,
) -> Result<(), ScenarioError> {
    let file = File::create(path).map_err(|e| {
        tracing::error!("Failed to create scenario file '{}': {}", path, e);
        ScenarioError::IoError(e.to_string())
    })?;
    let mut writer = BufWriter::new(file);

    let mut buffer = Vec::new();
    let mut serializer = serde_yaml::Serializer::new(&mut buffer);

    for s in scenarios {
        s.serialize(&mut serializer)
            .map_err(|e| ScenarioError::IoError(e.to_string()))?;
    }

    writer.write(&buffer).map_err(|e| ScenarioError::IoError(e.to_string()))?;

    Ok(())
}
