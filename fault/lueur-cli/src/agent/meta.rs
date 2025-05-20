use std::fmt;

use crate::report::types::Report;

#[derive(Debug, Clone, PartialEq)]
pub struct Meta {
    pub method: String,
    pub opid: String,
    pub path: String,
}

impl fmt::Display for Meta {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} [{} {}]", self.opid, self.method, self.path)
    }
}

pub fn get_metas(report: &Report) -> Vec<Meta> {
    let mut pairs = Vec::<Meta>::new();

    for scenario in &report.scenario_summaries {
        for item in &scenario.item_summaries {
            if let Some(meta) = &item.meta {
                if let Some(opid) = &meta.operation_id {
                    let m = Meta {
                        method: item.call.method.clone(),
                        opid: opid.clone(),
                        path: item.call.url.clone(),
                    };

                    if !pairs.contains(&m) {
                        pairs.push(m);
                    }
                }
            }
        }
    }

    pairs
}
