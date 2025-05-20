pub enum SupportedSpecVersion {
    V30x,
    V31x,
}

pub struct ParsedSpec {
    pub yaml: Option<serde_yaml::Value>,
    pub json: Option<serde_json::Value>,
}

#[derive(Clone, Debug)]
pub struct ApiOperation {
    pub path: String,
    pub method: http::Method,
    pub idempotent: bool,
    pub operation_id: Option<String>,
    pub body: Option<String>,
}

#[derive(Clone, Debug)]
pub struct Api {
    pub operations: Vec<ApiOperation>,
    pub servers: Vec<String>,
}
