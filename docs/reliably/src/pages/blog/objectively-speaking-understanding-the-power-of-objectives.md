---
title: "Objectively Speaking: Understanding the Power of Objectives"
description: "Understanding the power of objectives is critical in defining what
  good looks like for our systems but what are they & how do we define good
  objectives? "
category: Reliability
author: Mick Roper
author_role: Senior Software Engineer
author_image: /images/uploads/1598602874753.jpeg
date: 2022-04-29T07:40:23.590Z
featured_image:
  src: /images/uploads/pexels-athena-2962135.jpg
  alt: power of objectives
excerpt: "Understanding the power of objectives is critical in defining what
  good looks like for our systems but what are they & how do we define good
  objectives? "
layout: ../../layouts/PostLayout.astro
---
## What are Objectives?

Objectives help monitor different aspects of your services and systems such as latencies, error rates, PRs that are open, the age of a bug, and more. These are examples of things that drift away from what we think is good; which is essentially what an objective is.

Objectives help us to define what 'good' looks like.

## Why Should You Use Objectives?

Why would you use objectives versus traditional monitoring, such as cloud for cloud metrics, or Google monitoring? How is the objective different? The main difference is that traditional monitoring tells you what has happened, whereas an objective tells you what you want to happen.

### Signals intent

Objectives signal an intent straightaway. If you create an objective that signals that you do not want an issue to exist longer than three days, the intention there is clearly to have bugs resolved within three days. That intention is very visible and very powerful to have upfront.

### Drives discussion

Once you've signaled that intent, it drives discussion. Now the question then becomes why do we want to get rid of bugs within three days? Why do we want latency less than this? Why do we want an error rate greater than or less than that? What the metric is, is less important than the fact you are going to discuss it. That is powerful.

These types of discussions help to build a very robust team culture where members are all involved and they are trying to think beyond simply building. They also start to think about how this will operate and this provides clarity.

### Provides clarity

