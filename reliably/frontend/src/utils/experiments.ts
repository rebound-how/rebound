import type {
  ExperimentDefinition,
  Secret,
  EnvSecret,
  VaultSecret,
  Extension,
  Control,
  PythonProvider,
  HttpProvider,
  ProcessProvider,
  Probe,
  Action,
} from "@/types/experiments";

import { hasProp } from "./objects";

export function checkExperiment(object: Object): string {
  if (!checkTitle(object)) {
    return "<code>title</code> property is missing or invalid";
  }
  if (!checkDescription(object)) {
    return "<code>description</code> property is missing or invalid";
  }
  if (!checkContributions(object)) {
    return "<code>contributions</code> property is invalid";
  }
  if (!checkTags(object)) {
    return "<code>tags</code> property is invalid";
  }
  if (!checkConfiguration(object)) {
    return "<code>configuration</code> property is invalid";
  }
  if (!checkSecrets(object)) {
    return "<code>secrets</code> property is invalid";
  }
  if (!checkExtensions(object)) {
    return "<code>extensions</code> property is invalid";
  }
  if (!checkControls(object)) {
    return "<code>controls</code> property is invalid";
  }
  if (!checkSsh(object)) {
    return "<code>steady-state-hypothesis</code> property is invalid";
  }
  if (!checkMethod(object)) {
    return "<code>method</code> property is missing or invalid";
  }
  if (!checkRollbacks(object)) {
    return "<code>rollbacks</code> property is missing or invalid";
  }

  return "";
}

// There must be a title, and it must be a string
function checkTitle(object: Object): boolean {
  if (hasProp(object, "title")) {
    return (
      typeof (object as ExperimentDefinition).title === "string" &&
      (object as ExperimentDefinition).title !== ""
    );
  }
  return false;
}

// There must be a description, and it must be a string
function checkDescription(object: Object): boolean {
  if (hasProp(object, "description")) {
    return (
      typeof (object as ExperimentDefinition).description === "string" &&
      (object as ExperimentDefinition).description !== ""
    );
  }
  return false;
}

// Contributions object
function checkContributions(object: Object): boolean {
  const validContributions: string[] = ["none", "low", "medium", "high"];
  if (hasProp(object, "contributions")) {
    let contributions = (object as ExperimentDefinition).contributions;
    if (contributions !== undefined) {
      for (const [key, value] of Object.entries(contributions!)) {
        if (!validContributions.includes(value)) {
          return false;
        }
      }
    }
  }
  return true;
}

// If there are tags, it must be a string array
function checkTags(object: Object): boolean {
  if (hasProp(object, "tags")) {
    if (!Array.isArray((object as ExperimentDefinition).tags)) {
      return false;
    }
    let areTagsValid: boolean = true;
    (object as ExperimentDefinition).tags!.every((tag) => {
      if (typeof tag !== "string") {
        areTagsValid = false;
        return false;
      }
      return true;
    });
    if (!areTagsValid) {
      return false;
    }
  }
  return true;
}

// Configuration is optional
// If it's present, it must be an JSON object
// Each value must be either a string or a JSON object
function checkConfiguration(object: Object): boolean {
  if (hasProp(object, "configuration")) {
    let conf = (object as ExperimentDefinition).configuration;
    if (conf !== undefined) {
      if (typeof conf !== "object") {
        return false;
      } else {
        for (const [key, value] of Object.entries(conf)) {
          if (
            typeof value !== "string" &&
            typeof value !== "number" &&
            typeof value !== "boolean" &&
            typeof value !== "object"
          ) {
            return false;
          }
        }
      }
    }
  }
  return true;
}

