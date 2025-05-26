---
title: "SecDevOps: Understanding Shift Left Security"
description: SecDevOps describes the shift left security movement & focuses on
  improving the overall security posture of an organization. Learn about shift
  left security.
seo:
  title: "SecDevOps: Understanding Shift Left Security"
  description: SecDevOps describes the shift left security movement & focuses on
    improving the overall security posture of an organization. Learn about shift
    left security.
category: "Security "
author: Mika Boström
author_role: Security & Reliability
author_image: /images/uploads/mika-author-profile.jpeg
date: 2022-06-12T16:37:09.719Z
featured_image:
  src: /images/uploads/pexels-mikhail-nilov-6963098.jpg
  alt: Shift Left Security
excerpt: SecDevOps describes the shift left security movement & focuses on
  improving the overall security posture of an organization. Learn about shift
  left security.
layout: ../../layouts/PostLayout.astro
---
*No buzzwords were harmed in the making of this post*

Let's take one of the most overloaded terms, DevOps, and mix it with the haziest of topics, security. What do you get, apart from confusion?

SecDevOps. Or maybe it's DevSecOps. If you're not sure what either means, you're not alone. Even the industry at large can't decide what they should call it.

And so they - we - came up with a new term altogether.

## Shift-Left Security, a point of view

Most of us know the concept of 'Cost of Change'. The later a change is made to a system, the more expensive it gets. Changing a widely used and deployed system costs an awful lot indeed. If we could reliably figure out future changes earlier in the development process, then, at least according to theory, the overall costs would be lower.

Let's consider a security fix addressing an actively exploited vulnerability. A fix developed in a hurry, to prevent further exploitation. We are changing an already deployed system, so we are, by definition, in the most expensive stage of the software life cycle. It's too late to change the design, but what if we could reduce the time needed for the development part?

What if we could ... shift ... the effort earlier in the process? What would that look like?

And what would it mean in practice?

## Why shift-left?

![Shift Left Security](/images/uploads/pexels-scott-webb-430208.jpg "Shift-Left Security")

From a programming and product development perspective, security often means taking a conservative look at features. Avoiding feature creep. Doing less.

The goal, and the promise, of shift-left security is to reduce the time it takes to develop security fixes, without sacrificing too many features. To make a fundamentally expensive, but necessary part of the software life cycle a slightly less expensive one.

That is, to detect and fix potentially vulnerable features before they are deployed, so that urgent fixes would be needed less often. And when they are needed, shorten the time needed to develop the fix.

In short, to save costs. And for engineers, to reduce stress.

## Why not move further right?

I'll be blunt: live patching does not work at a non-trivial scale.

In theory, we should be able to deploy small, targeted changes to running software and avoid most of the messy build-release-deploy cycle. After all, telephone networks have done that for decades with some of their most critical systems.

But those are done with languages and runtimes explicitly designed for it, orchestrated by extremely skilled veterans of their trade. In environments that themselves are strictly controlled.

