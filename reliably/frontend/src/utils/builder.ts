
import {
  fetchRelatedActionTemplates,
} from "@/stores/templates";

import { experiment, fetchExperiment } from "@/stores/experiments";

import type { Template, RelatedActivity } from "@/types/templates";
import type {
  ExperimentDefinition,
  Runtime,
  EnvConfiguration,
  PythonProvider,
  Extension,
} from "@/types/experiments";
import type {
  Activity,
  TemplateActivity,
  BuilderWorkflow,
  ChatGptExtension,
} from "@/types/ui-types";

export function defineMode(): {
  type: "build" | "edit";
  id: string;
} | null {
  let location = window.location;
  let params = new URLSearchParams(location.search);
  if (params.has("activity")) {
    return {
      type: "build",
      id: params.get("activity")!,
    };
  } else if (params.has("edit")) {
    return {
      type: "edit",
      id: params.get("edit")!,
    };
  } else {
    return null;
  }
}

// export async function getTemplateFromId(id: string) {
//   let location = window.location;
//   let params = new URLSearchParams(location.search);
//   if (params.has("activity")) {
//     const id: string = params.get("activity")!;
//     await fetchActionTemplate(id);
//   }
// }

export async function setExperimentFromId(id: string) {
  await fetchExperiment(id);
  const exp = experiment.get();

  let d: ExperimentDefinition | null = null;
  let w: BuilderWorkflow | null = null;
  let total: number = 0;

  if (exp) {
    d = structuredClone(exp.definition);
    const i = d.extensions?.findIndex((ext) => {
      return ext.name === "reliablyui";
    });
    if (i !== undefined && i > -1) {
      w = d.extensions![i].workflow;
    }
  }
  if (w) {
    total =
      w.hypothesis.length +
      w.warmup.length +
      w.method.length +
      w.rollbacks.length;
  }
  return { d, w, total };
}

export function getActivityMeta(activity: TemplateActivity): Activity {
  const metadata = activity.template.manifest.metadata;
  const template = activity.template.manifest.spec.template;

  const id = metadata.name;
  const name = metadata.name;
  const target = metadata.labels[0];
  const category = metadata.labels[metadata.labels.length - 1];
  let type = "";
  const description = template.title;
  let module = "";

  if (template.method && template.method.length) {
    type = template.method[0].type;
  } else if (
    template["steady-state-hypothesis"] &&
    template["steady-state-hypothesis"].probes &&
    template["steady-state-hypothesis"].probes.length
  ) {
    type = template["steady-state-hypothesis"].probes[0].type;
  } else if (template.rollbacks && template.rollbacks.length) {
    type = template.rollbacks[0].type;
  }
  module = type;

  return {
    id: id,
    name: name,
    target: target,
    category: category,
    type: type,
    description: description,
    module: module,
  };
}

