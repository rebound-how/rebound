import type { TemplateCreate } from "@/types/templates";

import { hasProp } from "./objects";
import { checkExperiment } from "./experiments";

// Quickly check if the provided object is a valid template
export function checkTemplate(object: Object): string {
  if (!checkMetadata(object)) {
    return "<code>metadata</code> property is missing";
  }
  if (!checkName(object)) {
    return "<code>metadata.name</code> property is missing or invalid";
  }
  if (!checkLabels(object)) {
    return "<code>metadata.labels</code> property is invalid";
  }
  if (!checkSpec(object)) {
    return "<code>spec</code> property is missing";
  }
  if (!checkSpecProvider(object)) {
    return "<code>spec.provider</code> property is missing or invalid";
  }
  if (!checkSpecType(object)) {
    return "<code>spec.type</code> property is missing or invalid";
  }
  if (!checkSpecSchema(object)) {
    return "<code>spec.schema</code> property is invalid";
  }
  if (!checkSpecSchemaConfiguration(object)) {
    return "<code>spec.schema.configuration</code> property is missing or invalid";
  }
  if (!checkSpecTemplate(object)) {
    return "<code>spec.template</code> property is missing or invalid";
  }

  return "";
}

function checkMetadata(object: Object): boolean {
  if (hasProp(object, "metadata")) {
    return true;
  }
  return false;
}

function checkName(object: Object): boolean {
  if (hasProp((object as TemplateCreate).metadata, "name")) {
    return typeof (object as TemplateCreate).metadata.name === "string";
  }
  return false;
}

function checkLabels(object: Object): boolean {
  if (hasProp((object as TemplateCreate).metadata, "labels")) {
    const labels = (object as TemplateCreate).metadata.labels;
    if (Array.isArray(labels)) {
      return labels.every((l) => {
        return typeof l === "string";
      });
    } else {
      return false;
    }
  }
  return false;
}

function checkSpec(object: Object): boolean {
  if (hasProp(object, "spec")) {
    return true;
  }
  return false;
}

function checkSpecProvider(object: Object): boolean {
  if (hasProp((object as TemplateCreate).spec, "provider")) {
    return (object as TemplateCreate).spec.provider === "chaostoolkit";
  }
  return false;
}

function checkSpecType(object: Object): boolean {
  if (hasProp((object as TemplateCreate).spec, "type")) {
    return (object as TemplateCreate).spec.type === "experiment";
  }
  return false;
}

function checkSpecSchema(object: Object): boolean {
  if (hasProp((object as TemplateCreate).spec, "schema")) {
    return true;
  }
  return false;
}

function checkSpecSchemaConfiguration(object: Object): boolean {
  if (hasProp((object as TemplateCreate).spec.schema, "configuration")) {
    const conf = (object as TemplateCreate).spec.schema.configuration;
    if (Array.isArray(conf)) {
      return conf.every((c) => {
        return (
          typeof c.key === "string" &&
          typeof c.title === "string" &&
          typeof c.placeholder === "string" &&
          typeof c.help === "string" &&
          hasProp(c, "default") &&
          typeof c.type === "string" &&
          typeof c.required === "boolean"
        );
      });
    } else {
      return false;
    }
  }
  return false;
}

function checkSpecTemplate(object: Object): boolean {
  if (hasProp((object as TemplateCreate).spec, "template")) {
    return checkExperiment((object as TemplateCreate).spec.template) === "";
  }
  return false;
}