// Secrets are optional
// If they're present, it must be an JSON object
// Each value must be either a string, or a Env Secret, or a Vault Secret
function checkSecrets(object: Object): boolean {
  if (hasProp(object, "secrets")) {
    const s = (object as ExperimentDefinition).secrets;
    if (typeof s !== "object") {
      return false;
    } else {
      const keys: string[] = Object.keys(s);
      let areSecretsValid: boolean = true;
      keys.every((key) => {
        const secret = s[key];
        if (typeof secret !== "object") {
          areSecretsValid = false;
          return false;
        }
        const secretKeys = Object.keys(secret);
        secretKeys.every((k) => {
          if (
            !isInlineSecret(secret[k]) &&
            !isEnvSecret(secret[k]) &&
            !isVaultSecret(secret[k])
          ) {
            areSecretsValid = false;
            return false;
          }
          return true;
        });
        return areSecretsValid;
      });
      if (!areSecretsValid) {
        return false;
      }
    }
  }
  return true;
}

function isInlineSecret(object: Object): boolean {
  const t: string = typeof object;
  return t === "string" || t === "boolean" || t === "number";
}

function isEnvSecret(object: Object): boolean {
  if (typeof object !== "object") {
    return false;
  }
  const keys: string[] = Object.keys(object);
  let isValid: boolean = true;
  keys.every((k) => {
    if (k === "type") {
      if ((object as EnvSecret).type !== "env") {
        isValid = false;
        return false;
      } else {
        return true;
      }
    } else if (k === "key") {
      if (typeof (object as EnvSecret).key !== "string") {
        isValid = false;
        return false;
      } else {
        return true;
      }
    } else {
      isValid = false;
      return false;
    }
  });
  return isValid;
}

function isVaultSecret(object: Object): boolean {
  if (typeof object !== "object") {
    return false;
  }
  const keys: string[] = Object.keys(object);
  let isValid: boolean = true;
  keys.every((k) => {
    if (k === "type") {
      if ((object as VaultSecret).type !== "vault") {
        isValid = false;
        return false;
      } else {
        return true;
      }
    } else if (k === "path") {
      if (typeof (object as VaultSecret).path !== "string") {
        isValid = false;
        return false;
      } else {
        return true;
      }
    } else {
      isValid = false;
      return false;
    }
  });
  return isValid;
}

// Extensions are optional
function checkExtensions(object: Object): boolean {
  if (hasProp(object, "extensions")) {
    let extensions = (object as ExperimentDefinition).extensions;
    if (extensions !== undefined) {
      if (!Array.isArray(extensions)) {
        return false;
      }
      let areExtensionsValid: boolean = true;
      extensions.every((extension: Extension) => {
        if (!hasProp(extension, "name")) {
          areExtensionsValid = false;
          return false;
        }
        return true;
      });
      if (!areExtensionsValid) {
        return false;
      }
    }
  }
  return true;
}

// Controls are optional
function checkControls(object: Object): boolean {
  if (hasProp(object, "controls")) {
    let controls = (object as ExperimentDefinition).controls;
    if (controls !== undefined) {
      if (!Array.isArray(controls)) {
        return false;
      }
      let areControlsValid: boolean = true;
      controls.every((control: Control) => {
        if (!hasProp(control, "name")) {
          areControlsValid = false;
          return false;
        } else if (typeof control.name !== "string") {
          areControlsValid = false;
          return false;
        }
        if (!hasProp(control, "provider")) {
          areControlsValid = false;
          return false;
        } else if (!isControlProvider(control.provider)) {
          areControlsValid = false;
          return false;
        }
        if (hasProp(control, "scope")) {
          if (control.scope !== "before" && control.scope !== "after") {
            areControlsValid = false;
            return false;
          }
        }
        if (hasProp(control, "automatic")) {
          if (typeof control.automatic !== "boolean") {
            areControlsValid = false;
            return false;
          }
        } else return true;
      });
      if (!areControlsValid) {
        return false;
      }
    }
  }
  return true;
}

// Provider for Controls
function isControlProvider(object: Object): boolean {
  if (!hasProp(object, "type")) {
    return false;
  } else if ((object as PythonProvider).type !== "python") {
    return false;
  }
  if (!hasProp(object, "module")) {
    return false;
  } else if (typeof (object as PythonProvider).module !== "string") {
    return false;
  }
  return true;
}

