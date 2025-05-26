---
layout: ~/layouts/DocsLayout.astro
title: Assistant
description: Accompany your intuition.
---

Realiably recognizes the power of the knowledge available to engineers and
leaders today. We have created a unique assistant that brings this mass of
information to you

## Bring the World in to help you

Reliably allows you to use OpenAI models to ask questions that are relevant to
the current experiment. The goal is to provide context when reviewing the
execution results.


<div class="markdown-tip">

Reliably never sends your experiment or execution results to OpenAI. Only
the questions are passed on.
</div>


<p><img src="/images/docs/features/assistant/example.png" alt="A screenshot of the Reliably App, displaying the assistant" width="639" /></p>

Leveraging the capabilities of public large language models, such as 
<a href="https://openai.com/" alt="OpenAI website">OpenAI</a> ChatGPT, Reliably
contextualizes your executions with well-targeted conversations.

The power of the Reliably Assistant resides in its capacity to enable your
creativity by bringing the threads of your execution into a larger context and
letting you figure out what to do next from here.

## Open up to your creativity

Creating experiments with Reliably is easily achieved through its
[Builder](/docs/features/builder/). Reliably takes it one step further by
using the power of LLM to support you generating the right experiment through
a simple prompt approach.


<p><img src="/images/docs/features/assistant/assistant-builder.png" alt="A screenshot of the Reliably assistant builder main button" width="655" /></p>


The first time you access the assistant builder, it will ask you for an
OpenAI key. That key will be encrypted and stored into Reliably's database.

<p><img src="/images/docs/features/assistant/assistant-setup.png" alt="A screenshot of the Reliably assistant builder setup" width="655" /></p>



<div class="markdown-tip">

Reliably uses the [GPT-4.1](https://platform.openai.com/docs/models/gpt-4.1)
model. Please review its costs.
</div>

Once configured, you can start using the assistant builder by passing a 
prompt:


<p><img src="/images/docs/features/assistant/assistant-prompt.png" alt="A screenshot of the Reliably assistant prompt form" width="655" /></p>

Select now the target platform:

<p><img src="/images/docs/features/assistant/assistant-target.png" alt="A screenshot of the Reliably assistant target form" width="655" /></p>

Once you press enter, Reliably Assistant will start generating an experiment
for you:


<p><img src="/images/docs/features/assistant/assistant-experiment.png" alt="A screenshot of the Reliably assistant created experiment" width="655" /></p>

Reliably will then ask you for a few parameters:

<p><img src="/images/docs/features/assistant/assistant-params.png" alt="A screenshot of the Reliably assistant experiment's parameters" width="655" /></p>

Finally, give the experiment a meaningful title and it's done!

<p><img src="/images/docs/features/assistant/assistant-title.png" alt="A screenshot of the Reliably assistant experiment's title and run buttons" width="655" /></p>

The experiment is now created and is part of your catalog. You may decide to
run it on the spot, edit it or view it. Let's see what happens when we run it:


<p><img src="/images/docs/features/assistant/assistant-run-form.png" alt="A screenshot of the Reliably assistant run experiment's form" width="655" /></p>

Select the appropriate deployment runner, the right environment and off you go!

Reliably will then schedule the epxeriment:

<p><img src="/images/docs/features/assistant/assistant-run-experiment.png" alt="A screenshot of the Reliably assistant scheduling the experiment" width="655" /></p>

Once completed, Reliably will show you a link back to the execution's results:

<p><img src="/images/docs/features/assistant/assistant-run-experiment-completed.png" alt="A screenshot of the Reliably assistant completing the execution" width="655" /></p>

<p><img src="/images/docs/features/assistant/assistant-experiment-execution.png" alt="A screenshot of the Reliably assistant showing the execution" width="655" /></p>