export async function setExperimentFromTemplate(template: Template | null) {
  let e: ExperimentDefinition | null = null;
  let type: "method" | "hypothesis" | "rollbacks" = "method";

  if (template !== null) {
    e = structuredClone(template.manifest.spec.template);

    if (e["steady-state-hypothesis"] === undefined) {
      e["steady-state-hypothesis"] = {
        title: "Steady-State Hypothesis",
        probes: [],
      };
    }
    if (e.method === undefined) {
      e.method = [];
    }
    if (e.rollbacks === undefined) {
      e.rollbacks = [];
    }

    type = getStarterType(e);

    Object.keys(e.configuration!).forEach((k) => {
      // We're suffixing experiment configuration entries
      // and corresponding method arguments
      const tmp = e!.configuration![k];
      let newKey: string = `${k}_M001`;
      if (type === "hypothesis") {
        newKey = `${k}_H001`;
      } else if (type === "rollbacks") {
        newKey = `${k}_R001`;
      }
      e!.configuration![newKey] = tmp;
      delete e!.configuration![k];
      let value: string = "";
      if (type === "method") {
        value = (
          e!.method![0].provider.arguments! as {
            [key: string]: string;
          }
        )[k]; // Looks like "${something}"
      } else if (type === "hypothesis") {
        value = (
          e!["steady-state-hypothesis"]?.probes![0].provider.arguments! as {
            [key: string]: string;
          }
        )[k];
      } else if (type === "rollbacks") {
        value = (
          e!.rollbacks![0].provider.arguments! as {
            [key: string]: string;
          }
        )[k];
      }

      if (type === "method") {
        const newValue = [
          value.slice(0, value.length - 1),
          "_M001",
          value.slice(value.length - 1),
        ].join(""); // Looks like "${something_M001}"
        (
          e!.method![0].provider.arguments! as {
            [key: string]: string;
          }
        )[k] = newValue;
      } else if (type === "hypothesis") {
        const newValue = [
          value.slice(0, value.length - 1),
          "_H001",
          value.slice(value.length - 1),
        ].join(""); // Looks like "${something_H001}"
        (
          e!["steady-state-hypothesis"]?.probes![0].provider.arguments! as {
            [key: string]: string;
          }
        )[k] = newValue;
      } else if (type === "rollbacks") {
        const newValue = [
          value.slice(0, value.length - 1),
          "_R001",
          value.slice(value.length - 1),
        ].join(""); // Looks like "${something_R001}"
        (
          e!.rollbacks![0].provider.arguments! as {
            [key: string]: string;
          }
        )[k] = newValue;
      }
    });

    e.runtime = setExperimentRuntime(e);
  }

  return { e, type };
}

export async function getRelatedActivities(
  template: Template | null
): Promise<RelatedActivity[]> {
  let activities: RelatedActivity[] = [];
  if (template !== null) {
    if (template.manifest.spec.related) {
      template.manifest.spec.related.forEach((a: RelatedActivity) => {
        activities.push({
          name: a.name,
          block: a.block,
        });
      });
      await fetchRelatedActionTemplates(activities);
    }
  }
  return activities;
}
/*
 * postProcessExperiment() delete the method arguments for which the
 * configuration environment variable provides no default value.
 * It also deletes the environment variable.
 * This aims at preventing unwanted behaviours when Chaos Toolkit runs the
 * experiment and expects a null value when no default is set, while maintaining
 * the Reliably app behaviour of not setting a default value to null when none
 * is provided.
 * IT SHOULD ONLY BE CALLED WHEN THE TEMPLATE HAS BEEN CALLED FROM A STARTER,
 * that is if action.value !== null and id.value === undefined
 * (one should never go without the other).
 */
export function postProcessExperiment(
  e: ExperimentDefinition
): ExperimentDefinition {
  if (e.configuration !== undefined) {
    const keys = Object.keys(e.configuration);
    const keysCopy = [...keys];
    const ssh = e["steady-state-hypothesis"];
    const method = e.method;
    const rollbacks = e.rollbacks;
    const activitiesArray = [];
    if (ssh !== undefined && ssh.probes !== undefined && ssh.probes.length) {
      activitiesArray.push(...ssh.probes);
    }
    if (method !== undefined && method.length) {
      activitiesArray.push(...method);
    }
    if (rollbacks !== undefined && rollbacks?.length) {
      activitiesArray.push(...rollbacks);
    }
    activitiesArray.forEach((a) => {
      const args = a.provider.arguments;
      if (args !== undefined) {
        keysCopy.forEach((key) => {
          if (
            e.configuration![key] &&
            (e.configuration![key] as EnvConfiguration).default === undefined
          ) {
            delete (args as { [key: string]: string })[key];
            delete e.configuration![key];
          }
        });
      }
    });
  }
  return e;
}

/* addExperimentWorkflow saves the experiment workflow to the reliablyui
 * extension so it can be used when editing the experiment
 */
export function addExperimentWorkflow(
  e: ExperimentDefinition,
  w: BuilderWorkflow
) {
  if (e.extensions === undefined) {
    e.extensions = [];
  }
  let i: number = e.extensions.findIndex((ext) => {
    return ext.name === "reliablyui";
  });
  if (i === -1) {
    e.extensions.push({ name: "reliablyui" });
    i = e.extensions.length - 1;
  }
  e.extensions[i].workflow = {
    hypothesis: w.hypothesis,
    warmup: w.warmup,
    method: w.method,
    rollbacks: w.rollbacks,
  } as BuilderWorkflow;
}

