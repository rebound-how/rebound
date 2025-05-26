---
title: Choosing Between Reliability And Security
description: >
  We explore choosing between reliability and security and their relationships
  through shared response. Which one is more important and what should you focus
  on? 
category: Security
author: Mika Boström
author_role: Security & Reliability
author_image: /images/uploads/mika-author-profile.jpeg
date: 2022-03-19T09:15:58.057Z
featured_image:
  src: /images/uploads/pexels-pixabay-60504.jpg
  alt: reliability and security
excerpt: "We explore choosing between reliability and security and their
  relationships through shared response. Which one is more important and what
  should you focus on? "
layout: ../../layouts/PostLayout.astro
---
## The Security-Reliability Relationship through Shared Response

Security and reliability efforts tend to be at odds with each other. They shouldn't be: security should be considered an essential facet of reliability.

If we consider the tools used, there is a range of good tooling for reliability, and then a separate set of tools for security - which tend to be more expensive and more specialized.

The same tools, approaches, and ideas used for observing reliability and performance not only can but indeed must, be used for proper security because there is no way to decouple the two. The main difference is the motivation for using one over the other.

For example, if you do something and the site gets slow, the question is: what kind of problem is that? If you ask your frontend team, they might say that's a backend problem. Ask the back-end team, they'll say that's a performance problem. If we then ask sales and marketing, they would say that it's a PR problem.

If you ask a site reliability engineer ([SRE](https://reliably.com/blog/state-of-sre/)) they might say that's a reliability problem. And if we ask a sufficiently paranoid security person, they'll take a look, and say it's a 'denial-of-service vector.'

All of these can be true.

The difference with all of these responses is that the various professionals each saw the exact same behavior and results, but they interpreted the situation differently. They have their own agenda, own view, vision, as well as their own heavy and hefty biases.

In fact, we all use the same mechanisms, and the same tools, in the same way: to observe failures or problems. The tooling we use should be the same.

### Divisive Opinion: Linting is Static Analysis

If we talk about common patterns in shift-left thinking, [linting](https://www.perforce.com/blog/qac/what-lint-code-and-why-linting-important) focuses on detecting patterns early and easily, so in a way, linting is nothing more than doing a very basic form of static analysis. Those two words carry a very heavy load.

With regards to linting, if you were asked what is the actual difference between a linter and a SAST component (SAST = static analysis security/scanner tool): it could be claimed that there are no functional differences.

When you run a linter on a piece of code, and it detects bad patterns or just off-putting code syntax, it will flag what it thinks is wrong. If you run code through a static analyzer, it detects known-insecure patterns and flags what it thinks is insecure. In theory: a static analysis scanner does effectively just very focused linting.

Furthermore, both tools will be noisy - you need to configure each one to suit your own purpose, your own needs, and teach them what is meaningful. Above all, you have to override their boilerplate errors.

A linter that complains 'this is bad syntax' is unhelpful. A linter that tells you to use a particular pattern instead, is helpful. One that explains why such a replacement pattern is desired, is actually useful.

The same applies to a security scanner. If it complains that a given use of code is bad but does not explain why the construct is insecure, it is definitely unhelpful. Sadly (or depending on your viewpoint), every SAST tool defaults to the former.

However, if the scanner tells you how to fix the code in question, and what the problem is, then the tool becomes useful. No longer a source of irritation, it instead makes the code review scale better. As a result, anyone who copies code from StackOverflow will get the same explanation automatically from the CI. Copying already known-good code from your own codebase? Great, now we're on much better footing.

## Security or Reliability?

Despite their different goals, security and reliability are two sides of the same coin. Requirements, approaches, and even ways to detect issues rely on the same principles.

In a modern environment, if you are doing one, you are also doing the other. Let's take a couple of examples:

### Immutable Infrastructure - Reliability Paradigm

[Immutable infrastructure](https://www.hashicorp.com/resources/what-is-mutable-vs-immutable-infrastructure) is the gold standard of modern reliability engineering.

From a system and performance perspective, the main benefit is the lack of a long-term state. A fleet of hosts and systems that are easy to provision and even easier to remove. Configurations are completely codified so that all things within your fleet are reproducible. In short, the setup is delightfully boring.

When anything is manually done the same way over and over again, humans get bored. They find shortcuts. They forget steps that to them appear irrelevant. In summary, they innovate on the job. Humans are not good at repetitive, boring tasks.

Computers don't get bored.

With immutable infrastructure, the goal is to never alter systems after provisioning. In fact, modification after spawning is a problem: someone (or something) has messed about in your systems. Modified systems are deviants, and in the context of the paradigm, broken.

### Immutable Infrastructure - Security Properties Built In

From a security standpoint, immutable infrastructure is also very much desirable. Instead of trying to adapt to a changing state, you instead force one you know to be correct. Or if not correct, at least wrong in a systematically known way.

Modified systems are still deviants, but in the context of security, they are not only broken - they are potentially compromised. The goal of never modifying live systems has not changed, but the interpretation has: violation of the principle turns from a production incident to a security incident.

The ability to destroy and reprovision parts of a system without downtime or operational impact also brings in a really interesting downstream effect: hosts are, by design, transient. With regards to security, this makes a potential attacker's life quite difficult.

When we talk about modern attackers, their operations rely on four major steps:

1. Recon (short for reconnaissance)
2. Compromise
3. Persistence
4. Exfiltration

In an online world, the first one is impossible to protect against. Much of the traditional security work revolves around making the second step more difficult - and we still want to reduce the window of opportunity where we can. But we also have to assume that at some point a compromise does happen. While prevention is ideal, detection is paramount.

In modern systems, and especially with the programmable, immutable infrastructure we have additional levers.

If persistence becomes impossible, it changes the patterns attackers have to adapt to. When hosts routinely vanish and reappear, it means an attacker needs to re-execute their compromise steps, to regain their foothold and to get their tools in place again.

A one-off compromise can go undetected, but having to do the same things, again and again, exposes attackers into leaving more easily detected traces of themselves, with every cycle carrying the risk of triggering alerts.

In a system with only transient hosts, the system itself becomes automatically harder to attack: even once you do get in, you can not expect your foothold to last. Without the foothold, exfiltrating data becomes a much harder task.

There's a fifth step that we have deliberately ignored. If the goal of an attack is to deploy ransomware, there will be an additional step after exfiltration: ransack.

## Picking Between Reliability and Security

![reliability and security](/images/uploads/pexels-christina-morillo-1181243.jpg "reliability and security")

In the case of choosing between reliability and security, the question of which to focus on is by itself irrelevant, if not outright misguided. The people who work in the domains use common tools, have the same goals but above all, have aligned goals.

The main difference is the mindset - what we are doing and why? When something fails, why did it fail? What do we do to fix it? Why is the fix itself necessary or why is the underlying concern a problem?

We can even turn the statement around: if something is a security concern, it is very likely also a reliability concern. And that brings us a full circle to my original statement:

Whether we work on reliability or security - in the end, we should want to use the same tools.

As to why? Tools are a means to an end. We don't really care what the tools themselves are, we just want to see the relevant data for our purposes. And most of the time, the ends are not that different.

The question of whether you're doing security or [reliability](https://reliably.com/) is increasingly irrelevant. If you're doing one, you are doing both. Even if you didn't know it.