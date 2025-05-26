---
title: "Building high performing teams and reliable systems - a recipe for success"
description: "In our May meet-up, we'll explore why observability and delivery times are fuelling some of the most high-performing modern engineering teams and discover how an observability team increased the quality of their software delivery to run resilient distributed systems and deliver the ultimate shopping experience for their customers!"
date: 2022-05-19T17:00:00Z
link: https://www.meetup.com/reliability/events/285267262/
labels:
  - Online Event
  - Meetup
thumbnail: /images/uploads/2022-05-19-reliably-meetup.png
layout: ../../layouts/EventLayout.astro
---

### Fifteen minutes or bust
Charity Majors, _CTO Honeycomb_

There is a yawning gap opening up between the best and the rest — the elite top few percent of engineering teams are making incredible gains year on year in velocity, reliability and human compatibility, whilst the bottom 50% are actually losing ground.

The loss has nothing to do with engineering ability. Take an engineer out of an elite-performing team and place them in the bottom 50%, and they become subpar too; take an engineer out of a mediocre team and embed them in an elite team, and they are pulling their weight within the year.

So how do you build these high-performing teams?

The most important things to focus on are observability and delivery time. We’ll talk about both of these and more.

### Ensure the ultimate shopping experience by delivering a resilient distributed system
Arnold van Wijnbergen, _interim Product Owner Observability @ Ahold-delhaize, Founder @ Qensus.io_

Every day customers are looking for trending recipes, inspiring food and place thousands of orders for their groceries. During their journey we measure and try to improve their digital experience with various types of monitoring. In most cases we still spot issues with previous deployments using deployment markers, but still this is reactive. This eventually solves the outage, but nobody is happy when the website is loading slow, searches are irrelevant and the shopping basket is incorrect during a period. The worst thing that can happen is that a customer will visit a competitor instead, which eventually is profit loss.

During this talk you will learn how we as an observability team took advantage of GitOps, to overcome our challenges. After this success we took the next step to help application teams with extending their resilience strategy for deployments. We introduced a control plane called Keptn to trigger performance simulations and validate quality against Service Level Objectives defined in our monitoring solutions.

Our goal was reliable and confident deployments of our distributed system on Kubernetes. After all, we want to give our customers the ultimate shopping experience!