---
title: What Is A Service Level Indicator?
description: >+
  Service level indicators can help make measuring reliability easier but what
  are service level indicators and why are they important? Learn more about
  SLIs.

category: Reliability
author: Aimee Pearcy
author_role: Technical Writer
author_image: /images/uploads/aimee-profile-photo.jpeg
date: 2022-03-23T09:47:48.732Z
featured_image:
  src: /images/uploads/pexels-thisisengineering-3861957.jpg
  alt: what is a service level indicator
excerpt: Service level indicators can help make measuring reliability easier but
  what are service level indicators and why are they important? Learn more about
  SLIs.
layout: ../../layouts/PostLayout.astro
---
Measuring reliability can be [challenging](https://reliably.com/blog/the-challenge-of-reliability-for-developers/) for organizations. But service level indicators (SLIs) can help to make the process easier.

## What is a service level indicator?

Service level indicators (SLIs) are quantifiable measures of the reliability of a service. They are defined in Google's [SRE handbook](https://sre.google/sre-book/service-level-objectives/) as a 'carefully defined quantitative measure of some aspect of the level of service that is provided.'

SLIs can help organizations to view their performance metrics and quantitatively measure how they are affecting the level of service that is being provided to the end-user at a given time. They are essential for any organization that is trying to provide exceptional service – especially for those who are looking to improve their service in the future.

Today, SLIs are widely used by DevOps engineers to discuss the quality of service (QoS) and create shared goals to promote reliability within a system. They have become one of the primary metrics of Site Reliability Engineering (SRE).

### Types of service level indicators

Here's a rundown of the different types of SLI, and how they can be calculated:

#### Request-based SLIs

Request-based SLIs measure the number of complete requests in a service.

The general formula for a request-based SLI is:

Request-based SLI (%) = (good requests / total requests) * 100

For example, if a service has 186 successful requests out of 200 requests, then the overall success rate is 90%.

#### Window-based SLIs

Window-based SLIs measure a service's reliability threshold over a specified period of time.

The general formula for a window-based SLI is:

Window-based SLI (%) = (good time periods / total time periods) * 100

For example, if a service has 1,000 'good time periods' that meet the set objectives, versus 1,200 total time periods during peak hours, then an organization can determine that 97% of the measured windows have been successful.

### Service level indicator examples

![Service level indicator](/images/uploads/austin-distel-guij0yszpig-unsplash.jpg "Service level indicator")

Examples of specific SLIs metrics that an organization might want to track include:

* **Request latency** measures the delay in the system. Lower latency is associated with a more positive user experience. A 2019 [study by Portent](https://www.portent.com/blog/analytics/research-site-speed-hurting-everyones-revenue.htm#:~:text=The%20first%205%20seconds%20of,(between%20seconds%200%2D5)) revealed that website conversion rates drop by an average of 4.42% with each additional second of load time between seconds zero to five.
* **Error rate** measures how frequently errors are introduced into a system.
* **Traffic** measures how much demand is being placed on a system.
* **Availability** measures how often the system is online and accessible by users. While it might not sound like there is much difference between 99.995% availability and 99.671%, it is [quite substantial](https://www.rfcode.com/data-driven-data-center/bid/300651/Data-Center-Uptime-Why-0-1-Makes-a-Difference). Over a year, the former will be offline for only 0.44 hours in total, while the latter will be offline for a total of 28.84 hours.
* **Durability** measures the likelihood that the data can be retained for a long time.
* **Saturation** measures how 'full' the system is.

Google refers to request latency, traffic, error rate, and saturation as the 'four golden signals' of monitoring.

Google's SRE handbook suggests that 'if you measure all four golden signals and page a human when one signal is problematic (or, in the case of saturation, nearly problematic), your service will be at least decently covered by monitoring.'

### SLI metrics to track

Choosing SLI metrics to track can often seem overwhelming. But when it comes to monitoring a system, it should be noted that it is not necessary to track every metric.

Getting the balance right can be difficult. Tracking too many metrics runs the risk of the metrics that really matter going unnoticed, while tracking too few metrics could leave important parts of the system unmonitored.

Taking the time to figure out what users ultimately want from a system will allow organizations to select a few indicators.

In general, systems tend to fall under one of a few different categories:

* User-facing servicing systems should prioritize availability, latency, and throughput.
* Storage systems should prioritize latency, availability, and durability.
* Big data systems should prioritize throughput and end-to-end latency.

All systems should also prioritize correctness, which monitors whether the right data is being retrieved and returned to the user. However, this is often a property of the data in the system and not the infrastructure. As a result, it is often not the responsibility of the SRE to manage this.

## SLI vs. SLOs vs. SLAs

To fully understand how SLIs work, it is vital to also have an understanding of service level agreements (SLAs), and service level objectives (SLOs).

### Service Level Indicator (SLI)

An SLI compares the actual figures against the objectives of the service to determine whether there is a difference between them. If there is a difference, the organization can then decide where improvements are necessary.

### Service Level Agreement (SLA)

An SLA is an agreement between a service provider and an end-user. It includes the service provided, support, cost, and performance. Sometimes, it can outline compensation, such as a payment or rebate, that the customer will receive in the case of a missed objective. [Tracking SLAs can be difficult](https://www.atlassian.com/itsm/service-request-management/slas), and changing them can be even harder.

### Service Level Objective (SLO)

SLOs are goals created by organizations. They will eventually be compared against the SLIs – there's no point in having an SLO if you don't have an SLI to measure against it.

An SLO is part of the SLA, and it is designed to provide a method of evaluation of the performance of a service, usually through outlining internal goals. For instance, if an organization sets an SLO of a 97% availability rate, and an SLI shows a 98% availability rate, then the organization can determine that it has met its objective.

To summarise: SLIs are measurements of the performance of a system, SLOs are the performance objectives an organization aims to achieve, while SLAs outline the consequences of not meeting these SLOs.

## How do you define service level indicators?

![service level indicators sli](/images/uploads/pexels-elevate-digital-1647919.jpg "Service level indicators (SLI)")

To define your SLIs, you must first create and define your SLOs so that you know what you will ultimately be comparing your SLIs against.

Once you have defined your SLIs, you should decide what metrics you want to use to measure each SLI so that you can compare it against your SLOs.

Finally, you should make sure that you update your SLIs for changes to the system. These changes could include factors such as how many users or requests the system processes, and how high the latency is. You may also need to change your SLIs based on how consistently they are meeting your SLOs.

### How are SLIs relevant in SRE?

SLIs are relevant to SRE because they provide a way for organizations to define which parts of their system are the most important, and provide them with a thorough overview of their system.

Choosing appropriate SLIs means that the SRE team can quickly take corrective action if something goes wrong. It also provides team members with confidence that the service is healthy if the SRIs are being met.

As a result, when deciding which SLIs to measure, it is important to prioritize metrics that have more of an effect on the end-user of the service.

### How is an SLI calculated for SRE?

Once you have defined your metrics, you can use the SLI equation to calculate the correct SLI for your organization.

SLI equation = ( good events / valid events ) * 100

The resulting SLI will be a number between 0 and 100. In general, a result closer to 100 is linked to a better user experience. A lower SLI score suggests that there are more improvements to be made.

## How to implement SLIs

Before implementing your SLIs, it is important to have a solid understanding of why you need SLIs in the first place. You should always be thinking about how your SLIs are benefitting your customers.

Once this is in place, you must select which SLIs to use. These should be specific – the more specific your SLIs are, the better and more accurate data you can collect.

Next, you must decide how frequently to measure your SLIs. Some SLIs can be measured monthly or bi-monthly, whereas other SLIs might need to be measured daily, depending on your SLAs.

Now that you've started measuring your SLIs, you can gather baseline data that you can use to compare your future measurements against.

Finally, you must regularly check your SLIs to see if you're meeting your SLOs. This ensures that you're meeting your objectives. If you're not meeting your objectives, you can take steps to realign your system to make sure that you are meeting your objectives.

## Benefits of SLIs

In conclusion, SLIs can have many benefits for organizations. In particular, SLI implementation can help organizations to:

* View performance metrics
* Track customer satisfaction
* Identify areas for improvement
* Immediately notice if something is not going as expected and take corrective action
* Encourage engineers to prioritize tasks and create shared goals