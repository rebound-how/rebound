---
title: How to Establish Service Level Objectives In Software Engineering
description: Service Level Objectives or SLOs are the foundation of SRE. We
  explore how to establish service level objectives in software engineering.
seo:
  title: How to Establish Service Level Objectives (SLOs)
  description: Service Level Objectives or SLOs are the foundation of SRE. We
    explore how to establish service level objectives in software engineering.
category: SLO
author: Samadrita Ghosh
author_role: AI, Observability & MLOps
author_image: /images/uploads/1596292244631.jpeg
date: 2022-06-19T07:33:44.914Z
featured_image:
  src: /images/uploads/austin-distel-mpn7xjkq_ns-unsplash.jpg
  alt: service level objectives
excerpt: Service Level Objectives or SLOs are the foundation of SRE. We explore
  how to establish service level objectives in software engineering.
layout: ../../layouts/PostLayout.astro
---
## What are service level objectives in software engineering?

SLOs or Service Level Objectives are the foundation of Site Reliability Engineering (SRE). To correctly understand SLOs, the first step is to understand Service Level Indicators or SLIs.

SLIs are metrics that measure the vitals of the service. These vitals are chosen based on two conditions. First, they are the features that the user is primarily concerned about. Second, they allow the engineering team to get an overview of the system's health.

