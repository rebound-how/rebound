---
layout: ~/layouts/DocsLayout.astro
title: Custom Templates
soon: no
description: Create reusable templates to make it easier for your teammates to run custom experiments with minimum effort.
---

Custom templates allow you to provide your teammates with customizable experiments, that can be used in your organization with little to no configuration. It's like being able to create your own [starters](/docs/concepts/starters/).

<div class="media media--video">
  <iframe
    width="560"
    height="315"
    src="https://www.youtube.com/embed/LCs0rvTvEtA"
    title="Custom template creation and usage demo"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen></iframe>
</div>

## Creating a template

<p>From the templates page, click the <strong>New template</strong> button.</p>

### Upload an experiment

Then, you need to upload or paste a JSON file describing a Chaos Toolkit experiment.

<img src="/images/docs/concepts/custom-templates/reliably-import-experiment.png" width="851" alt="Screenshot showing an experiment pasted in the Reliably UI" />

This template must declare a `configuration` property. This property will allow Reliably to define which values will be made editable in the template.

Example of a `configuration` property in a JSON experiment.

```json
"configuration": {
  "reliably_latency": {
    "key": "RELIABLY_PARAM_LATENCY",
    "type": "env",
    "default": 0.2
  },
  "reliably_service_url": {
    "key": "RELIABLY_PARAM_SERVICE",
    "type": "env",
    "default": "https://example.com"
  }
}
```

### Edit template metadata and fields.

Once the experiment has been uploaded, Reliably asks you to provide a title for your template, as well as optional labels. These labels will be used to allow users to search for specific templates.

<p><img src="/images/docs/concepts/custom-templates/reliably-edit-metadata.png" width="548" alt="The UI for providing a title and labels" /></p>

Reliably will then present you with a field-description block for each entry in your `configuration` property.

<p><img src="/images/docs/concepts/custom-templates/reliably-edit-template-field.png" width="1350" alt="The UI for describing a field that will be presented to users" /></p>

Each block consists of two sections. The left-hand side section is a form prompting you to provide a title for the field, the expected data type (string, number, boolean, or a JSON object), as well as an optional default value, and define if this data is required or optional. The right-hand side section displays a preview of the field as it will appear to users, as well as a reminder of the `configuration` item they will be overriding.

## Using a template

On the templates list page, select an existing template.

<img src="/images/docs/concepts/custom-templates/reliably-templates-list.png" width="1336" alt="The list displays a single template, titled Simple Latency Verification" />

You will then be brought to the template's detailed view, with its title, description and a preview of the editable fields.

<p><img src="/images/docs/concepts/custom-templates/reliably-template-view.png" width="1357" alt="" /></p>

Clicking the **Create an experiment from this template** button will bring you to the experiment creation form.

<p><img src="/images/docs/concepts/custom-templates/reliably-create-experiment-from-template.png" width="1352" alt="" /></p>

<p>On this page, you can edit the experiment title, its description, and fill in the required data. After you click the <strong>Save experiment</strong> button, the experiment will be visible in the experiments list and will be available for your <a href="/docs/concepts/plans/">plans</a>.</p>
