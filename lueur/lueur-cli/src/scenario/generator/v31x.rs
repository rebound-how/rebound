use anyhow::Result;
use oas3::OpenApiV3Spec as V31;

use super::types::Api;
use super::types::ApiOperation;
use super::types::ParsedSpec;

pub fn load_v31(v: &ParsedSpec) -> Result<Api> {
    if let Some(s) = &v.yaml {
        let api: V31 = serde_yaml::from_value(s.clone())?;
        return build(&api);
    }

    let api: V31 = serde_json::from_value(v.json.clone().unwrap().clone())?;

    build(&api)
}

fn build(model: &V31) -> Result<Api> {
    let mut ops = Vec::new();

    for (path, method, op) in model.operations() {
        ops.push(ApiOperation {
            path: path.clone(),
            idempotent: method.clone().is_idempotent(),
            method: method,
            operation_id: op.operation_id.clone(),
        });
    }

    Ok(Api {
        operations: ops,
        servers: model
            .servers
            .iter()
            .map(|s| s.url.clone())
            .collect::<Vec<String>>(),
    })
}