Providing clarity refers to metrics and monitoring that happens, especially if you ever worked with a more [traditional SRE](https://www.redhat.com/en/topics/devops/what-is-sre), that is quite deep and requires explanation. Whereas an objective doesn't, especially if you think about it from the perspective of who is affected by the objective.

Ideally, objectives should always be from a customer's viewpoint. The customer doesn't necessarily care about what version of Linux you are running. From a perspective of reliability you do, but this is where it all falls in.

Objectives should be clear and always provide clarity, for example, an error rate or an issue rate, something that can very quickly be understood.

### Allows reflection

Last, of all, we think you should use objectives because they allow you to reflect properly, which embodies the [Agile Manifesto mantra of continuous improvement.](https://www.gbscorporate.com/blog/want-to-develop-a-culture-of-continuous-improvement) You want to be able to look at something empirically and then reflect: 'Did we do well? Did we not?' without letting emotion get in the way.

It's very easy to say, 'we've got a lot of alerts so it's not very good.' It may be a negative situation but it also depends on the impact of those alerts.

Objectives help you to reflect on whether the alerts simply have very high tolerances or whether the alerts are something that users care about. This reflection helps us to think critically about what we have done and then what we can do going forward.

You must not forget to update your objectives post reflection to ensure that they are not static. They flow as time flows.

## What Value Do Objectives Bring To Your Business?

![defining good objectives](/images/uploads/campaign-creators-gmsnxqiljp4-unsplash.jpg "defining good objectives")

Much like culture, these things depend completely upon your business, your circumstances, your capabilities, and your desires for what a good objective looks like.

## Defining good objectives

We've provided a few ideas below that are slightly more vague and broad just to give you some good pointers to get you going on creating impactful objectives for your business.

### 1. Important to your customers

First and foremost, an objective should be important to your customers. That's critical.

An objective that is not important to your customers is not good. The definition of a customer in this context is specifically the person using the stuff you build. Anyone who uses your software needs to be impacted by the objective and if they are not, then it is not a valuable objective.

### 2. Understandable by all stakeholders

Objectives need to be understandable by all stakeholders and although it may be difficult to do, you want to make these things as simple as humanly possible. However, it is important to note that you do not have to be extremely technical in your explanation, just enough for stakeholders to comprehend and take something away from it.

A useful way of showcasing this is through percentages: the percentage of successful requests, percentages of requests service within X number of milliseconds, the age of a bug, and the number of PRs closed versus open.

### 3. Easily measurable

The objective should always be easily measurable. An easily measurable objective depends very much on what you are measuring and what tooling is available to measure it. For example, if you were measuring the age of a PR, it is not very difficult to understand and you could easily jump on a web browser and have a look. But if you are trying to measure the percentile error rate of a given request, it is going to be slightly harder to measure.

If we go even deeper, and we are talking about very high-performance systems, you might be looking at some very low-level calls using a library that is monitoring at almost a kernel level, which is a lot harder to measure.

Ultimately, easily measurable as an objective, can be objective. Don't hold yourself to that one too much but make it as easy as possible, so that it doesn't become a hurdle to your adoption of objectives.

### 4. Reasonably achievable

Objectives should also be reasonably achievable. It is very easy to create an example of what 'good' looks like and it is not something you can realistically achieve.

You should always set a goal that is slightly out of reach but could be achieved and when you do achieve it, that is when you move toward the objective. This enables you to become slightly more refined or you may just decide that this is enough and we want to maintain that state of 'good.'

If you are going to set a state of good, which is to have a latency of fewer than 50 milliseconds, across the public internet, it is possible, but it is also very unlikely.

Additionally, you are leaving yourself in a situation where you are at someone else's mercy regarding how you will be able to achieve that. If you get an ISP that goes down then your objective is shot and there is very little you can do about that. In short, give yourself achievable objectives.

### 5. Fairly coarse

Try and make your objectives fairly coarse. The advantage of a fairly coarse objective is that it does not depend upon any single component or individual or system. You want to try and make it as agnostic as possible.

It is best to look at outcomes, rather than looking at individual things. Do not say, for instance, we use a particular version of Python as an object because it does not affect the end-user - unless your objective is around the library.

Try and make it coarse, it makes things easier which is what objectives are meant to do. Objectives are a nice way of understanding what 'good' looks like, not presenting the difficult way that it was done.

### 6. Easy to refine

Lastly, objectives should also be easy to refine with a bare minimum number of metrics.

## How To Maintain Objectives

![power of objectives](/images/uploads/raj-rana-ri0pi8ujrri-unsplash.jpg "power of objectives")

Once you've got your objectives, you need to think about what you need to do next because objectives evolve. They are primarily a tool for culture than they are a tool for tech and as a result, it moves at the speed of culture.

### Review your objectives at regular intervals

You should always be reviewing your objectives at regular intervals; the end of the sprint is a good idea although you could set a more arbitrary timeline depending on what you want and change them every day. As long as they continue to reflect what 'good' looks like.

### Don't be afraid to change objectives that have 'drifted'

Don't be afraid to change objectives. Some objectives can last a long time and never have to be changed and they become like furniture.

Once they've been there for a long time, people are wary to make tweaks. If they have drifted and they no longer define good then they need to be tweaked and changed.

There have been instances where various tests have been carried out on what happens when we change objectives, and the alerts are overwhelming because you suddenly change an objective. But that is valuable because what it shows is that what worked yesterday and what was 'good' yesterday is not 'good' today.

### Incorporate objectives into wider 'resilient engineering' practices

Anything else you're going to do that is classified as 'resilient engineering' - chaos, engineering, compliance engineering, and continuous improvement of existing processes - you should incorporate your objectives into these systems or these processes.

#### Chaos engineering

If you perform a chaos experiment, use an objective as part of the measure.

#### Compliance

If you're doing compliance, set an objective to see how compliant systems are. [Reliably](https://reliably.com/) is a great tool that will help with that.

#### Continuous improvement

Continuous Improvement goes without saying as objectives are a definition of 'good'. It is your constant drive to improve your processes so that your outcomes are better. Objectives are a brilliant tool to allow that to happen.