---
title: Three Pillars Of Service Reliability
description: >+
  We explore the three pillars of service reliability needed to achieve high
  reliability for services which are monitoring, release engineering &
  simplicity. 

category: Reliability
author: Steve Wade
author_role: Kubernates Consultant
author_image: /images/uploads/1630758024864.jpeg
date: 2022-03-23T10:35:09.362Z
featured_image:
  src: /images/uploads/alina-grubnyak-ziqkhi7417a-unsplash.jpg
  alt: pillars of service reliability
excerpt: "We explore the three pillars of service reliability needed to achieve
  high reliability for services which are monitoring, release engineering &
  simplicity. "
layout: ../../layouts/PostLayout.astro
thumbnail: /images/uploads/pexels-olia-danilevich-4974920.jpg
---
In order to achieve high levels of reliability for services and products, businesses should consider the three fundamental pillars of reliability: monitoring, release engineering and simplicity.

### 1. Monitoring

Monitoring is a key pillar in reliability but you should be selective in what you choose. You don't need to monitor absolutely everything. Monitoring metrics that you can act on and make changes based on is key.

It's very tempting to log every bit of information that you can get out of your service but what ends up happening is information overload. Data can be overwhelming and too many metrics can become misleading.

There are many tools available that allow you to collate metrics and monitor your services such as [prometheus](https://prometheus.io/) and [grafana](https://grafana.com/). These are open-source tools and are available to you to provide and facilitate monitoring at your application level but also at your platform level as well. There's a lot of custom and out-of-the-box dashboards that mean you don't have to keep reinventing the wheel when everyone builds the same set of alerts and dashboards.

The most common metrics that you should focus on from a [monitoring](https://reliably.com/blog/four-golden-signals-of-monitoring-for-sre/) perspective are the four golden signals.

* Latency - the time it takes for a service to respond to a given request
* Traffic - the amount of load a service is currently experiencing
* Error rate - which is how often do requests to the service fail (think error budgets)
* Saturation - how much longer the service resource will last or how saturated the service is

These are often the metrics that you'll use to measure components of your service level indicators so keeping an eye on these metrics can allow you to understand your customers' happiness better.

### 2. Release Engineering

Release engineering means building and deploying software in a consistent, stable and repeatable way.

There are many principles around releasing software and how it should be done - having a good release engineering strategy is the second most important pillar for high reliability.

Anything that you can do to make a release easier and smoother is going to provide much more benefit and make the whole release process much more reliable.

Whenever you change something or release something you may or may not make it more or less reliable than it was previously. Having automation and testing around your release process and a mantra of continuous testing, or a process of catching errors as soon as possible

You should consider running automated tests not just in your downstream environments but also in production.

Pretending to be the customer to ensure you understand what impact the change is having on your customer base before the customer actually sees it can also be impactful.

### 3. Simplicity

Simplicity is the final pillar and encourages you to focus on trying not to develop the most complex system but still performs as it's intended.

The concept of microservices - where hundreds and hundreds of very small microservices get created that do one thing very well, can over complicate relationships between services making it difficult to ensure there's no breaking it when making changes.

Systems trend towards complexity as new features are introduced so you need to consider the cost of additional complexity when proposing new features. You can use user satisfaction as one form of standard. You should ask yourself - will these features contribute enough business value to offset the level of complexity? How do we implement that well?

It's important to have metrics that evaluate the complexity of a system and be able to evaluate the development with simplicity in mind.

When designing new features having that business value to complexity trade-off and setting standards in a way of being able to obtain whether something is overly complex.

## Reliability - Whose Problem Is It?

![](/images/uploads/arnold-francisca-f77bh3inupe-unsplash.jpg)

It is all too common to hear 'it's not my problem' and 'it doesn't affect my microservice so therefore it doesn't have anything to do with me'. There is typically a [blame game](https://reliably.com/blog/hugops-during-downtime-building-empathetic-teams/), where it's everyone else's problem when it comes to reliability. This needs to change.

When everyone starts to think about the product as a whole and succeeding and failing together, teams start to come together and it's the responsibility of the whole engineering team, not just the product team that's working on that feature.

The whole engineering team succeeds or fails together as a unit. It's an engine that works together and there are many components and constituent parts to that.

Truthfully it's a people problem, the technology is the easiest part. It's people that make the problems difficult and once you get everybody aligned you make having conversations about reliability a lot easier.