SLOs are the targeted levels of [SLIs](https://reliably.com/blog/what-is-a-service-level-indicator/) that the engineering team is required to achieve.

## Why do we need SLOs?

SLOs are increasingly adopted by organizations to serve the following requirements:

* **Setting expectations -** SLOs don't just set user expectations by defining the SLI targets, but it also aligns the expectations across the entire stakeholder hierarchy through a chosen set of objectives. The end result of limiting over-expectation is happy customers and satisfied internal stakeholders.
* **Measuring service health -** It has been noted that by setting a few SLOs, the health of a system could be easily defined and captured. Too many SLOs could distract the users and developers, while too few could paint an incomplete picture of the system's health.
* **Aligning engineering efforts -** By setting fixed targets and periodically measuring the SLIs, the engineering team could easily tune their efforts to get closer to achieving the target. This streamlines the process and also acts as the team's productivity indicator.

## What is a good Service Level Objective?

It is tricky to choose a set of SLOs for a particular service since there are multiple unique parameters that are involved for every unique pair of service and user. Good SLOs ensure that the user set is well defined so that a handful of SLIs can attend to the needs of every user as well as serve the engineering team.

However, the most critical factor that defines good service level objectives is the right choice of upper and/or lower bound which is challenging and requires experience with SLOs and a good understanding of the particular service. Flexibility in the SLO range also ensures proportionality.

### Service Level Objective Examples

To better understand service level objectives, some examples always come in handy.

#### Big data services

Since big data services handle high volumes of data, such systems focus on latency as well as throughput as the primary SLOs. Processing and delivery speed are critical in such services.

#### ERP-based services

Latest ERP systems depend on real-time updates so that customers are served with high personalization with the help of the latest data insights. SLOs that could work well here could be live communication response time and application availability.

#### Web services

Web services are focused on retrieving and sending packets of data across a network. The primary SLOs for web services could be page load time so that users can enjoy a swift browsing experience.

## How Do You Establish Service Level Objectives (SLOs) In Engineering

![Service Level Objectives SLOs](/images/uploads/windows-dfjexzflhgq-unsplash.jpg "Service Level Objectives SLOs")

The best SLOs maintain a perfect balance when it comes to quantity. Overdoing the number of SLOs can make the tracking process too chaotic while too few could lead to missing out on key details.

Coming to the choice of SLOs, they should stick to two conditions:

* Are they looking after the features that serve the user's primary needs?
* Are they providing a full picture of the system's health to the development team?

### Understanding service level indicators

The first step to establishing an SLO is to create and measure SLIs or Service Level Indicators.

There are multiple metrics that can be tracked for any type of engineered system. However, only a few sensitive indicators must be targeted to serve as SLIs so that it is simple and easy for both the customer and the service provider to keep track of what's going right and what's not.

SLIs are straightforward formula-based metrics and can be easily furnished by studying the use case at hand. The examples of services and their respective SLOs shared above also apply to SLIs.

### Understanding service level objectives

An SLO is an objective drawn up for the SLIs that are being tracked. In simple terms, SLOs are boundaries or targets set for the values of the SLIs.

The conditions change depending on the target requirement and the range of the SLI is adjustable. SLOs that are flexible and open to change the targets serve as better objectives since they are able to grow and adapt to the changing application. For example, a regular system might receive 100 requests per day, but in a high-demand case or during an anomaly like a supermarket sale, the number of requests could rise well beyond the pre-defined targets.

SLOs offer a guided path to developers to re-align the system whenever it goes adrift. It also enables users to leverage the solution to maximum potential by being wary of the SLOs that have been defined in the Service Level Agreement (SLA) and mutually agreed upon.

Another less-discussed benefit of SLOs is that it provides some space for engineers to experiment and recover by setting objectives that are lower than the actual system potential. This keeps users' expectations in check and also makes the service appear more consistent.

### Monitoring and reporting based on SLO

SLOs are frequently [monitored](https://reliably.com/blog/four-golden-signals-of-monitoring-for-sre/) and reported across the hierarchy of stakeholders including development teams, business teams, and the customers. Service providers are often bound by the SLA to periodically provide system status reports.

However, once the service is live in production, engineers tend to shift their focus to more challenging problems at hand such as building new solutions. But monitoring deployed applications is one of the most critical steps to maintaining optimal customer satisfaction.

Automated techniques to monitor the SLIs are useful and alerts can be configured whenever the targets of the SLOs are not met.

By setting tighter SLOs for internal teams, the alerts would always precede the faults observed at the user's end, leading to fast fixes and minimal impact on user experience.

## Tips For Establishing Service Level Objectives (SLOs)

![How to Establish Service Level Objectives](/images/uploads/windows-jucuefekgs8-unsplash.jpg "How to Establish Service Level Objectives")

Below are a few quick tips that could enable you to set up effective SLOs in a short span of time.

### 1. Have as few SLOs as possible

Having a handful of SLOs is enough to define and understand the overall health of the system. Too many spoil the broth.

### 2. Avoid absolutes

Fixing absolute values as SLI targets can restrict the system. Instead, maintain flexibility so that SLOs can evolve with growing systems.

### 3. Keep them simple

SLOs should be simple enough for the entire hierarchy of stakeholders to easily grasp and take decisions on. Complicating these objectives can lead to multiple iterations which are costly for both the service provider and the customer.

### 4. They don't need to be perfect

SLOs offer a guide or a realignment system for the service at hand. They don't need to be extremely detail-oriented with precise numbers as long as they are able to show the right direction to developers and users.

### 5. Experiment

SLOs are like signboards on the highway. Multiple signs could be applicable for a point in the road. It bodes well to experiment with a couple of SLOs before finalizing the set.

### 6. Be realistic

Setting unrealistic expectations to impress a prospect would inevitably fire back and cause issues for the service provider. Firstly, it is going to set a high bar for expectations, and secondly, it is going to increase the chance of losing the customer when internal teams aren't able to meet the SLA terms.

### 7. Have a safety margin

To minimize escalations, it is always recommended to set tighter SLOs for internal teams so that the threshold of errors is always well below the actual threshold. This kickstarts fault recovery even before the fault is noticeable at the user's end.

## How is SLO measured?

The SLO cannot be directly measured. It is tracked through the SLI that measures a particular metric such as system availability, response time, latency, throughput, etc.

The SLO is the target set upon these metrics. If the value of the indicators meets the admissible goal, then the SLO or Service Level Objective is considered fulfilled. Otherwise, the engineering team is called upon to adjust the system and thereafter, the SLI outcome.

## SLOs and SRE

SLOs are the foundation of Site Reliability Engineering (SRE). Even though an SRE team is mostly not involved in finalizing the SLA (as business teams take care of it), they are critical in selecting, maintaining, and evolving SLOs that are consequently used as the primary tool for communication between developers and users, and also between developers and internal stakeholders.

[SRE](https://reliably.com/blog/state-of-sre/) teams also set the target for the SLIs by clearly understanding the system's highest potential and the team's ability to maintain it.

The final number is a balance between the two so that user expectations do not surpass the daily service potential of the system.

### What is a reasonable degree of target reliability for an SLO?

Even though few SRE teams set extremely high SLOs- an example would be [99.999% availability](https://www.techtarget.com/searchnetworking/feature/The-Holy-Grail-of-five-nines-reliability), it is not recommended since it avoids the margin of safety. 99.9% uptime allows over 8 hours of error budget in a year whereas 99.999% uptime allows only a couple of minutes of error in a whole year!

It is therefore critical to assess the system and team capability well so that realistic SLOs can be set forth, maintaining user retention as well as reasonable targets for the team