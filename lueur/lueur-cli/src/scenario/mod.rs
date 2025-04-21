use std::path::Path;
use std::pin::Pin;

use async_stream::stream;
use serde::Deserialize;
use serde_yaml::Deserializer;
use tokio::fs::File;
use tokio::io::AsyncReadExt;
use tokio_stream::Stream;
use types::Scenario;
use types::ScenarioItem;
use types::ScenarioItemCallStrategy;
use walkdir::WalkDir;

use crate::errors::ScenarioError;

pub(crate) mod event;
pub(crate) mod executor;
pub(crate) mod generator;
pub(crate) mod strategy;
pub(crate) mod types;

pub fn count_scenario_items(scenario: &Scenario) -> u64 {
    let mut total_count = 0;

    for item in scenario.items.iter() {
        let strategy = item.context.strategy.clone();
        if let Some(strategy) = strategy {
            match strategy {
                ScenarioItemCallStrategy::Repeat {
                    count,
                    add_baseline_call,
                    ..
                } => {
                    total_count += count;
                    if add_baseline_call.is_some_and(|x| x) {
                        total_count += 1;
                    }
                }
                ScenarioItemCallStrategy::Load { .. } => {
                    total_count += 1;
                }
                ScenarioItemCallStrategy::Single {} => {
                    total_count += 1;
                }
            }
        } else {
            total_count += 1;
        }
    }

    total_count as u64
}

pub fn load_scenarios(
    dir_path: &Path,
) -> Pin<Box<dyn Stream<Item = Result<Scenario, ScenarioError>> + Send>> {
    let dir_path = dir_path.to_owned();

    let scenario_stream = stream! {
        tracing::info!("Loading scenario files from directory {:?}", dir_path);

        let paths = match tokio::task::spawn_blocking(move || {
            WalkDir::new(&dir_path)
                .into_iter()
                .filter_map(|entry| match entry {
                    Ok(e) => {
                        let path = e.path();
                        if e.file_type().is_file()
                            && path.extension().is_some_and(|ext| {
                                ext.eq_ignore_ascii_case("yaml") || ext.eq_ignore_ascii_case("yml")
                            })
                        {
                            Some(path.to_owned())
                        } else {
                            None
                        }
                    },
                    Err(_) => {
                        None
                    }
                })
                .collect::<Vec<_>>()
        }).await {
            Ok(paths) => paths,
            Err(e) => {
                yield Err(ScenarioError::WalkDirError(e.to_string()));
                return;
            }
        };

        for path in paths {
            let path_clone = path.clone();
            tracing::info!("Loading scenarios from {:?}", path_clone);

            match File::open(&path_clone).await {
                Ok(mut file) => {
                    let mut contents = String::new();

                    match file.read_to_string(&mut contents).await {
                        Ok(_) => {
                            let scenarios_result = tokio::task::spawn_blocking(move || {
                                let mut docs = Vec::new();
                                for document in Deserializer::from_str(&contents) {
                                    let doc = Scenario::deserialize(document);
                                    docs.push(doc);
                                }
                                docs
                            }).await;

                            match scenarios_result {
                                Ok(scenarios) => {
                                    for scenario in scenarios {
                                        match scenario {
                                            Ok(s) => yield Ok(s),
                                            Err(e) => yield Err(ScenarioError::ParseError(
                                                path_clone.to_string_lossy().to_string(),
                                                e.to_string()
                                            )),
                                        }
                                    }
                                },
                                Err(e) => {
                                    yield Err(ScenarioError::ReadError(
                                        path_clone.to_string_lossy().to_string(),
                                        e.to_string(),
                                    ));
                                }
                            }
                        },
                        Err(e) => {
                            yield Err(ScenarioError::ReadError(
                                path_clone.to_string_lossy().to_string(),
                                e.to_string()
                            ));
                        }
                    }
                },
                Err(e) => {
                    yield Err(ScenarioError::ReadError(
                        path_clone.to_string_lossy().to_string(),
                        e.to_string()
                    ));
                }
            }
        }
    };

    Box::pin(scenario_stream)
}
