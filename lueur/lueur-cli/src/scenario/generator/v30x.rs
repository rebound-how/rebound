#[cfg(feature = "openapi")]
use std::fs::File;
use std::io::BufReader;

use anyhow::Result;
use openapiv3::OpenAPI as V3;
use openapiv3::Operation;
use openapiv3::PathItem;

use super::types::Api;
use super::types::ApiOperation;
use super::types::ParsedSpec;
use crate::scenario::types::ScenarioGlobalConfig;

pub fn load_v3(v: &ParsedSpec) -> Result<Api> {
    let mut api: V3 = V3::default();

    if let Some(s) = &v.yaml {
        api = serde_yaml::from_value(s.clone())?;
    } else if let Some(s) = &v.json {
        api = serde_json::from_value(s.clone())?;
    }

    let mut ops = Vec::new();

    for (path, item) in api.paths.paths {
        if let openapiv3::ReferenceOr::Item(item) = item {
            if let Some((m, idem, op)) = operation_method(&item) {
                let body = if m == http::Method::POST || m == http::Method::PUT
                {
                    op.request_body.as_ref().and_then(|rb_ref| {
                        if let openapiv3::ReferenceOr::Item(rb) = rb_ref {
                            rb.content.get("application/json").and_then(|media| {
                                if let Some(example) = &media.example {
                                    serde_json::to_string(example).ok()
                                } else {
                                    media.schema.as_ref().and_then(|schema_ref| {
                                        if let openapiv3::ReferenceOr::Item(schema) = schema_ref {
                                            serde_json::to_string(schema).ok()
                                        } else {
                                            None
                                        }
                                    })
                                }
                            })
                        } else {
                            None
                        }
                    })
                } else {
                    None
                };

                ops.push(ApiOperation {
                    path: path.clone(),
                    method: m,
                    idempotent: idem,
                    operation_id: op.operation_id.clone(),
                    body,
                });
            }
        }
    }

    Ok(Api {
        operations: ops,
        servers: api
            .servers
            .iter()
            .map(|s| s.url.clone())
            .collect::<Vec<String>>(),
    })
}

fn operation_method(
    item: &PathItem,
) -> Option<(http::Method, bool, Operation)> {
    if let Some(op) = &item.get {
        (http::Method::GET, true, op);
    }

    if let Some(op) = &item.post {
        (http::Method::POST, false, op);
    }

    if let Some(op) = &item.put {
        (http::Method::PUT, false, op);
    }

    if let Some(op) = &item.delete {
        (http::Method::DELETE, false, op);
    }

    if let Some(op) = &item.patch {
        (http::Method::PATCH, false, op);
    }

    if let Some(op) = &item.trace {
        (http::Method::TRACE, false, op);
    }

    if let Some(op) = &item.options {
        (http::Method::OPTIONS, true, op);
    }

    None
}
