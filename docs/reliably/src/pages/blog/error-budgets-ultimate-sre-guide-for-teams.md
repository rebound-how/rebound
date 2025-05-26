---
title: "Error Budgets: Ultimate SRE Guide For Teams"
description: >
  Teams depend on error budgets & are a critical requirement that protects teams
  from failures. Learn about error budgets with our ultimate SRE guide.
seo:
  description: Teams depend on error budgets & are a critical requirement that
    protect teams from failures. Learn about error budgets with our ultimate SRE
    guide.
  title: "Error Budgets: Ultimate SRE Guide For Teams"
category: Error Budgets
author: Samadrita Ghosh
author_role: AI, Observability & MLOps
author_image: /images/uploads/1596292244631.jpeg
date: 2022-05-26T06:54:11.734Z
featured_image:
  src: /images/uploads/fabian-blank-pelskgra2nu-unsplash.jpg
  alt: error budgets sre
excerpt: Teams depend on error budgets & are a critical requirement that
  protects teams from failures. Learn about error budgets with our ultimate SRE
  guide.
layout: ../../layouts/PostLayout.astro
---
## What is an error budget?

Any engineered system does not guarantee 100% uptime. There are bound to be some unforeseen system failures that cause downtime for the customers or create a poor customer experience. It is, therefore, best practice to take into account a margin for plausible failures.

An error budget is this margin of error that the customer is informed about beforehand to secure tolerance during system failure for a decided number of hours. The error budget is a critical requirement since it protects the service provider from inevitable system failures that are unforeseen and can rarely be mitigated during system design.

## Why Do Organisations Need An Error Budget?

Organizations depend on error budgets to firstly secure a minimum number of hours during which the system can fail without any repercussions from the customers' end.

However, another major contribution of error budgets is providing the ability to take risks without any consequences. For example, if the team wants to push a new feature that carries the risk of causing failures, an error budget provides the padding to push it nonetheless.

### What types of outages must fit into an error budget?

![sre outages error budget](/images/uploads/erik-mclean-sxisod0tyyq-unsplash.jpg "sre outages error budget")

Most system failures easily fit into consideration for error budgets. Some of the common types of outages include:

* **Maintenance activities:** Maintenance activities include performance checks, pushing bug fixes, upgrading dependencies or integrated tools, and many more similar tasks. These can lead to errors causing downtime. It is best practice to execute these tasks during minimal traffic.
* **New feature addition:** Innovation is key to product growth in a competitive market. However, every new feature can disrupt the system causing system failures. Error budgets offer an allowance for such failures to encourage pace in innovation.
* **Unplanned bugs:** Bugs are an inevitable part of tech systems, especially ones with growing complexity. Error budgets ensure to offer enough margin for such bugs to play out so they can be fixed without the pressure of being held accountable by the customer.

## How is an error budget calculated?

To have a clear picture of how to calculate error budgets, it is critical to understand SLAs and SLOs first.

SLAs or Service Level Agreements list the terms agreed upon by both service provider and consumer. SLOs or Service Level Objective lists down the goals that the development team has to meet to ensure the SLA is maintained. SLO is usually more difficult to maintain compared to the SLA since it is internal and more tightly planned.

Setting an SLO of 99.9% would convert to an error budget of 1-SLO or 0.1%. So if a system is supposed to run for 10,000 hours in a year, the allowance to fail would be 1000 hours with an error budget of 0.1%.

## Error Budget and Maintenance Windows

Maintenance windows are pre-planned time slots where maintenance activities are conducted which may lead to disruptions in the system. Even though recent technologies like resource virtualization have enabled the ability to carry out tasks in isolation without affecting the system, narrow slices of downtime due to unforeseen maintenance activities in the production environment are unavoidable.

If maintenance activities are not planned out well, it can easily eat away the error budget. However, there are ways through which it can be exempted from the error budget, saving both performance metrics and risk potential.

### Business Hours

Several services operate only during business hours. If the maintenance operations are carried out after or before business hours, it can be exempted from the error budget since it does not impact customer experience.

### Traffic Analysis

By planning the maintenance window outside the peak traffic hours, the impact on customers is minimized and therefore the impact on the error budget is minimized.

Depletion of the error budget is directly proportional to the number of error tickets raised by customers. To find the traffic pattern, the team has to rely on historical data which is typically not ideal while encountering random traffic patterns.

### Eliminating toil

