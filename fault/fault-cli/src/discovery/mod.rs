use std::collections::HashSet;
use std::collections::VecDeque;

pub(crate) mod aws;
pub(crate) mod gcp;
pub(crate) mod k8s;
pub(crate) mod types;

use crate::discovery::types::Resource;

pub fn get_resource_graph(
    resources: &[Resource],
    root: &Resource,
) -> Vec<Resource> {
    let mut result = Vec::new();
    let mut visited = HashSet::new();
    let mut queue = VecDeque::new();

    // seed with the root node
    visited.insert(root.id.clone());
    queue.push_back(root.id.clone());

    while let Some(cur_id) = queue.pop_front() {
        // look up the Resource by id
        if let Some(res) = resources.iter().find(|r| r.id == cur_id) {
            // collect it
            result.push(res.clone());

            // enqueue any linked resources we haven't seen yet
            for link in &res.links {
                if visited.insert(link.id.clone()) {
                    queue.push_back(link.id.clone());
                }
            }
        }
    }

    result
}