// Returns a full activity ID from a provider object
export function getActivityId(provider: PythonProvider): string {
  const name = provider.func;
  const module = provider.module.split(".");
  const target = module[0].startsWith("chaos") ? module[0].slice(5) : module[0];
  const service = module[1];
  return `${target}-${service}-${name}`;
}

export function addAssistantQuestions(
  template: Template,
  experiment: ExperimentDefinition
) {
  const extensions = template.manifest.spec.template.extensions;
  if (extensions) {
    const chatgpt = extensions.find((e: Extension) => {
      return e.name === "chatgpt";
    });
    if (chatgpt) {
      const messages = (chatgpt as ChatGptExtension).messages;
      const existingExtensions = experiment.extensions;
      if (existingExtensions) {
        // Existing experiment already has an extensions block
        const existingGpt = existingExtensions.findIndex((e) => {
          return (e.name = "chatgpt");
        });
        if (existingGpt > -1) {
          // Existing experiment already has a ChatGPT block
          if (
            (experiment.extensions![existingGpt] as ChatGptExtension).messages
              .length
          ) {
            // Existing experiment already has questions
            messages.forEach((message) => {
              const index = (
                experiment.extensions![existingGpt] as ChatGptExtension
              ).messages.findIndex((m) => {
                return m.content === message.content;
              });
              if (index === -1) {
                (
                  experiment.extensions![existingGpt] as ChatGptExtension
                ).messages.push(message);
              }
            });
          } else {
            (
              experiment.extensions![existingGpt] as ChatGptExtension
            ).messages.push(...messages);
          }
        } else {
          experiment.extensions?.push(chatgpt);
        }
      } else {
        experiment.extensions = [chatgpt];
      }
    }
  }
}

// Not exported
function getStarterType(
  experiment: ExperimentDefinition
): "method" | "hypothesis" | "rollbacks" {
  let type: "method" | "hypothesis" | "rollbacks" = "method";
  if (experiment.method === undefined || experiment.method.length === 0) {
    if (
      experiment["steady-state-hypothesis"] !== undefined &&
      experiment["steady-state-hypothesis"].probes!.length
    ) {
      return "hypothesis";
    } else if (
      experiment.rollbacks !== undefined &&
      experiment.rollbacks.length
    ) {
      return "rollbacks";
    }
  }
  return type;
}

function setExperimentRuntime(experiment: ExperimentDefinition): Runtime {
  const defaultRuntime: Runtime = {
    hypothesis: {
      strategy: "default",
      frequency: 1,
      fail_fast: false,
    },
    rollbacks: {
      strategy: "default",
    },
  };
  if (
    experiment.runtime === undefined ||
    Object.keys(experiment.runtime).length === 0
  ) {
    return defaultRuntime;
  } else {
    let runtime: Runtime = JSON.parse(JSON.stringify(experiment.runtime));
    if (!runtime.rollbacks) {
      runtime.rollbacks = defaultRuntime.rollbacks;
    } else {
      if (runtime.rollbacks.strategy === undefined) {
        runtime.rollbacks!.strategy = defaultRuntime.rollbacks!.strategy;
      }
    }

    if (!runtime.hypothesis) {
      runtime.hypothesis = defaultRuntime.hypothesis;
    } else {
      if (runtime.hypothesis.strategy === undefined) {
        runtime.hypothesis!.strategy = defaultRuntime.hypothesis!.strategy;
      }
      if (runtime.hypothesis.frequency === undefined) {
        runtime.hypothesis.frequency = defaultRuntime.hypothesis!.frequency;
      }
      if (runtime.hypothesis.fail_fast === undefined) {
        runtime.hypothesis.fail_fast = defaultRuntime.hypothesis!.fail_fast;
      }
    }
    return runtime;
  }
}