// Provider for Probes and Actions
function isProvider(object: Object): boolean {
  if (typeof object !== "object") {
    return false;
  } else {
    return (
      isPythonProvider(object) ||
      isHttpProvider(object) ||
      isProcessProvider(object)
    );
  }
}

function isPythonProvider(object: Object): boolean {
  if (!hasProp(object, "type")) {
    return false;
  } else if ((object as PythonProvider).type !== "python") {
    return false;
  }
  if (!hasProp(object, "module")) {
    return false;
  } else if (typeof (object as PythonProvider).module !== "string") {
    return false;
  }
  if (!hasProp(object, "func")) {
    return false;
  } else if (typeof (object as PythonProvider).func !== "string") {
    return false;
  }
  if (hasProp(object, "arguments")) {
    if (typeof (object as PythonProvider).arguments !== "object") {
      return false;
    }
  }
  if (hasProp(object, "secrets")) {
    let s = (object as PythonProvider).secrets;
    if (!Array.isArray(s)) {
      return false;
    } else {
      let areSecretsValid: boolean = true;
      s.every((secret) => {
        if (typeof secret !== "string") {
          areSecretsValid = false;
          return false;
        }
        return true;
      });
      if (!areSecretsValid) {
        return false;
      }
      // TODO Check if the secret actually exist?
    }
  }
  return true;
}

function isHttpProvider(object: Object): boolean {
  if (!hasProp(object, "type")) {
    return false;
  } else if ((object as HttpProvider).type !== "http") {
    return false;
  }
  if (!hasProp(object, "url")) {
    return false;
  } else if (typeof (object as HttpProvider).url !== "string") {
    return false;
  } else if ((object as HttpProvider).url === "") {
    return false;
  }
  if (hasProp(object, "method")) {
    if (typeof (object as HttpProvider).method !== "string") {
      return false;
    } else {
      let allowedMethods = [
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "CONNECT",
        "OPTIONS",
        "TRACE",
      ];
      if (!allowedMethods.includes((object as HttpProvider).method!)) {
        return false;
      }
    }
  }
  if (hasProp(object, "headers")) {
    if (typeof (object as HttpProvider).headers !== "object") {
      return false;
    } else if (Array.isArray((object as HttpProvider).headers)) {
      return false;
    }
  }
  if (hasProp(object, "expected_status")) {
    if (typeof (object as HttpProvider)["expected_status"] !== "number") {
      return false;
    }
  }
  if (hasProp(object, "arguments")) {
    let args = (object as HttpProvider).arguments;
    if (typeof args !== "object") {
      return false;
    }
  }
  if (hasProp(object, "timeout")) {
    let timeout = (object as HttpProvider).timeout;
    if (typeof timeout !== "number") {
      if (!Array.isArray(timeout)) {
        return false;
      } else {
        if (
          timeout.length !== 2 ||
          typeof timeout[0] !== "number" ||
          typeof timeout[1] !== "number"
        ) {
          return false;
        }
      }
    }
  }
  if (hasProp(object, "secrets")) {
    let s = (object as HttpProvider).secrets;
    if (!Array.isArray(s)) {
      return false;
    } else {
      let areSecretsValid: boolean = true;
      s.every((secret) => {
        if (typeof secret !== "string") {
          areSecretsValid = false;
          return false;
        }
        return true;
      });
      if (!areSecretsValid) {
        return false;
      }
    }
    // TODO Check if the secret actually exist?
  }
  return true;
}

function isProcessProvider(object: Object): boolean {
  if (!hasProp(object, "type")) {
    return false;
  } else if ((object as ProcessProvider).type !== "process") {
    return false;
  }
  if (!hasProp(object, "path")) {
    return false;
  } else if (typeof (object as ProcessProvider).path !== "string") {
    return false;
  }
  if (hasProp(object, "arguments")) {
    if (
      (typeof (object as ProcessProvider).arguments !== "string" &&
        typeof (object as ProcessProvider).arguments !== "object") ||
      Array.isArray((object as ProcessProvider).arguments)
    ) {
      return false;
    }
  }
  if (hasProp(object, "timeout")) {
    if (typeof (object as ProcessProvider).timeout !== "number") {
      return false;
    }
  }
  if (hasProp(object, "secrets")) {
    let s = (object as ProcessProvider).secrets;
    if (!Array.isArray(s)) {
      return false;
    } else {
      let areSecretsValid: boolean = true;
      s.every((secret) => {
        if (typeof secret !== "string") {
          areSecretsValid = false;
          return false;
        }
        return true;
      });
      if (!areSecretsValid) {
        return false;
      }
    }
    // TODO Check if the secret actually exist?
  }
  return true;
}

