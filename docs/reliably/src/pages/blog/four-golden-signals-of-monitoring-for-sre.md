---
title: Four Golden Signals Of Monitoring For SRE
description: The four golden signals of monitoring for SRE ensure applications
  and services remain highly available but what are the four signals and why are
  they important?
category: Reliability
author: Kyle Jones
author_role: Senior Software Engineer
author_image: /images/uploads/kyle-author-photo.jpeg
date: 2022-03-19T08:16:37.885Z
featured_image:
  src: /images/uploads/pexels-olia-danilevich-4974912.jpg
  alt: four golden signals
excerpt: The four golden signals of monitoring for SRE ensure applications and
  services remain highly available but what are the four signals and why are
  they important?
layout: ../../layouts/PostLayout.astro
---
## What are the four golden signals of monitoring?

![Four golden signals of monitoring](/images/uploads/golden-signals.png "Four golden signals of monitoring")

Building a modern, cloud-based application that uses microservices to handle a high throughput is the goal for many organizations across the globe, particularly those that are technology-focused.

To deliver on this goal whilst ensuring that the application remains highly available, four golden signals should be monitored:

* Latency
* Traffic
* Errors
* Saturation

### 1. Latency

The time it takes a piece of data to pass from its origin to its destination is known as latency. Often referred to as response time, latency is usually measured in milliseconds but can also be measured in seconds if performing poorly.

A variety of factors could affect latency including the distance between the origin and the destination. For example, a packet of data might be sent from a server in London (England) at 12:00:00.000GMT to another server in Dublin (Ireland) which arrives at 12:00:00.072GMT. This means that the latency for sending this packet is 72 milliseconds (ms).

It is important to differentiate between the different status codes associated with these requests, particularly if they are being returned from an API in your application. This is because errors (such as status code 500 responses) will likely fail fast and so will have a slower response time.

### 2. Traffic

The quantity of data that moves through a network is known as traffic. It is generally measured in HTTP requests per second. This fluctuates with the number of people using your service and so is a good indication of demand. It can also be measured using transactions per second, retrievals per second, or concurrent sessions.

As these metrics directly correspond to the number of users accessing your application, they can be used to assist with capacity planning. Using trend analysis will allow you to identify peak and off-peak periods of use, which allows you to scale your infrastructure either horizontally or vertically.

Yan Cui spoke on [Software Engineering Daily](https://softwareengineeringdaily.com/wp-content/uploads/2018/12/SED704-Streaming-Platform-Architecture.pdf) about handling spikes in traffic at DAZN, a live streaming service like Netflix that solely provides sports content. This means that their traffic increases by large quantities at infrequent intervals (around 20 seconds before a match starts).

This is something that can be incredibly problematic and can only be solved by frequently analyzing the traffic for different match categories and planning capacity for them in advance.

### 3. Errors

Almost everyone who has used a computer has experienced errors. However, when we're talking about monitoring, errors are the rate of requests that result in some kind of failure. These failures can be explicit or implicit depending on the status code of the response.

An implicit error would be a response that has a 2XX status code whereas explicit errors would contain a non-2XX status code - often either 4XX or 5XX.

You can also configure your application to treat any requests that do not conform to a policy as errors. For example, if you set up a policy for response times to be subsecond, then any requests that take longer than 1 second would also be regarded as an error.

These errors should be logged and compared against an error budget. An error budget is the number of errors an application can return before users start to become unhappy and consider their experience to be a negative one.

### 4. Saturation

Saturation is the measure of how constrained the resources available to your application are, comparing the current usage to the maximum utilization. Metrics for this could show figures relating to resources such as input and output (I/O) or memory. These resources all have their own limits that will cause degradation of the application's performance. This is often before the metrics reach 100% due to the services that will become blocked by resource starvation.

Increases in latency often precede increases in saturation. Similarly, an increase in saturation can point to degradation in the future in some cases. An example of this could be the CPU, memory, or storage for an application slowly increasing until they become full and performance degrades accordingly.

## Why are the four golden signals important for monitoring?

![Four golden signals](/images/uploads/pexels-firos-nv-8171308.jpg "Four golden signals")

The four golden signals are vital to providing a positive customer experience. Each signal is an umbrella that covers several metrics.

Each of these metrics, when monitored correctly, can be used to make your services more reliable and robust. This can be done by allowing your SRE team to undertake corrective measures where possible, alleviating stress on the application and reducing the number of errors. Frequent errors could end up with your users becoming frustrated and not returning to use your service in the future.

### What to do with the golden signals?

Many of the actions that should be taken with the golden signals are general practices when it comes to monitoring and observability.

The most important actions are to add alerting on the metrics and to create dashboards to provide a comprehensive view of the status of the application and its components. The signals and the methods above can be used to troubleshoot components to diagnose the root causes of problems with the application.

The golden signals should also be used to inform your service level objectives (SLAs) and your capacity planning. Poor capacity planning could lead to overprovisioning and therefore overpaying for infrastructure. On the flip side, it could also lead to exceeding your error budget and failing to meet your SLAs if you do not provision too small or too few instances.

## What are monitoring best practices?

One of the most important elements of a strong monitoring practice is detailed, well-structured alerts with an effective method of delivery.

If something is going wrong with your application, you want any interested parties to be notified of it as soon as possible and to have the relevant information to put it right. These alerts should inform your engineers when thresholds are reached, such as when the RAM for an instance exceeds 90%.

Alerting engineers through Slack is one way you can get visibility on issues.

Another key practice is to use the golden signals to inform your error budget, SLIs, SLOs, and SLAs. This is because the golden signals directly align with key metrics like availability and responsiveness.

Failing to maintain a healthy application when SLAs are in place could prove disastrous, particularly if the SLA was not informed by data from the golden signals.

### Improving reliability with monitoring

The four golden Signals can be used to help with the implementation of a variety of measures that will improve the reliability of the application and its components.

The first example of this is using traffic for capacity planning. In some cases, this is a straightforward task as there is a regular stream of traffic. However, in others, this could prove incredibly difficult to predict without careful studying of the historical values associated with this signal.

Another way that reliability can be improved through monitoring is through anomaly detection and troubleshooting.

Strong monitoring and observability enable us to quickly identify when any components of our application are not working as we expect them to. From here, we can then begin to dig into why these issues are occurring. In most cases, the four golden signals can be used to make this process easier by providing us with some context and clues as to where is the best place to start our investigation.

### SRE monitoring tools

* [Datadog](https://www.datadoghq.com/) is a monitoring and security platform built especially for cloud applications.
* [New Relic](https://newrelic.com/) is a full-stack monitoring and observability platform that has a free plan.
* [Reliably](https://reliably.com/) assists engineering teams and organizations to get better at operating with greater predictability and less anxiety.
* [OpsGenie](https://www.atlassian.com/software/opsgenie) is an incident management platform from the team at Atlassian.
* [PagerDuty](https://www.pagerduty.com/) is an incident management and operational analytics platform used by a range of tech companies such as Slack, Twilio, and Zoom.
* [Prometheus](https://prometheus.io/) is an open-source monitoring and alerting toolkit.
* [Sentry](https://sentry.io/) provides real-time error reporting and tracing with a free developer plan.