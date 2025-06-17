use std::fs;
use std::path::Path;
use std::sync::Arc;

use rmcp::Error as McpError;
use rmcp::ServerHandler;
use rmcp::model::CallToolResult;
use rmcp::model::Content;
use rmcp::model::GetPromptRequestParam;
use rmcp::model::GetPromptResult;
use rmcp::model::PromptMessage;
use rmcp::model::PromptMessageContent;
use rmcp::model::PromptMessageRole;
use rmcp::model::ServerCapabilities;
use rmcp::model::ServerInfo;
use rmcp::schemars;
use rmcp::service::RequestContext;
use rmcp::service::RoleServer;
use rmcp::tool;
use serde::Deserialize;
use serde::Serialize;
use serde_json::json;
use swiftide::indexing::EmbeddedField;
use swiftide::integrations::qdrant::Qdrant;
use swiftide::query;
use swiftide::query::answers;
use swiftide::query::query_transformers;
use swiftide_core::EmbeddingModel;
use swiftide_core::SimplePrompt;

use crate::agent::CODE_COLLECTION;
use crate::agent::clients::SupportedLLMClient;
use crate::agent::clients::get_client;
use crate::agent::mcp::code;
use crate::agent::mcp::code::extract_function_snippet;
use crate::agent::mcp::code::list_functions;

#[derive(Serialize, Deserialize, schemars::JsonSchema)]
pub struct CodeBlock {
    #[schemars(
        description = "full function block, including its signature and outter decorators"
    )]
    pub full: String,
    #[schemars(description = "full function body only")]
    pub body: String,
}

#[derive(Default, Clone)]
pub struct FaultMCP {
    pub llm_type: SupportedLLMClient,
    pub prompt_model: String,
    pub embed_model: String,
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
    ) -> Self {
        Self {
            llm_type,
            prompt_model: prompt_model.into(),
            embed_model: embed_model.into(),
        }
    }

    #[tool(
        name = "extract.function_names",
        description = "List all function names in the given file"
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
        name = "source.index",
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
        name = "extract.code_block",
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
        name = "score.performance",
        description = "Compute performance score"
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
        name = "score.reliability",
        description = "Compute reliability score"
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
        name = "suggest.performance_improvement",
        description = "Generate a unified diff to improve the function's performance"
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
            .vector_size(1536)
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
        name = "suggest.reliability_improvement",
        description = "Generate a unified diff to improve the function's reliability"
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
            .vector_size(1536)
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

    #[tool(
        name = "suggest.slos",
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

        let filled = prompt
            .replace("{lang}", &lang)
            .replace("{snippet}", &snippet);

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
        name = "analysis.reliability",
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
            instructions: Some("A simple calculator".into()),
            capabilities: ServerCapabilities::builder()
                .enable_tools()
                .enable_prompts()
                .build(),
            ..Default::default()
        }
    }

    async fn get_prompt(
        &self,
        GetPromptRequestParam { name, arguments }: GetPromptRequestParam,
        _: RequestContext<RoleServer>,
    ) -> Result<GetPromptResult, McpError> {
        match name.as_str() {
            "example_prompt" => {
                let message = arguments
                    .and_then(|json| {
                        json.get("message")?.as_str().map(|s| s.to_string())
                    })
                    .ok_or_else(|| {
                        McpError::invalid_params(
                            "No message provided to example_prompt",
                            None,
                        )
                    })?;

                let prompt = format!(
                    "This is an example prompt with your message here: '{message}'"
                );
                Ok(GetPromptResult {
                    description: None,
                    messages: vec![PromptMessage {
                        role: PromptMessageRole::User,
                        content: PromptMessageContent::text(prompt),
                    }],
                })
            }
            _ => Err(McpError::invalid_params("prompt not found", None)),
        }
    }
}