For us mortals, who have to worry about both building and deploying the patched versions, shortening and hardening the build/release/deploy cycle remains the best alternative. The entire [DevOps](https://reliably.com/blog/devops-vs-sre-the-main-differences/) movement was born to make that a better experience, after all. Let's not reinvent the wheel, when we can improve it further.

Oh, and those live patches? They still need to be retrofitted to the overall development cycle, so that future releases include the fixes too. The expense is merely deferred.

And in a way, live patching of specialized systems is an extreme version of doing very rapid deployments indeed.

## What's in it for me?

Why should I bother? Modern build pipelines are already chock-full of tools, each purporting to help us be more productive or effective. What could possibly be improved in them by adding yet more complexity?

A healthy question, given that developer tooling often feels like a bottomless pit. And the answer is confidence.

Dealing with security alerts and vulnerability announcements is stressful. Given that most of the code that we ship comes from dependencies, keeping them up-to-date is basic security hygiene. But with our modern ecosystems, continuously chasing dependency updates is a burden.

Receiving a notification about a vulnerability in a dependency allows to focus our efforts and decide how to deal with it. Despite what the more unscrupulous vendors may claim, the tools in this space do not magically make us more secure. Just better informed.

Time is money. (Gratuitous Francis Bacon quote omitted.)

## Let's measure it!

I'll let you in on a dirty secret of infosec.

Traditional information security is mostly about boring stuff - and reporting in particular. Number of vulnerabilities present, by severity. Time to detect. Time to remedy. Window of exposure. Number of software components affected. At times it feels like security divisions are run by accountants.

Given that security is commonly seen as a cost and impediment, one can understand the attempt to quantify the state and direction. Or as it's often called, posture.

Well, we can play this game too. To introduce a developer-oriented security tool, get figures and real data on what is available:

* number of dependencies per project
* most frequently used dependencies across projects
* number of detected vulnerabilities, by severity
* the ages of your oldest and newest dependencies

... and so on

Then start keeping track of how long, in actual calendar time, it takes to get a dependency updated. These are your initial time-to-remedy figures.

The best part of this approach is that you can do the data collection automatically after the builds have finished. This means that your initial impact on CI/CD and build time should be zero. While you are collecting data, the last thing you want is to introduce latencies to the development workflow, let alone add additional points of build breakage.

And here's the important part: whatever the figures are, feed them back to the development teams. The entire shift-left movement sits on the premise that developers can - and should - be responsible for maintaining their security baseline. But for that to happen, the process of discovery and prioritization has to be as distraction-free as possible.

We are not even trying to do traditional information security. We know better.

Over time the number of detected vulnerabilities should be *trending down*, and in the long run, the time from detection to remedy should approximately follow the time it takes to do any relatively simple change.

Time is money.

## Shift-left and security testing

![shift left and security testing](/images/uploads/danial-igdery-fchlyvr5gji-unsplash.jpg "shift-left and security testing")

With the previous points in mind, we can finally approach the testing part of shift-left security.

Once the number of vulnerabilities is no longer a concern, and the time it takes to do a dependency upgrade is no different from any other updates - then, and only then, should we look at integrated security testing as part of standard CI/CD flow.

After all, the purpose of integrated testing is to \*BREAK\* the build on test errors. To make it impossible to release a version with known failures. Or in case of security testing: to make it impossible to release a version with known high-severity vulnerabilities or easily detected security bugs.

This is also where the speed of your chosen security tools matter. A report generated after the build has completed would have no impact on development cycle time. An integrated security check as part of CI takes time, and will eat into your overall time budget.

More complex security testing, such as running a multi-service setup through the OWASP test suite, does not belong in the CI stage. It belongs in the more involved contract, end-to-end and integration/user-acceptance testing stages.

Time is money, and engineering time is particularly expensive.

## How is this different from reliability?

It's not. As far as I am concerned, [security is an aspect of reliability](https://reliably.com/blog/choosing-between-reliability-and-security/).

The only difference is that failure modes can be more subtle, and stakes higher. Failure of reliability implies downtime, and loss of revenue. Failure of security implies a breach, and possibly loss of sensitive data.

Shift-left approach is a manifestation of the reality that both can, and should, be maintained using similar strategies.

After all: time spent dealing with incidents and their fallout is time deprived from development.

## Tools, and the curse of choice

As said earlier, selecting any development security tools can feel like looking into a bottomless pit. Below are a few relatively common ones, to get you started.

* [dependabot](https://github.com/dependabot): Github's automatic dependency scanner
* [Jenkins ZAP](https://plugins.jenkins.io/zap/): OWASP test suite
* [Aqua](https://www.aquasec.com/products/container-vulnerability-scanning/): container (image) security scanner
* [Snyk](https://www.googleadservices.com/pagead/aclk?sa=L&ai=CR1mi9hmmYpHfIdnUtwfO0ICwAv3ChsZqnqyDx-AO5tKpqc4LCAAQASC5VGC7rp-D0AqgAbSfwrgDyAEByAPYIKoEWk_QvVpDKqSxiJFBFEaX7tnt2F8oTw0OeVciD-BRajl1IvpVB2ET_zqk5ADZ69-RZY1ZUhEqpLU860OXbLduaU3Pr7Yheo9hzbBtnSS-fXeGDURFGIxyn3JuHcAE-LXGhfgDgAWQTogFxoj24TigBmaAB7TgvUeIBwGQBwGoB6a-G6gHuZqxAqgH89EbqAfu0huoB_-csQKoB8rcG6gH2KaxAqAItLg9sAgB0ggREAIghAEyAoJAOgaAgICAgBCaCRBodHRwczovL3NueWsuaW8vsQlL2mvuTXanWrkJS9pr7k12p1r4CQGYCwGqDAIIAbgMAegMBoIUCAgDEgRzbnlriBQEyBSQ3KPvgoaOiTXQFQH4FgGAFwGSFwgSBggBEAMYVA&ae=2&ved=2ahUKEwjo_aONsKj4AhULQEEAHaPkAg8Q0Qx6BAgDEAE&dct=1&cid=CAASFeRoh0dGGTKfg-p-Lw819stAh45DDQ&dblrd=1&sival=AF15MEASznS8PWDbSL9VmAWjjndJtwI9uEsj7GoDiQm5T_wL-lMewBM3Q-N-CtEy_HSEdFsFnt3Je1Kft6-AJeKDJ4NLTjjk3BurrC2UECssT215KfD7jkz4PlwSXv8mXOLuqo5JaMLIDl_WFzsShoIwUzUq5SSdh6LwAT2SLFZZnnlCo5WshMHgG8eQ3v0RLyFntQ2iUUPJ&sig=AOD64_3WjllRHeTI4Mdsbfrs22xJfOiTuQ&adurl=https://snyk.io/%3Futm_medium%3DPaid-Search%26utm_source%3Dgoogle%26utm_campaign%3DGS_SN:_Brand%26utm_content%3DBR_EX%26utm_term%3Dsnyk): dependency scanner; source code static analysis
* [Bandit (part of PyCQA)](https://github.com/PyCQA/bandit): static analysis for python
* [Semgrep](https://semgrep.dev/): a more modern static analysis engine
* [dep-check](https://www.npmjs.com/package/depcheck): dependency and vulnerability scanner
* [SonarQube](https://www.sonarqube.org/): code quality checker and static analysis engine