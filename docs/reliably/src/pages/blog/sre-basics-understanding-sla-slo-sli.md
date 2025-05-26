---
title: "SRE basics: Understanding SLAs, SLOs and SLIs"
description: "SLAs, SLOs and SLIs are fundamental to site reliability
  engineering (SRE), but what are they and why are they important for delivering
  services? "
seo:
  title: "SRE basics: Understanding SLAs, SLOs and SLIs"
  description: "SLAs, SLOs and SLIs are fundamental to site reliability
    engineering (SRE), but what are they and why are they important for
    delivering services? "
category: Reliability
author: Aimee Pearcy
author_role: Technical Writer
author_image: /images/uploads/aimee-profile-photo.jpeg
date: 2022-05-27T15:05:47.637Z
featured_image:
  src: /images/uploads/redd-5u_28ojjgms-unsplash.jpg
  alt: SLA SLO SLI
excerpt: "SLAs, SLOs and SLIs are fundamental to site reliability engineering
  (SRE), but what are they and why are they important for delivering services? "
layout: ../../layouts/PostLayout.astro
---
SLAs, SLOs and SLIs are fundamental to site reliability engineering (SRE), but what are they and why are they important for delivering services?

## SLA: Service Level Agreement

### What is an SLA?

A [service level agreement (SLA)](https://reliably.com/blog/10-reasons-you-need-a-service-level-agreement-and-why-its-important/) is an agreement between the service provider and the end-user that is designed to make sure that the system runs as expected and that the user's needs are being met. Often, SLAs will also outline compensation that the end-user can receive if objectives are missed.

For instance, Google's [Cloud VPN SLA](https://cloud.google.com/network-connectivity/docs/vpn/sla) guarantees a Monthly Uptime Percentage of &gt;=99.9% for its classic VPN, and &gt;=99.99% for its high-availability (HA) VPN.

At first glance, these metrics might not appear too different. However, while a [99.9% uptime guarantee](https://uptime.is/) can allow for up to 8 hours, 45 minutes, and 56 seconds of downtime per year, a 99.99% uptime guarantee allows for only 52 minutes, 35 seconds of downtime per year – a stark difference.

If the service does not meet these targets, then the user is entitled to financial credit. The amount of credit they will receive depends on how much the target is missed.

SLAs should be created by considering what matters to the customer. They should be high-level and written using plain language to make sure that they are easy to understand and to avoid confusion.

### The challenges of SLAs

SLAs come with lots of challenges. They are typically very difficult to measure, report on, and meet.

One of the biggest issues is that managers typically have to extract a significant amount of raw data to see how they are performing against an SLA, which can end up being time-consuming.

It's not just measuring SLAs that can be difficult – they often have to be hard-coded into service desks which means changing them is often an arduous task. As a result of this, SLAs often evolve much more slowly than the business does. This means that SLAs that were set a long time ago sometimes end up being honored simply because they're there.

There's typically also little flexibility in reporting SLAs – they're either met, or they aren't.

Another common issue is that SLAs are often created by legal teams who are not responsible for making sure that they are met. To try and mitigate this and help to make sure that SLAs reflect the real world, organizations can try and ensure that tech teams are also involved in the creation of SLAs.

Finally, SLAs are often created using complicated language that customers don't fully understand, which can create misunderstandings later on. To reduce the chances of this becoming a problem, it is important that organizations make sure the language they use is as simple as possible, and that there is little room for misunderstanding.

### Who needs SLAs?

SLAs can help teams to build an [error budget](https://reliably.com/blog/error-budgets-ultimate-sre-guide-for-teams/) to leave room for failures and rapid changes to make sure that customer expectations can be met. They can also help to reassure customers that they will be compensated if the expected level of service is not reached.

Organizations that provide services to users in exchange for a fee typically need SLAs so that they can outline the compensation available if the objectives are not met.

Organizations providing free services do not typically require SLAs, as they are not expected to provide compensation.

## SLO: Service Level Objective

![SLO ](/images/uploads/jud-mackrill-qnt9iigv444-unsplash.jpg "SLO ")

### What is an SLO?

Service level objectives (SLOs) are the individual promises that organizations make to their customers. Each SLO measures a specific metric, such as error rate, uptime, or request latency. SLOs are typically defined within an SLA, and measured against SLIs to make sure that the right objectives are being met.

The primary purpose of SLOs is to help teams to understand what goals they are trying to meet, so that they can measure how close they are to their targets and adjust their strategy accordingly.

If the availability of a service violates the SLO, then the team must react quickly to make sure that it does not breach the SLA. Otherwise, they may have to provide compensation to the users of the service.

### The challenges of SLOs

SLOs typically share many of the same problems as SLAs: they are often vague, complicated, and difficult to measure. It is also common for organizations to track too many metrics – even the ones that don't matter to customers.

To try and mitigate this issue, organizations should think carefully about what metrics they want to include as SLOs – only the most important and most relevant should be chosen. After all, there is no point in setting an SLO if you don't have an SLI to measure against it.

SLOs should be clearly defined, simple, and easy to measure. This will make it easy to test whether they have been fulfilled, and will also reduce the time spent by engineers trying to figure out how to overcome roadblocks that don't make sense.

### Who needs SLOs?

SLOs can be useful for a wide variety of organizations that want to evaluate the performance of a service and improve its reliability.

Given that engineers are a scarce and expensive resource, it is important that they invest their efforts in the most important services that will have the greatest impact. SLOs help them to do this by informing them what they should focus on.

## SLI: Service Level Indicator

![SLI SRE](/images/uploads/austin-distel-wd1lrb9oeeo-unsplash.jpg "SLI SRE")

### What is an SLI?

A [service level indicator (SLI)](https://reliably.com/blog/what-is-a-service-level-indicator/) is a way of quantitatively measuring service reliability. It helps organizations to view performance metrics, track customer satisfaction, identify areas for improvement, and quickly notice when something is not going as expected so that teams can take corrective action before the problem spirals out of hand.

SLIs can help organizations to promote reliability by giving them a transparent way to compare the actual figures against a set of objectives to determine the difference between them.

For example, some of the most common SLI metrics that an organization might want to measure to make sure that it is meeting customer expectations include request latency, traffic, availability, error rate, throughput, and response time.

### The challenges of SLIs

When it comes to creating SLIs, the biggest challenge by far is keeping them simple and tracking the right metrics.

Technology has made it possible to track virtually any metric we can think of with the click of a button, which means that it can be tempting to track lots of metrics that don't matter, just because we can. However, this quickly overcomplicates the process and can end up wasting time and resources while making very little overall difference to the end-user.

It can also distract engineers from focusing on the most important performance indicators and can lead them to feel overwhelmed and burned out from trying to spin too many plates and focus on too many metrics.

### Who needs SLIs?

There's no point in having service level agreements (SLAs) or service level objectives (SLOs) – without having SLIs to monitor how the service is running and determine the actual figures.

SLIs are vital for measuring performance and helping organizations to understand where and when improvements need to be made. By choosing appropriate SLIs, teams can quickly identify issues and take corrective action if something goes wrong. Without SLIs, it becomes very difficult to accurately measure performance and get a clear picture of how reliable the system is.

## The difference between SLIs, SLOs, and SLAs

Ultimately, SLIs, SLOs, and SLAs are all used to help organizations to improve their reliability. However, they have some key differences:

* SLIs are actual measurements taken by an organization that measures the performance of a system to make sure it is reaching its objectives.
* SLOs are performance objectives that an organization is trying to reach. Unlike SLAs which are primarily used for paid services, SLOs are useful for both paid and free services.
* SLAs are the promises that an organization has made with the end-user of the system, as well as the consequences that will result if these promises are not met. This is an external metric that is visible to customers. If the SLA is breached, then there will be consequences. For instance, the organization may need to refund some money to customers or provide additional subscription time for free.

### How does this impact SRE?

SLIs, SLAs, and SLOs are the cornerstones of SRE, as they are a vital part of measuring reliability. They should be a key part of system requirements – especially if you're building a system from scratch.

They provide organizations with a thorough overview of a system to help them understand whether it is available, useful, and reliable.

They also help development and operations teams to set boundaries and understand which tasks need to take priority at a given moment. Finally, they provide end-users with a guarantee that their expectations will be met, or that they will receive compensation.

SLIs, SLAs, and SLOs should be linked explicitly with organizational objectives to provide a clear understanding of whether the choices you are making are helping or hurting your business.

## SLA, SLO, and SLI best practices

![SLA SLO SLI ](/images/uploads/cherrydeck-upsef48wagk-unsplash.jpg "SLA SLO SLI ")

SLAs should be kept simple, and focus on the expectations of the end-user. SLOs are used internally within the team and are typically tighter than SLAs. SLAs are used externally and are designed to be easily understood by the end-user.

All that the end-user cares about is that the system functions as expected – and SLAs should reflect this. They should be expressed as simply as possible, without using complicated language that could cause confusion. As well as keeping customers satisfied, this will make it easier for the engineers delivering the promises to make sure they can meet them.

SLAs should include factors out of your organization's control. It can be easy to forget that sometimes some of your organization's goals will be limited by factors that you can't control. For instance, who is at fault if you promise to resolve all incidents within 24 hours, but your customer takes several hours to reply to one of your messages?

The number of SLIs and SLOs should be kept small. While it can be tempting to try and track every single metric, it is not necessary. Engineers have limited time and resources, so it is important that they put their energy into implementing things that matter most.

Under-promise and overdeliver. Just because you can promise something, it doesn't mean that you should. Leaving an error budget means that customers will be impressed when you exceed expectations, and it also reduces the pressure on your team.

## How do you measure SLIs, SLOs, and SLAs?

To form the basis of your SLIs and understand how reliable your service is, you should measure the rates of successful and unsuccessful queries.

SLIs are measured as a percentage – a measurement of 0% indicates nonexistent performance, while a measurement of 100% indicates perfect performance. A higher percentage means that the site is functioning well, which typically means that customer satisfaction will be higher.

SLOs are essentially the minimum percentage that an organization would like to achieve for its SLIs.

Given that hitting 100% all the time is likely to be unrealistic in most scenarios, an organization might set its SLO to 95%. While a more reliable service may seem more appealing to customers, it will cost more to operate, and can also slow down the velocity of development. This means that many organizations set their SLOs to the lowest level of reliability that they can get away with.

SLAs should be revisited regularly to make sure you're measuring the right metrics within your organization. You should consistently be checking that they align with your business goals and your users' goals. You should also be in regular contact with your users to get their feedback to try and identify areas for improvement. This means you can remove SLAs you no longer need and implement more useful ones. Teams should have full support from management when removing old SLAs and implementing new ones.

SLIs, SLOs, and SLAs are each created based on the assumption that a service will not be available 100% of the time.

Downtime, whether planned or unplanned, is inevitable – and it's important that customers understand this.