use std::collections::HashMap;
use std::fs;
use std::path::Path;
use std::sync::Arc;

use outlines_core::json_schema;
use pulldown_cmark::Parser;
use pulldown_cmark::TextMergeStream;
use regex::Regex;
use rmcp::Error as McpError;
use rmcp::ServerHandler;
use rmcp::model::CallToolResult;
use rmcp::model::Content;
use rmcp::model::ServerCapabilities;
use rmcp::model::ServerInfo;
use rmcp::schemars;
use rmcp::tool;
use serde::Deserialize;
use serde::Serialize;
use serde_json::json;
use similar::TextDiff;
use swiftide::indexing::EmbeddedField;
use swiftide::integrations::fastembed::FastEmbed;
use swiftide::integrations::qdrant::Qdrant;
use swiftide::query;
use swiftide::query::answers;
use swiftide::query::query_transformers;
use swiftide_core::EmbeddingModel;
use swiftide_core::SimplePrompt;
use url::Url;

use crate::agent::CODE_COLLECTION;
use crate::agent::clients::SupportedLLMClient;
use crate::agent::clients::get_client;
use crate::agent::mcp::code;
use crate::agent::mcp::code::extract_function_snippet;
use crate::agent::mcp::code::guess_file_language;
use crate::agent::mcp::code::list_functions;
use crate::report;
use crate::report::types::Report;
use crate::scenario::executor::run_scenario_first_item;
use crate::scenario::types::Scenario;
use crate::scenario::types::ScenarioItem;
use crate::scenario::types::ScenarioItemCall;
use crate::scenario::types::ScenarioItemCallStrategy;
use crate::scenario::types::ScenarioItemContext;
use crate::scenario::types::ScenarioItemProxySettings;
use crate::scenario::types::ScenarioItemSLO;
use crate::types::BandwidthUnit;
use crate::types::FaultConfiguration;
use crate::types::StreamSide;

#[derive(Serialize, Deserialize, schemars::JsonSchema)]
pub struct CodeBlock {
    #[schemars(
        description = "full function block, including its signature and outter decorators"
    )]
    pub full: String,
    #[schemars(description = "full function body only")]
    pub body: String,
}

#[derive(Serialize, Deserialize, Default, schemars::JsonSchema)]
pub struct CodeChange {
    #[schemars(description = "score before the improvements were computed")]
    pub score: f64,
    #[schemars(
        description = "a short summary of the main threats you found and changes you made"
    )]
    pub explanation: String,
    #[schemars(
        description = "the full content of the file before the changes"
    )]
    pub old: String,
    #[schemars(description = "the full content of the file after the changes")]
    pub new: String,
    #[schemars(
        description = "a list of dependencies that may be required to install as part of the changes"
    )]
    pub dependencies: Vec<String>,
    #[schemars(description = "the computed unified-diff between old and new")]
    pub diff: String,
}

#[derive(Default, Clone)]
pub struct FaultMCP {
    pub llm_type: SupportedLLMClient,
    pub prompt_model: String,
    pub embed_model: String,
    pub embed_model_dim: u64,
}

const PERFORMANCE_TEMPLATE: &str =
    include_str!("../prompts/tool_eval_code_performance.md");
const RELIABILITY_TEMPLATE: &str =
    include_str!("../prompts/tool_eval_code_reliability.md");
const SCENARIO_TEMPLATE: &str =
    include_str!("../prompts/tool_eval_code_scenario.md");

#[tool(tool_box)]
impl FaultMCP {
    #[allow(dead_code)]
    pub fn new(
        llm_type: SupportedLLMClient,
        prompt_model: &str,
        embed_model: &str,
        embed_model_dim: u64,
    ) -> Self {
        Self {
            llm_type,
            prompt_model: prompt_model.into(),
            embed_model: embed_model.into(),
            embed_model_dim,
        }
    }

