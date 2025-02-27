export function formatDeploymentType(t: string): string {
  if (t === "github") {
    return "[GitHub]";
  } else if (t === "reliably_cloud") {
    return "[Reliably Cloud]";
  } else if (t === "reliably_cli") {
    return "[Reliably CLI]";
  } else if (t === "container") {
    return "[Docker]";
  } else if (t === "k8s_job") {
    return "[Kubernetes]";
  } else {
    return `[${t}]`;
  }
}
