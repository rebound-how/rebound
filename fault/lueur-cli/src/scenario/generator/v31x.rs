#[cfg(feature = "openapi")]
use anyhow::Result;
use http::Method;
use oas3::OpenApiV3Spec as V31;
use oas3::Spec;
use oas3::spec::FromRef;
use oas3::spec::MediaType;
use oas3::spec::MediaTypeExamples;
use oas3::spec::ObjectOrReference;
use oas3::spec::ObjectSchema;
use oas3::spec::RequestBody;
use oas3::spec::Schema;
use oas3::spec::SchemaType;
use oas3::spec::SchemaTypeSet;
use serde_json::Map;
use serde_json::Number;
use serde_json::Value;

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
        let body = if method == Method::POST || method == Method::PUT {
            op.request_body
                .as_ref()
                .and_then(|obr| resolve_request_body(obr, model))
        } else {
            None
        };

        ops.push(ApiOperation {
            path: path.clone(),
            idempotent: method.clone().is_idempotent(),
            method: method,
            operation_id: op.operation_id.clone(),
            body,
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

fn resolve_request_body(
    obr: &ObjectOrReference<RequestBody>,
    model: &V31,
) -> Option<String> {
    match obr {
        ObjectOrReference::Object(rb) => parse_body(rb, model),
        ObjectOrReference::Ref { ref_path } => {
            // Only handle local refs of form "#/components/requestBodies/Name"
            const PREFIX: &str = "#/components/requestBodies/";
            if let Some(name) = ref_path.strip_prefix(PREFIX) {
                if let Some(comp_obra) =
                    model.components.as_ref()?.request_bodies.get(name)
                {
                    // Recurse with the component
                    resolve_request_body(comp_obra, model)
                } else {
                    None
                }
            } else {
                None
            }
        }
    }
}

fn parse_body(rb: &RequestBody, model: &V31) -> Option<String> {
    rb.content.get("application/json").and_then(|mt: &MediaType| {
        if let Some(MediaTypeExamples::Example { example }) = &mt.examples {
            return serde_json::to_string(example).ok();
        }

        if let Some(MediaTypeExamples::Examples { examples }) = &mt.examples {
            for eor in examples.values() {
                if let ObjectOrReference::Object(example_obj) = eor {
                    return serde_json::to_string(&example_obj.value).ok();
                }
            }
        }

        if let Some(schema_ref) = &mt.schema {
            let schema_enum = match schema_ref {
                ObjectOrReference::Object(obj_schema) => Schema::Object(
                    Box::new(ObjectOrReference::Object(obj_schema.clone())),
                ),
                ObjectOrReference::Ref { ref_path } => {
                    Schema::Object(Box::new(ObjectOrReference::Ref {
                        ref_path: ref_path.clone(),
                    }))
                }
            };

            let value = instantiate_schema(&schema_enum, model);
            return serde_json::to_string(&value).ok();
        }
        None
    })
}

/// Instantiate an "empty" JSON value for the given OpenAPI Schema:
/// - objects => { "prop": <default>, ... }
/// - strings => ""
/// - numbers/integers => 0
/// - booleans => false
/// - arrays => []
/// - everything else =>  null
pub fn instantiate_schema(
    schema: &Schema,
    spec: &Spec, // your full spec, for resolving $refs
) -> Value {
    match schema {
        Schema::Boolean(_) => Value::Bool(false),

        Schema::Object(boxed_oor) => {
            // resolve the ObjectOrReference<ObjectSchema>
            let obj_schema: ObjectSchema = match &**boxed_oor {
                ObjectOrReference::Object(o) => o.clone(),
                ObjectOrReference::Ref { ref_path } => {
                    // use the FromRef impl to pull in the referenced schema
                    ObjectSchema::from_ref(spec, ref_path)
                        .expect("unresolvable schema ref")
                }
            };
            instantiate_object(&obj_schema, spec)
        }
    }
}

fn instantiate_object(obj: &ObjectSchema, spec: &Spec) -> Value {
    // pick first schema
    if let Some(sub) = obj
        .all_of
        .iter()
        .chain(&obj.one_of)
        .chain(&obj.any_of)
        .filter_map(|oor| match oor {
            ObjectOrReference::Object(o) => Some(o.clone()),
            ObjectOrReference::Ref { ref_path } => {
                ObjectSchema::from_ref(spec, &ref_path).ok()
            }
        })
        .next()
    {
        return instantiate_object(&sub, spec);
    }

    // Build up a JSON object
    let mut map = Map::new();

    // Properties
    for (name, oor) in &obj.properties {
        let child_schema = match oor {
            ObjectOrReference::Object(child) => child.clone(),
            ObjectOrReference::Ref { ref_path } => {
                ObjectSchema::from_ref(spec, ref_path)
                    .expect("unresolvable property schema ref")
            }
        };
        map.insert(name.clone(), instantiate_object(&child_schema, spec));
    }

    if let Some(typeset) = &obj.schema_type {
        return default_value_for_type_set(typeset, map);
    } else {
        return Value::Object(map);
    }
}

fn default_value_for_type_set(
    typeset: &SchemaTypeSet,
    map: Map<String, Value>,
) -> Value {
    match typeset {
        SchemaTypeSet::Single(t) => match t {
            SchemaType::Boolean => Value::Bool(false),
            SchemaType::Integer => Value::Number(Number::from(0)),
            SchemaType::Number => {
                Number::from_f64(0.0).map(Value::Number).unwrap_or(Value::Null)
            }
            SchemaType::String => Value::String(String::new()),
            SchemaType::Array => Value::Array(Vec::new()),
            SchemaType::Object => {
                // empty object (use the provided `map` to fill props)
                Value::Object(map)
            }
            SchemaType::Null => Value::Null,
        },

        SchemaTypeSet::Multiple(list) => {
            // Pick the first type in the set and recurse
            if let Some(first) = list.first() {
                default_value_for_type_set(
                    &SchemaTypeSet::Single(first.clone()),
                    map,
                )
            } else {
                // fallback if somehow empty
                Value::Null
            }
        }
    }
}