// Steady-state hypothesis is optional
function checkSsh(object: Object): boolean {
  if (hasProp(object, "steady-state-hypothesis")) {
    const ssh = (object as ExperimentDefinition)["steady-state-hypothesis"];
    if (ssh !== undefined) {
      if (typeof ssh !== "object" || Array.isArray(ssh)) {
        return false;
      }
      if (!hasProp(ssh, "title")) {
        return false;
      } else {
        if (typeof ssh.title !== "string") {
          return false;
        }
      }
      if (!hasProp(ssh, "probes")) {
        return false;
      } else if (!Array.isArray(ssh.probes)) {
        return false;
      } else {
        if (ssh.probes.length === 0) {
          return false;
        }
        let areProbesValid: boolean = true;
        ssh.probes.every((probe) => {
          if (!isProbe(probe)) {
            areProbesValid = false;
            return false;
          } else if (!hasProp(probe, "tolerance")) {
            areProbesValid = false;
            return false;
          } else if (!isToleranceValid(probe.tolerance)) {
            areProbesValid = false;
            return false;
          }
          return true;
        });
        if (!areProbesValid) {
          return false;
        }
      }
    }
  }
  return true;
}

function isProbe(object: Object): boolean {
  if (!hasProp(object, "type")) {
    return false;
  } else if ((object as Probe).type !== "probe") {
    return false;
  }
  if (!hasProp(object, "name")) {
    return false;
  } else if (typeof (object as Probe).name !== "string") {
    return false;
  }
  if (!hasProp(object, "provider")) {
    return false;
  } else {
    if (!isProvider((object as Probe).provider)) {
      return false;
    }
  }
  if (hasProp(object, "background")) {
    if (typeof (object as Probe).background !== "boolean") {
      return false;
    }
  }
  if (checkControls(object) === false) {
    return false;
  }
  // TODO Do something about 'ref' case?
  return true;
}

function isToleranceValid(x: unknown): boolean {
  return isScalarTolerance(x) || isArrayTolerance(x) || isObjectTolerance(x);
}

function isScalarTolerance(x: unknown): boolean {
  return (
    typeof x === "string" || typeof x === "number" || typeof x === "boolean"
  );
}

function isArrayTolerance(x: unknown): boolean {
  if (!Array.isArray(x)) {
    return false;
  } else if (x.length === 0) {
    return false;
  } else {
    let isToleranceArrayValid: boolean = true;
    x.every((t: unknown) => {
      if (!isScalarTolerance(t)) {
        isToleranceArrayValid = false;
        return false;
      }
      return true;
    });
    if (!isToleranceArrayValid) {
      return false;
    }
  }
  return true;
}

function isObjectTolerance(x: unknown): boolean {
  if (typeof x !== "object" || x === null) {
    return false;
  } else if (!hasProp(x, "type")) {
    return false;
  } else if (isProbeTolerance(x)) {
    return true;
  } else if (isRegexTolerance(x)) {
    return true;
  } else if (isJsonPathTolerance(x)) {
    return true;
  } else if (isRangeTolererance(x)) {
    return true;
  } else {
    return false;
  }
}

function isProbeTolerance(x: unknown): boolean {
  if ((x as any).type !== "probe") {
    return false;
  } else if (!isProbe(x!)) {
    return false;
  }
  return true;
}

function isRegexTolerance(x: unknown): boolean {
  if ((x as any).type !== "regex") {
    return false;
  } else if (!hasProp(x!, "pattern")) {
    return false;
  } else {
    try {
      new RegExp((x as any).pattern);
    } catch (e) {
      return false;
    }
  }
  return true;
}