    #[tool(
        name = "fault_list_function_names",
        description = "List all function names in the given source code file"
    )]
    async fn list_functions(
        &self,
        #[tool(param)]
        #[schemars(description = "Absolute local path to a code file")]
        file: String,
    ) -> Result<CallToolResult, McpError> {
        let path = file.strip_prefix("file://").unwrap_or(&file);
        let src = fs::read_to_string(path).map_err(|e| {
            McpError::internal_error(
                "file_read",
                Some(json!({"err": e.to_string()})),
            )
        })?;

        let ext = Path::new(path)
            .extension()
            .and_then(|s| s.to_str())
            .ok_or_else(|| McpError::invalid_params("bad_uri", None))?;

        let names = list_functions(&src, ext)
            .ok_or_else(|| McpError::invalid_params("func_not_found", None))?;

        Ok(CallToolResult::success(vec![Content::json(json!(names)).map_err(
            |e| {
                McpError::internal_error(
                    "file_read",
                    Some(json!({"err": e.to_string()})),
                )
            },
        )?]))
    }

    #[tool(
        name = "fault_index_source_code",
        description = "Index a source code directory"
    )]
    async fn index_source(
        &self,
        #[tool(param)]
        #[schemars(description = "Directory of to start indexing from")]
        source_dir: String,
        #[tool(param)]
        #[schemars(
            description = "Language type of the source: python, rust, go..."
        )]
        lang: String,
    ) -> Result<CallToolResult, McpError> {
        let path: &str =
            source_dir.strip_prefix("file://").unwrap_or(&source_dir);
        let cache_db_path = "/tmp/index.db";

        code::index(
            path,
            &lang,
            cache_db_path,
            self.llm_type,
            &self.prompt_model,
            &self.embed_model,
            self.embed_model_dim,
        )
        .await
        .map_err(|e| {
            McpError::internal_error(
                "code_index",
                Some(json!({"err": e.to_string()})),
            )
        })?;

        Ok(CallToolResult::success(vec![Content::text("done".to_string())]))
    }

    #[tool(
        name = "fault_extract_code_block",
        description = "Extract function code block by name"
    )]
    async fn extract_code_block(
        &self,
        #[tool(param)]
        #[schemars(description = "Absolute local path to a code file")]
        file: String,
        #[tool(param)]
        #[schemars(description = "Function name to extract from the file")]
        func: String,
    ) -> Result<CallToolResult, McpError> {
        let path = file.strip_prefix("file://").unwrap_or(&file);
        let src = fs::read_to_string(path).map_err(|e| {
            McpError::internal_error(
                "file_read",
                Some(json!({"err": e.to_string()})),
            )
        })?;

        let ext = Path::new(path)
            .extension()
            .and_then(|s| s.to_str())
            .ok_or_else(|| McpError::invalid_params("bad_uri", None))?;

        let snippet =
            extract_function_snippet(&src, ext, &func).ok_or_else(|| {
                McpError::invalid_params(
                    "func_not_found",
                    Some(json!({"func": func.clone()})),
                )
            })?;

        let block = CodeBlock { full: snippet.full, body: snippet.body };

        Ok(CallToolResult::success(vec![Content::json(json!(block)).map_err(
            |e| {
                McpError::internal_error(
                    "file_read",
                    Some(json!({"err": e.to_string()})),
                )
            },
        )?]))
    }

    #[tool(
        name = "fault_score_performance",
        description = "Compute a performance score of a code block, snippet or function"
    )]
    async fn score_performance(
        &self,
        #[tool(param)]
        #[schemars(description = "Code block to score")]
        snippet: String,
        #[tool(param)]
        #[schemars(
            description = "Language of the snippet: python, rust, go..."
        )]
        lang: String,
    ) -> Result<CallToolResult, McpError> {
        let prompt = include_str!("../prompts/tool_score_code_performance.md");

        let filled =
            prompt.replace("{lang}", &lang).replace("{snippet}", &snippet);

        let llm =
            get_client(self.llm_type, &self.prompt_model, &self.embed_model)
                .map_err(|e| {
                    McpError::internal_error(
                        "client_build",
                        Some(json!({"err": e.to_string()})),
                    )
                })?;

        let answer = llm.prompt(filled.into()).await.map_err(|e| {
            McpError::internal_error(
                "llm_prompt",
                Some(json!({"err": e.to_string()})),
            )
        })?;

        let parsed: serde_json::Value =
            serde_json::from_str(&answer).map_err(|e| {
                McpError::internal_error(
                    "parse_score_response",
                    Some(json!({"err": e.to_string()})),
                )
            })?;

        Ok(CallToolResult::success(vec![Content::json(parsed).map_err(
            |e| {
                McpError::internal_error(
                    "score_performance",
                    Some(json!({"err": e.to_string()})),
                )
            },
        )?]))
    }

    #[tool(
        name = "fault_score_reliability",
        description = "Compute a reliability score of a code block, snippet or function"
    )]
    async fn score_reliability(
        &self,
        #[tool(param)]
        #[schemars(description = "Code block to score")]
        snippet: String,
        #[tool(param)]
        #[schemars(
            description = "Language of the snippet: python, rust, go..."
        )]
        lang: String,
    ) -> Result<CallToolResult, McpError> {
        let prompt = include_str!("../prompts/tool_score_code_reliability.md");

        let filled =
            prompt.replace("{lang}", &lang).replace("{snippet}", &snippet);

        let llm =
            get_client(self.llm_type, &self.prompt_model, &self.embed_model)
                .map_err(|e| {
                    McpError::internal_error(
                        "client_build",
                        Some(json!({"err": e.to_string()})),
                    )
                })?;
        let answer = llm.prompt(filled.into()).await.map_err(|e| {
            McpError::internal_error(
                "llm_prompt",
                Some(json!({"err": e.to_string()})),
            )
        })?;

        let parsed: serde_json::Value =
            serde_json::from_str(&answer).map_err(|e| {
                McpError::internal_error(
                    "parse_score_response",
                    Some(json!({"err": e.to_string()})),
                )
            })?;

        Ok(CallToolResult::success(vec![Content::json(parsed).map_err(
            |e| {
                McpError::internal_error(
                    "score_reliability",
                    Some(json!({"err": e.to_string()})),
                )
            },
        )?]))
    }

    /// Suggest a diff to improve performance from current to target score
    #[tool(
        name = "fault_suggest_better_function_performance",
        description = "Generate a unified diff which improves the code's performance"
    )]
    async fn suggest_performance_improvement(
        &self,
        #[tool(param)]
        #[schemars(description = "Code block to review")]
        snippet: String,
        #[tool(param)]
        #[schemars(
            description = "Language of the code block: python, rust, go..."
        )]
        lang: String,
        #[tool(param)]
        #[schemars(
            description = "Current score for the code block: 0.0 (worst) to 1.0 (best)"
        )]
        score: f64,
        #[tool(param)]
        #[schemars(
            description = "Target score to try to reach from the changes: 0.0 (worst) to 1.0 (best)"
        )]
        target_score: f64,
    ) -> Result<CallToolResult, McpError> {
        let prompt =
            include_str!("../prompts/tool_suggest_perf_improvement.md");

        let filled = prompt
            .replace("{lang}", &lang)
            .replace("{snippet}", &snippet)
            .replace("{score}", &score.to_string())
            .replace("{target_score}", &target_score.to_string());

        let llm =
            get_client(self.llm_type, &self.prompt_model, &self.embed_model)
                .map_err(|e| {
                    McpError::internal_error(
                        "client_build",
                        Some(json!({"err": e.to_string()})),
                    )
                })?;

        let sp: Arc<dyn SimplePrompt> = llm.clone();
        let em: Arc<dyn EmbeddingModel> = llm.clone();

        let qdrant: Qdrant = Qdrant::builder()
            .batch_size(50)
            .vector_size(self.embed_model_dim)
            .with_vector(EmbeddedField::Combined)
            .with_sparse_vector(EmbeddedField::Combined)
            .collection_name(CODE_COLLECTION)
            .build()
            .map_err(|e| {
                McpError::internal_error(
                    "qdrant_builder",
                    Some(json!({"err": e.to_string()})),
                )
            })?;

        let pipeline = query::Pipeline::default()
            .then_transform_query(query_transformers::Embed::from_client(
                em.clone(),
            ))
            .then_retrieve(qdrant.clone())
            .then_answer(answers::Simple::from_client(sp.clone()));

        let q: String = filled.into();
        let resp = pipeline.query(q).await.map_err(|e| {
            McpError::internal_error(
                "query",
                Some(json!({"err": e.to_string()})),
            )
        })?;
        let diff = resp.answer().to_string();

        /*let diff = llm.prompt(filled.into()).await.map_err(|e| {
            McpError::internal_error(
                "llm_prompt",
                Some(json!({"err": e.to_string()})),
            )
        })?;*/

        Ok(CallToolResult::success(vec![Content::text(diff)]))
    }

    /// Suggest a diff to improve reliability from current to target score
    #[tool(
        name = "fault_suggest_better_function_reliability",
        description = "Generate a unified diff which improves the code's reliability"
    )]
    async fn suggest_reliability_improvement(
        &self,
        #[tool(param)]
        #[schemars(description = "Code block to review")]
        snippet: String,
        #[tool(param)]
        #[schemars(
            description = "Language of the code block: python, rust, go..."
        )]
        lang: String,
        #[tool(param)]
        #[schemars(
            description = "Current score for the code block: 0.0 (worst) to 1.0 (best)"
        )]
        score: f64,
        #[tool(param)]
        #[schemars(
            description = "Target score to try to reach from the changes: 0.0 (worst) to 1.0 (best)"
        )]
        target_score: f64,
    ) -> Result<CallToolResult, McpError> {
        let prompt =
            include_str!("../prompts/tool_suggest_reliability_improvement.md");

        let filled = prompt
            .replace("{lang}", &lang)
            .replace("{snippet}", &snippet)
            .replace("{score}", &score.to_string())
            .replace("{target_score}", &target_score.to_string());

        let llm =
            get_client(self.llm_type, &self.prompt_model, &self.embed_model)
                .map_err(|e| {
                    McpError::internal_error(
                        "client_build",
                        Some(json!({"err": e.to_string()})),
                    )
                })?;

        let sp: Arc<dyn SimplePrompt> = llm.clone();
        let em: Arc<dyn EmbeddingModel> = llm.clone();

        let qdrant: Qdrant = Qdrant::builder()
            .batch_size(50)
            .vector_size(self.embed_model_dim)
            .with_vector(EmbeddedField::Combined)
            .with_sparse_vector(EmbeddedField::Combined)
            .collection_name(CODE_COLLECTION)
            .build()
            .map_err(|e| {
                McpError::internal_error(
                    "qdrant_builder",
                    Some(json!({"err": e.to_string()})),
                )
            })?;

        let pipeline = query::Pipeline::default()
            .then_transform_query(query_transformers::Embed::from_client(
                em.clone(),
            ))
            .then_retrieve(qdrant.clone())
            .then_answer(answers::Simple::from_client(sp.clone()));

        let q: String = filled.into();
        let resp = pipeline.query(q).await.map_err(|e| {
            McpError::internal_error(
                "query",
                Some(json!({"err": e.to_string()})),
            )
        })?;
        let diff = resp.answer().to_string();

        /*
        let diff = llm.prompt(filled.into()).await.map_err(|e| {
            McpError::internal_error(
                "llm_prompt",
                Some(json!({"err": e.to_string()})),
            )
        })?;*/

        Ok(CallToolResult::success(vec![Content::text(diff)]))
    }

    /// Suggest changes for a whole file
    #[tool(
        name = "fault_make_reliability_and_perf_changes",
        description = "Generate a unified diff patch for a source code file to improve reliability and performance"
    )]
    async fn suggest_code_changes(
        &self,
        #[tool(param)]
        #[schemars(description = "Absolute local path to a code file")]
        file: String,
    ) -> Result<CallToolResult, McpError> {
        let prompt = include_str!(
            "../prompts/tool_suggest_complete_reliability_changeset.md"
        );

        let lang = guess_file_language(&file)?;

        let snippet = fs::read_to_string(&file).map_err(|e| {
            McpError::internal_error(
                "read_file",
                Some(json!({"err": e.to_string()})),
            )
        })?;

        let filled =
            prompt.replace("{lang}", &lang).replace("{snippet}", &snippet);

        let llm =
            get_client(self.llm_type, &self.prompt_model, &self.embed_model)
                .map_err(|e| {
                    McpError::internal_error(
                        "client_build",
                        Some(json!({"err": e.to_string()})),
                    )
                })?;

        let sp: Arc<dyn SimplePrompt> = llm.clone();
        let em: Arc<dyn EmbeddingModel>;

        if self.llm_type == SupportedLLMClient::OpenRouter {
            em = Arc::new(FastEmbed::try_default().unwrap().to_owned());
        } else {
            em = llm.clone();
        }

        let qdrant: Qdrant = Qdrant::builder()
            .batch_size(50)
            .vector_size(self.embed_model_dim)
            .with_vector(EmbeddedField::Combined)
            .with_sparse_vector(EmbeddedField::Combined)
            .collection_name(CODE_COLLECTION)
            .build()
            .map_err(|e| {
                McpError::internal_error(
                    "qdrant_builder",
                    Some(json!({"err": e.to_string()})),
                )
            })?;

        let pipeline = query::Pipeline::default()
            .then_transform_query(query_transformers::Embed::from_client(
                em.clone(),
            ))
            .then_retrieve(qdrant.clone())
            .then_answer(answers::Simple::from_client(sp.clone()));

        let q: String = filled.into();
        let resp = pipeline.query(q).await.map_err(|e| {
            McpError::internal_error(
                "query",
                Some(json!({"err": e.to_string()})),
            )
        })?;

        let answer = resp.answer().to_string();
        tracing::debug!("LLM replied with: {}", answer);

        let mut parsed = CodeChange::default();

        if let Some(code) = code::extract_json_fence(&answer) {
            parsed = serde_json::from_str(&code).map_err(|e| {
                McpError::internal_error(
                    "parse_code_change",
                    Some(json!({"err": e.to_string()})),
                )
            })?;

            let filename = Path::new(&file)
                .file_name()
                .and_then(|os_str| os_str.to_str())
                .unwrap();

            let old_text = snippet;
            let new_text = &parsed.new;
            let text_diff = TextDiff::from_lines(&old_text, &new_text);
            parsed.diff = text_diff
                .unified_diff()
                .context_radius(10)
                .header(filename, filename)
                .to_string();
        }

        Ok(CallToolResult::success(vec![Content::json(parsed).map_err(
            |e| {
                McpError::internal_error(
                    "sugget_changes",
                    Some(json!({"err": e.to_string()})),
                )
            },
        )?]))
    }

    #[tool(
        name = "fault_suggest_service_level_objectives_slo",
        description = "Generate valuable SLOs for a code snippet"
    )]
    async fn suggest_slo(
        &self,
        #[tool(param)]
        #[schemars(description = "Code block to review")]
        snippet: String,
        #[tool(param)]
        #[schemars(
            description = "Language of the code block: python, rust, go..."
        )]
        lang: String,
    ) -> Result<CallToolResult, McpError> {
        let prompt = include_str!("../prompts/tool_suggest_slo.md");

        let filled =
            prompt.replace("{lang}", &lang).replace("{snippet}", &snippet);

        let llm =
            get_client(self.llm_type, &self.prompt_model, &self.embed_model)
                .map_err(|e| {
                    McpError::internal_error(
                        "client_build",
                        Some(json!({"err": e.to_string()})),
                    )
                })?;
        let diff = llm.prompt(filled.into()).await.map_err(|e| {
            McpError::internal_error(
                "llm_prompt",
                Some(json!({"err": e.to_string()})),
            )
        })?;

        Ok(CallToolResult::success(vec![Content::text(diff)]))
    }

    #[tool(
        name = "fault_run_latency_impact_scenario",
        description = "Measure the impact of increased latency on response time"
    )]
    async fn run_latency_scenario(
        &self,
        #[tool(param)]
        #[schemars(description = "Endpoint URL")]
        url: String,
        #[tool(param)]
        #[schemars(description = "Endpoint HTTP method")]
        method: String,
        #[tool(param)]
        #[schemars(
            description = "JSON-encoded string to pass as a the body when method has one. Leave empty to not set it. When set, the content-type will be set to application/json."
        )]
        body: String,
        #[tool(param)]
        #[schemars(description = "Duration of the run: 10s, 30s, 1m...")]
        duration: String,
        #[tool(param)]
        #[schemars(
            description = "Latency to introduce in milliseconds, e.g. 300"
        )]
        latency: f64,
        #[tool(param)]
        #[schemars(
            description = "Latency standard deviation in milliseconds. Set 0 to stick to the latency without variation"
        )]
        deviation: f64,
        #[tool(param)]
        #[schemars(
            description = "Direction on which to apply the latency, one of ingress or egress. A good default is to use ingress."
        )]
        direction: String,
        #[tool(param)]
        #[schemars(
            description = "Network side on which applying the latency, one of client or server. A good default is to use server."
        )]
        side: String,
        #[tool(param)]
        #[schemars(
            description = "Apply the latency every time data is written or read on the stream. The default is to apply the fault once only over the entire course of the stream.."
        )]
        per_read_write_op: bool,
        #[tool(param)]
        #[schemars(description = "Number of concurrent clients, e..g. 1")]
        num_clients: usize,
        #[tool(param)]
        #[schemars(description = "Request per second, e.g. 2")]
        rps: usize,
        #[tool(param)]
        #[schemars(
            description = "Client timeout in seconds to apply on calls made to your application"
        )]
        timeout: u64,
        #[tool(param)]
        #[schemars(
            description = "List of mapping to map local ports to remote addresses. The target url will always be set by default but you can add more. Proxies look like: PORT=REMOTE_HOST"
        )]
        proxies: Vec<String>,
    ) -> Result<CallToolResult, McpError> {
        let stream_side = if side == "client".to_owned() {
            StreamSide::Client
        } else {
            StreamSide::Server
        };

        let fault = FaultConfiguration::Latency {
            distribution: Some("normal".to_string()),
            global: Some(!per_read_write_op),
            side: Some(stream_side),
            mean: Some(latency),
            stddev: Some(deviation),
            min: None,
            max: None,
            shape: None,
            scale: None,
            direction: Some(direction),
            period: None,
        };

        let report = run_scenario(
            url,
            method,
            body,
            duration,
            fault,
            num_clients,
            rps,
            timeout,
            proxies,
        )
        .await?;

        Ok(CallToolResult::success(vec![Content::text(report.render())]))
    }

    #[tool(
        name = "fault_run_jitter_impact_scenario",
        description = "Measure the impact of jitter on response time"
    )]
    async fn run_jitter_scenario(
        &self,
        #[tool(param)]
        #[schemars(description = "Endpoint URL")]
        url: String,
        #[tool(param)]
        #[schemars(description = "Endpoint HTTP method")]
        method: String,
        #[tool(param)]
        #[schemars(
            description = "JSON-encoded string to pass as a the body when method has one. Leave empty to not set it. When set, the content-type will be set to application/json."
        )]
        body: String,
        #[tool(param)]
        #[schemars(description = "Duration of the run: 10s, 30s, 1m...")]
        duration: String,
        #[tool(param)]
        #[schemars(description = "Amplitude in milliseconds, e.g. 100")]
        amplitude: f64,
        #[tool(param)]
        #[schemars(
            description = "Frequency per second (Hertz) to which the jitter should be applied, e.g. 3"
        )]
        frequency: f64,
        #[tool(param)]
        #[schemars(
            description = "Direction on which to apply the jitter, one of ingress or egress. A good default is to use ingress."
        )]
        direction: String,
        #[tool(param)]
        #[schemars(
            description = "Network side on which applying the jitter, one of client or server. A good default is to use server."
        )]
        side: String,
        #[tool(param)]
        #[schemars(description = "Number of concurrent clients, e..g. 1")]
        num_clients: usize,
        #[tool(param)]
        #[schemars(description = "Request per second, e.g. 2")]
        rps: usize,
        #[tool(param)]
        #[schemars(
            description = "Client timeout in seconds to apply on calls made to your application"
        )]
        timeout: u64,
        #[tool(param)]
        #[schemars(
            description = "List of mapping to map local ports to remote addresses. The target url will always be set by default but you can add more. Proxies look like: PORT=REMOTE_HOST"
        )]
        proxies: Vec<String>,
    ) -> Result<CallToolResult, McpError> {
        let stream_side = if side == "client".to_owned() {
            StreamSide::Client
        } else {
            StreamSide::Server
        };

        let fault = FaultConfiguration::Jitter {
            amplitude: amplitude,
            frequency: frequency,
            direction: Some(direction),
            side: Some(stream_side),
            period: None,
        };

        let report = run_scenario(
            url,
            method,
            body,
            duration,
            fault,
            num_clients,
            rps,
            timeout,
            proxies,
        )
        .await?;

        Ok(CallToolResult::success(vec![Content::text(report.render())]))
    }

    #[tool(
        name = "fault_run_bandwidth_impact_scenario",
        description = "Measure the impact of bandwidth constraints on response time and behavior"
    )]
    async fn run_bandwidth_scenario(
        &self,
        #[tool(param)]
        #[schemars(description = "Endpoint URL")]
        url: String,
        #[tool(param)]
        #[schemars(description = "Endpoint HTTP method")]
        method: String,
        #[tool(param)]
        #[schemars(
            description = "JSON-encoded string to pass as a the body when method has one. Leave empty to not set it. When set, the content-type will be set to application/json."
        )]
        body: String,
        #[tool(param)]
        #[schemars(description = "Duration of the run: 10s, 30s, 1m...")]
        duration: String,
        #[tool(param)]
        #[schemars(description = "Bandwidth rate to restrict traffic to: 300")]
        rate: u32,
        #[tool(param)]
        #[schemars(description = "Bandwidth limit: e.g. Kbps, Bps")]
        unit: String,
        #[tool(param)]
        #[schemars(
            description = "Direction on which to apply the bandwidth, one of ingress or egress. A good default is to use ingress."
        )]
        direction: String,
        #[tool(param)]
        #[schemars(
            description = "Network side on which applying the bandwidth, one of client or server. A good default is to use server."
        )]
        side: String,
        #[tool(param)]
        #[schemars(description = "Number of concurrent clients, e..g. 1")]
        num_clients: usize,
        #[tool(param)]
        #[schemars(description = "Request per second, e.g. 2")]
        rps: usize,
        #[tool(param)]
        #[schemars(
            description = "Client timeout in seconds to apply on calls made to your application"
        )]
        timeout: u64,
        #[tool(param)]
        #[schemars(
            description = "List of mapping to map local ports to remote addresses. The target url will always be set by default but you can add more. Proxies look like: PORT=REMOTE_HOST"
        )]
        proxies: Vec<String>,
    ) -> Result<CallToolResult, McpError> {
        let stream_side = if side == "client".to_owned() {
            StreamSide::Client
        } else {
            StreamSide::Server
        };

        let fault = FaultConfiguration::Bandwidth {
            rate: rate,
            unit: BandwidthUnit::from_str(&unit).unwrap_or_default(),
            direction: Some(direction),
            side: Some(stream_side),
            period: None,
        };

        let report = run_scenario(
            url,
            method,
            body,
            duration,
            fault,
            num_clients,
            rps,
            timeout,
            proxies,
        )
        .await?;

        Ok(CallToolResult::success(vec![Content::text(report.render())]))
    }

    #[tool(
        name = "fault_run_packet_loss_impact_scenario",
        description = "Measure the impact of packet loss on response time and behavior"
    )]
    async fn run_packet_loss_scenario(
        &self,
        #[tool(param)]
        #[schemars(description = "Endpoint URL")]
        url: String,
        #[tool(param)]
        #[schemars(description = "Endpoint HTTP method")]
        method: String,
        #[tool(param)]
        #[schemars(
            description = "JSON-encoded string to pass as a the body when method has one. Leave empty to not set it. When set, the content-type will be set to application/json."
        )]
        body: String,
        #[tool(param)]
        #[schemars(description = "Duration of the run: 10s, 30s, 1m...")]
        duration: String,
        #[tool(param)]
        #[schemars(
            description = "Direction on which to apply the packet loss, one of ingress or egress. A good default is to use ingress."
        )]
        direction: String,
        #[tool(param)]
        #[schemars(
            description = "Network side on which applying the packet loss, one of client or server. A good default is to use server."
        )]
        side: String,
        #[tool(param)]
        #[schemars(description = "Number of concurrent clients, e..g. 1")]
        num_clients: usize,
        #[tool(param)]
        #[schemars(description = "Request per second, e.g. 2")]
        rps: usize,
        #[tool(param)]
        #[schemars(
            description = "Client timeout in seconds to apply on calls made to your application"
        )]
        timeout: u64,
        #[tool(param)]
        #[schemars(
            description = "List of mapping to map local ports to remote addresses. The target url will always be set by default but you can add more. Proxies look like: PORT=REMOTE_HOST"
        )]
        proxies: Vec<String>,
    ) -> Result<CallToolResult, McpError> {
        let stream_side = if side == "client".to_owned() {
            StreamSide::Client
        } else {
            StreamSide::Server
        };

        let fault = FaultConfiguration::PacketLoss {
            direction: Some(direction),
            side: Some(stream_side),
            period: None,
        };

        let report = run_scenario(
            url,
            method,
            body,
            duration,
            fault,
            num_clients,
            rps,
            timeout,
            proxies,
        )
        .await?;

        Ok(CallToolResult::success(vec![Content::text(report.render())]))
    }

    #[tool(
        name = "fault_run_http_error_impact_scenario",
        description = "Measure the impact of HTTP error on response time and behavior"
    )]
    async fn run_http_error_scenario(
        &self,
        #[tool(param)]
        #[schemars(description = "Endpoint URL")]
        url: String,
        #[tool(param)]
        #[schemars(description = "Endpoint HTTP method")]
        method: String,
        #[tool(param)]
        #[schemars(
            description = "JSON-encoded string to pass as the request body when method has one. Leave empty to not set it. When set, the content-type will be set to application/json."
        )]
        body: String,
        #[tool(param)]
        #[schemars(
            description = "Probability, between 0.0 and 1.0, on how often the error is set."
        )]
        probability: f64,
        #[tool(param)]
        #[schemars(description = "Response status code.")]
        status_code: u16,
        #[tool(param)]
        #[schemars(description = "Response body to set.")]
        error_body: String,
        #[tool(param)]
        #[schemars(description = "Duration of the run: 10s, 30s, 1m...")]
        duration: String,
        #[tool(param)]
        #[schemars(description = "Number of concurrent clients, e..g. 1")]
        num_clients: usize,
        #[tool(param)]
        #[schemars(description = "Request per second, e.g. 2")]
        rps: usize,
        #[tool(param)]
        #[schemars(
            description = "Client timeout in seconds to apply on calls made to your application"
        )]
        timeout: u64,
        #[tool(param)]
        #[schemars(
            description = "List of mapping to map local ports to remote addresses. The target url will always be set by default but you can add more. Proxies look like: PORT=https://REMOTE_HOST:REMOTE_PORT"
        )]
        proxies: Vec<String>,
    ) -> Result<CallToolResult, McpError> {
        let fault = FaultConfiguration::HttpError {
            status_code: status_code,
            body: Some(error_body),
            probability: probability,
            period: None,
        };
        let report = run_scenario(
            url,
            method,
            body,
            duration,
            fault,
            num_clients,
            rps,
            timeout,
            proxies,
        )
        .await?;

        Ok(CallToolResult::success(vec![Content::text(report.render())]))
    }

    #[tool(
        name = "fault_run_blackhole_impact_scenario",
        description = "Measure the impact of network blackhole response time and behavior"
    )]
    async fn run_blackhole_scenario(
        &self,
        #[tool(param)]
        #[schemars(description = "Endpoint URL")]
        url: String,
        #[tool(param)]
        #[schemars(description = "Endpoint HTTP method")]
        method: String,
        #[tool(param)]
        #[schemars(
            description = "JSON-encoded string to pass as the request body when method has one. Leave empty to not set it. When set, the content-type will be set to application/json."
        )]
        body: String,
        #[tool(param)]
        #[schemars(
            description = "Direction on which to apply the packet loss, one of ingress or egress. A good default is to use ingress."
        )]
        direction: String,
        #[tool(param)]
        #[schemars(
            description = "Network side on which applying the packet loss, one of client or server. A good default is to use server."
        )]
        side: String,
        #[tool(param)]
        #[schemars(description = "Duration of the run: 10s, 30s, 1m...")]
        duration: String,
        #[tool(param)]
        #[schemars(description = "Number of concurrent clients, e..g. 1")]
        num_clients: usize,
        #[tool(param)]
        #[schemars(description = "Request per second, e.g. 2")]
        rps: usize,
        #[tool(param)]
        #[schemars(
            description = "Client timeout in seconds to apply on calls made to your application"
        )]
        timeout: u64,
        #[tool(param)]
        #[schemars(
            description = "List of mapping to map local ports to remote addresses. The target url will always be set by default but you can add more. Proxies look like: PORT=REMOTE_HOST"
        )]
        proxies: Vec<String>,
    ) -> Result<CallToolResult, McpError> {
        let stream_side = if side == "client".to_owned() {
            StreamSide::Client
        } else {
            StreamSide::Server
        };

        let fault = FaultConfiguration::Blackhole {
            direction: Some(direction),
            side: Some(stream_side),
            period: None,
        };

        let report = run_scenario(
            url,
            method,
            body,
            duration,
            fault,
            num_clients,
            rps,
            timeout,
            proxies,
        )
        .await?;

        Ok(CallToolResult::success(vec![Content::text(report.render())]))
    }

    #[tool(
        name = "fault_function_reliability_deep_analysis",
        description = "Deep evaluation of reliability anti-patterns of a function"
    )]
    async fn evaluate_code_lite(
        &self,
        #[tool(param)]
        #[schemars(description = "Source code file absolute path")]
        file: String,
        #[tool(param)]
        #[schemars(description = "Language of the file: python, rust, go...")]
        lang: String,
        #[tool(param)]
        #[schemars(description = "Function name to review")]
        func: String,
        #[tool(param)]
        #[schemars(
            description = "Concerns to focus on: performance, reliability, threat"
        )]
        concerns: Vec<String>,
    ) -> Result<CallToolResult, McpError> {
        let ext = Path::new(&file).extension().ok_or_else(|| {
            McpError::internal_error(
                "file_ext_not_found",
                Some(json!({"func": func.clone()})),
            )
        })?;

        let src = fs::read_to_string(&file).map_err(|e| {
            McpError::internal_error(
                "file_read",
                Some(json!({"err": e.to_string()})),
            )
        })?;

        let snippet =
            extract_function_snippet(&src, ext.to_str().unwrap(), &func)
                .ok_or_else(|| {
                    McpError::internal_error(
                        "func_not_found",
                        Some(json!({"func": func.clone()})),
                    )
                })?;

        let llm =
            get_client(self.llm_type, &self.prompt_model, &self.embed_model)
                .map_err(|e| {
                    McpError::internal_error(
                        "client_build",
                        Some(json!({"err": e.to_string()})),
                    )
                })?;

        let templates = vec![
            ("performance", PERFORMANCE_TEMPLATE),
            ("reliability", RELIABILITY_TEMPLATE),
            ("threat", SCENARIO_TEMPLATE),
        ];

        let mut results: Vec<String> = Vec::new();
        let mut prompts = Vec::new();

        for (angle, tmpl) in templates {
            if !concerns.is_empty() {
                if !concerns.contains(&angle.to_string()) {
                    continue;
                }
            }

            let prompt = tmpl
                .replace("{file}", &file)
                .replace("{func}", &func)
                .replace("{snippet}", &snippet.full)
                .replace("{lang}", &lang);

            prompts.push(prompt.clone());

            let answer = llm.prompt(prompt.into()).await.map_err(|e| {
                McpError::internal_error(
                    "llm_prompt",
                    Some(json!({"err": e.to_string()})),
                )
            })?;

            results.push(answer);
        }

        let payload = json!({ "evaluations": results , "prompts": prompts });

        Ok(CallToolResult::success(vec![Content::text(payload.to_string())]))
    }
}

