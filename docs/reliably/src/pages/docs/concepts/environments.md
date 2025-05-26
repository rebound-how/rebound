---
layout: ~/layouts/DocsLayout.astro
title: Environments
description: Environments allow you to store variables and secrets that will be used by the Reliably App, the Reliably CLI or GitHub workflows.
---

Environments allow you to store variables and encrypted secrets that will be used by the Reliably App, the Reliably CLI or GitHub workflows (see [How it works](/docs/how-it-works/)).

## Create an environment

<p>Navigate to the Environments page  to view your existing environments and click on "New" to create a new one.</p>

<p><img src="/images/docs/concepts/environments/reliably-new-environment-form.png" alt="A screenshot of the Environment creation form in the Reliably App. The form displays a text input to name the deployment and fields to add new variables and secrets" width="490" /></p>

### Environment variables

Environment variables are key/value pairs used to store non-sensitive data.

### Secrets

Secrets are encrypted variables used to store sensitive information, such as service accounts, tokens, etc.

There are two types of secrets:

- Variables are key/value pairs.
- Paths are designed to be used as files your experiment will read from. They're made of:
    - a path (like /home/svc/.chaostoolkit/integrations/c5ce...7fd80/sa.json),
    - the content of the file (as a string).