function isJsonPathTolerance(x: unknown): boolean {
  if ((x as any).type !== "jsonpath") {
    return false;
  } else if (!hasProp(x!, "path")) {
    return false;
    // There is no easy way to validate that a string is a valid JSONPath
    // even less that it is valid on the context of the experiment.
    // TODO later, maybe.
  } else if (hasProp(x!, "expect")) {
    if (!["boolean", "string", "number"].includes(typeof (x as any).expect)) {
      return false;
    }
  }
  return true;
}

function isRangeTolererance(x: unknown): boolean {
  if ((x as any).type !== "range") {
    return false;
  } else if (!hasProp(x!, "range")) {
    return false;
  } else if (!Array.isArray((x as any).range)) {
    return false;
  } else if ((x as any).range.length < 2) {
    return false;
  } else {
    let isRangeValid: boolean = true;
    (x as any).range.every((value: number) => {
      if (typeof value !== "number") {
        isRangeValid = false;
        return false;
      }
      return true;
    });
    if (isRangeValid) {
      return true;
    } else {
      return false;
    }
  }
}

// Method
function checkMethod(object: Object): boolean {
  if (hasProp(object, "method")) {
    const method = (object as ExperimentDefinition).method;
    if (method !== undefined) {
      if (!Array.isArray(method)) {
        return false;
      } else {
        let isMethodValid: boolean = true;
        method.every((item: object) => {
          if (!isAction(item) && !isProbe(item)) {
            isMethodValid = false;
            return false;
          }
          return true;
        });
        if (isMethodValid) {
          return true;
        }
      }
    }
  }
  return false;
}

function isAction(object: Object): boolean {
  if (!hasProp(object, "type")) {
    return false;
  } else if ((object as Action).type !== "action") {
    return false;
  }
  if (!hasProp(object, "name")) {
    return false;
  } else if (typeof (object as Action).name !== "string") {
    return false;
  }
  if (!hasProp(object, "provider")) {
    return false;
  } else {
    if (!isProvider((object as Action).provider)) {
      return false;
    }
  }
  if (hasProp(object, "controls")) {
    if (checkControls(object) === false) {
      return false;
    }
  }
  if (hasProp(object, "background")) {
    if (typeof (object as Action).background !== "boolean") {
      return false;
    }
  }
  if (hasProp(object, "pauses")) {
    const pauses = (object as Action).pauses;
    if (pauses === undefined) {
      return false;
    } else {
      if (!hasProp(pauses, "before") && !hasProp(pauses, "after")) {
        return false;
      }
      if (hasProp(pauses, "before")) {
        if (
          typeof pauses.before !== "number" &&
          typeof pauses.before !== "string"
        ) {
          return false;
        }
      }
      if (hasProp(pauses, "after")) {
        if (
          typeof pauses.after !== "number" &&
          typeof pauses.after !== "string"
        ) {
          return false;
        }
      }
    }
  }
  // TODO Do something about 'ref' case?
  return true;
}

// Method
function checkRollbacks(object: Object): boolean {
  if (hasProp(object, "rollbacks")) {
    const rollbacks = (object as ExperimentDefinition).rollbacks;
    if (rollbacks !== undefined) {
      if (!Array.isArray(rollbacks)) {
        return false;
      } else {
        let areRollbacksValid: boolean = true;
        rollbacks.every((action: object) => {
          if (!isAction(action)) {
            areRollbacksValid = false;
            return false;
          }
          return true;
        });
        if (!areRollbacksValid) {
          return false;
        }
      }
    }
  }
  return true;
}

export function getReliablyUiExtension(
  e: ExperimentDefinition
): Extension | null {
  const exts = e.extensions;
  if (exts !== undefined) {
    const index = exts.findIndex((ext) => {
      return ext.name === "reliablyui";
    });
    if (index > -1) {
      return exts[index];
    }
    return null;
  }
  return null;
}