#[tool(tool_box)]
impl ServerHandler for FaultMCP {
    fn get_info(&self) -> ServerInfo {
        ServerInfo {
            instructions: Some("Senior AI Agent for your operations".into()),
            capabilities: ServerCapabilities::builder().enable_tools().build(),
            ..Default::default()
        }
    }
}

async fn run_scenario(
    url: String,
    method: String,
    body: String,
    duration: String,
    fault: FaultConfiguration,
    num_clients: usize,
    rps: usize,
    timeout: u64,
    proxies: Vec<String>,
) -> Result<Report, McpError> {
    let components = Url::parse(&url.clone()).map_err(|e| {
        McpError::internal_error(
            "parse_url",
            Some(json!({"err": e.to_string()})),
        )
    })?;

    let scheme = components.scheme();

    let host = components
        .host_str()
        .ok_or(McpError::internal_error("extract_url_host", None))?;

    let port = components
        .port_or_known_default()
        .ok_or(McpError::internal_error("extract_url_port", None))?;

    let origin = format!("{}://{}:{}", scheme, host, port);

    let headers = if !body.is_empty() {
        let mut h = HashMap::<String, String>::new();
        let _ =
            h.insert("content-type".to_owned(), "application/json".to_owned());
        Some(h)
    } else {
        None
    };

    let mut disable_http_proxies = false;
    let mut proxies_mapping = Vec::<String>::new();
    if !proxies.is_empty() {
        disable_http_proxies = true;
        proxies_mapping.extend(proxies);
    } else {
        // only apply this proxy when no other proxying was provided
        // I chose here to only apply the faults to calls made to the app
        // when no other specific proxies were set. When they are set, this
        // is an explicit configuration I want to respect
        proxies_mapping.push(format!("{}={}", 3180, origin));
    }

    let s = Scenario {
        title: format!("Evaluating runtime performance of {}", url.clone()),
        description: None,
        items: vec![ScenarioItem {
            call: ScenarioItemCall {
                method: method,
                url: url,
                headers: headers,
                body: (!body.is_empty()).then(|| body),
                timeout: Some(timeout * 1000u64),
                meta: None,
            },
            context: ScenarioItemContext {
                upstreams: vec![],
                faults: vec![fault],
                strategy: Some(ScenarioItemCallStrategy::Load {
                    duration: duration,
                    clients: num_clients,
                    rps: rps,
                }),
                slo: Some(vec![
                    ScenarioItemSLO {
                        slo_type: "latency".to_string(),
                        title: "99% @ 350ms".to_string(),
                        objective: 99.0,
                        threshold: 350.0,
                    },
                    ScenarioItemSLO {
                        slo_type: "latency".to_string(),
                        title: "95% @ 200ms".to_string(),
                        objective: 95.0,
                        threshold: 200.0,
                    },
                ]),
                proxy: Some(ScenarioItemProxySettings {
                    disable_http_proxies: disable_http_proxies,
                    proxies: proxies_mapping,
                }),
                runs_on: None,
            },
            expect: None,
        }],
        config: None,
    };

    tracing::debug!("Applying scenario from MCP tool {:?}", s);

    let results = run_scenario_first_item(s).await.map_err(|e| {
        McpError::internal_error(
            "run_scenario",
            Some(json!({"err": e.to_string()})),
        )
    })?;

    let report = report::builder::to_report(&results);

    Ok(report)
}
