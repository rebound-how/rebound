use std::collections::BTreeMap;

use chrono::DateTime;
use chrono::Utc;
use serde::Deserialize;
use serde::Serialize;
use serde_json::Value;

#[derive(
    clap::ValueEnum, Clone, Copy, Debug, Serialize, Deserialize, Eq, PartialEq,
)]
#[serde(rename_all = "lowercase")]
pub enum ResourcePlatform {
    Kubernetes,
}

#[derive(Serialize, Deserialize)]
pub struct K8sSpecSnapshot {
    pub selector: BTreeMap<String, String>,
    pub ports: Vec<Value>,
}

#[derive(Clone, Serialize, Deserialize, Debug)]
pub struct Link {
    pub direction: String,
    pub kind: String,
    pub path: String,
    pub pointer: String,
    pub id: String,
}

#[derive(Clone, Serialize, Deserialize, Debug)]
pub struct Meta {
    pub name: String,
    pub ns: String,
    pub display: String,
    pub dt: DateTime<Utc>,
    pub kind: String,
    pub category: String,
    pub platform: Option<String>,
    pub region: Option<String>,
    pub project: Option<String>,
}

#[derive(Clone, Serialize, Deserialize, Debug)]
pub struct Resource {
    pub id: String,
    pub meta: Meta,
    pub links: Vec<Link>,
    pub content: Value,
}