Toil is a set of repetitive and manual tasks associated with a service that tends to grow with scale. [Toil](https://cloud.google.com/blog/products/management-tools/identifying-and-tracking-toil-using-sre-principles) can be minimized primarily through automation which contributes significantly towards maintaining error budgets as well.

By automating processes, the possibility of manual errors is reduced significantly, leading to a reduced impact on the error budget. Ideally, the automation should also work in case of system failures when it comes to toil since manually-intensive recovery protocols have significant scope for automation.

## Error budgets and SRE

SRE or Site Reliability Engineering is an IT approach to ensure performance and reliability in software systems. The SRE employs various metrics and tools to align processes over time to minimize downtime and maximize [reliability](https://reliably.com/blog/the-journey-of-building-reliability-and-scaling-your-systems/).

One such metric is the SLO or Service Level Objectives which define the goals for the team to meet the conditions of the SLA. An error budget is the outcome of the SLOs and draws the line at an acceptable level of system errors. SRE methods are aimed at bringing back the fluctuating or disrupted systems within the decided margin of acceptable errors.

## Useful error budget calculator tools

Error budget can be easily calculated through a set of a few simple formulas or even through online or pre-built tools such as follows:

* [Error budget calculator](https://dastergon.gr/error-budget-calculator/)
* [Availability calculator and cheat sheet](https://availability.sre.xyz/)
* [Uptime and downtime calculator](https://uptime.is/)
* [SLI calculator](http://work.haufegroup.io/calculating-slis-with-prometheus/)

## SLI, SLO, and SLA - what are they and how do they relate to error budgets?

We have touched upon SLOs and SLA on a high level, so let's look into them a bit further here. Service Level Objectives (SLOs) are set by internal teams to meet the Service Level Agreement (SLA) defined and agreed upon by the two engaging parties (service provider and service consumer). Whenever the terms in the SLA are not met, there are some repercussions clearly defined, mostly financial, that must be borne by the service provider.

SLOs can be drawn for various objectives including service availability, latency, error rate, durability, system throughput, and many others. [Service Level Indicators](https://reliably.com/blog/what-is-a-service-level-indicator/) (or SLIs) are drawn up to accurately track the progress toward SLOs. The SLIs should be carefully selected since too many could be difficult to manage and track, and end up not giving any clear indication of the status of the SLOs.

SLIs can be calculated through a straightforward formula since it is essentially a ratio between good events and all valid events. It is usually converted to a percentage format. A bunch of SLIs together easily creates a picture of the state of the defined SLOs so that the team can change course or stay on it accordingly.

All of the above link to error budgets since they are all directed towards system reliability and performance. While SLIs indicate the status of SLOs, the SLOs directly indicate the extent of the error budget. For example, as illustrated earlier, if the SLO for availability is 99.9%, then the error budget would be (1-SLO) or 0.1%.

### How Can Developers 'Spend' Their Error Budget?

![spending error budget sre](/images/uploads/towfiqu-barbhuiya-jhevwhcbvyw-unsplash.jpg "spending error budget sre")

The key is to have a balance between innovation and reliability. Developers are usually advised to plan the expenditure of their error budget to ensure maximum flexibility while exploring risks and minimal impact on customer experience.

For example, if the development team does not plan new feature updates and pushes multiple features during the first month itself, it can rapidly deplete the error budget and leave the team with no room to innovate features during the remaining year.

### What Actions Should a Team Take If Their Error Budget is Spent Or Close To Spent?

There are a handful of steps that can be taken when the error budget has either completely burned or is about to be:

* Freeze all new releases
* Prioritize bug fixes over features
* Rollback to the previous system version and gradually push fixes
* Check for incorrectly categorized errors
* Deal with hard dependencies by removing them gradually

### How Do You Determine Uptime and Downtime in SRE?

Uptime and downtime can be determined by taking into account the service availability. For example, if the number of serviceable hours is 365 days * 24 hours with service availability of 99%, then:

Uptime = (365\*24)\*99/100 = 8672.4 hours or 361.35 days

Downtime = (365\*24)\*(1-99/100) = 87.6 hours yearly

### Benefits Of Strategically Burning The Error Budget To Zero

The error budget shouldn't be burned without a good plan at hand. However, if there is a proper strategy with some buffer budget for emergencies, it could mean adding a competitive edge to the product.

Error budget offers an allowance of errors so that engineers can explore risks without any repercussions from customers. By innovating new features and pushing them in a planned way such that the customer experience is minimally affected, the product can move ahead of the competition through features that have not yet been introduced in the wider market.

### Are Fixed Error Budgets Better?

Fixed error budgets ensure that the team properly evaluates every new decision that could eventually impact the customer's experience. Having a flexible error budget could enable the teams to take unprecedented risks with lower priority on disrupting the system and compromising reliability.