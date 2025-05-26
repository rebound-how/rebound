---
title: "How Does Chaos Engineering Work? "
description: Wondering how chaos engineering works & if you should use chaos
  experiments to test your systems? This article explores everything you need to
  know.
seo:
  description: Wondering how chaos engineering works & if you should use chaos
    experiments to test your systems? This article explores everything you need
    to know.
  title: How Does Chaos Engineering Work? 2022 Guide
category: Chaos Engineering
author: Aimee Pearcy
author_role: Technical Writer
author_image: /images/uploads/aimee-profile-photo.jpeg
date: 2022-06-28T16:37:47.666Z
featured_image:
  src: /images/uploads/pietro-jeng-n6b49ltx7nm-unsplash.jpg
  alt: chaos engineering
excerpt: Wondering how chaos engineering works & if you should use chaos
  experiments to test your systems? This article explores everything you need to
  know.
layout: ../../layouts/PostLayout.astro
---
## What is chaos testing?

Chaos testing is a way to test the integrity of a system. Its purpose is to simulate failures that could crash a production system in a controlled environment. This helps to identify failures before they cause unplanned downtime that disrupts the user experience.

Unlike standard testing, which tests a system response against a predefined result, chaos testing does not have a predefined result. Rather, the entire purpose of the experiment is to find out new information about the system.

This information can then be used to improve the system and avoid these incidents from happening unexpectedly in the future, which would cause much more disruption.

### Engineering chaos

'Chaos engineering' relies on the concepts underlying chaos theory – the study of apparently random or unpredictable behaviour in systems.

It is designed to improve the resilience of a system by providing information about its weaknesses. This prevents potential outages and helps to make sure that an organization meets its [service level agreements (SLAs)](https://reliably.com/blog/sre-basics-understanding-sla-slo-sli/).

### Why is chaos testing important?

Chaos testing helps build better and more resilient systems. You can never know when your systems will go down next, so testing can identify errors and vulnerabilities before you encounter the issue in real life.

Development is now also dominated by short, frequent release cycles. While there are many benefits to this, it also means that testing is often left until the last minute, or sometimes even skipped completely. As a result of this, the likelihood of defects in the code increases significantly, and things are more likely to go wrong.

### Who is responsible for chaos testing?

Chaos testing is usually carried out by a specific DevOps engineer, or by a site reliability engineer (SRE).

This person will typically be responsible for defining the required testing scenarios, carrying out the tests, and tracking the results. It is important that organizations try to minimize the impact on users while these tests are carried out.

#### Improving resiliency with chaos testing

Resiliency is an important requirement for applications. However, modern development practices have made it increasingly difficult to ensure.

Since DevOps started to [become more widespread](https://www.appknox.com/blog/history-of-devops#:~:text=The%20concept%20of%20DevOps%20emerged,it%20became%20quite%20a%20buzzword.) in 2009, many organizations have been merging their development and operations teams. This means that teams are now typically required to share responsibility for the deployment of the system, while simultaneously increasing deployment velocity. Meanwhile, testing has become automated as much as possible to keep up with this increased pace of development.

It is becoming increasingly apparent that traditional quality assurance is not enough anymore. As a result, an increasing number of organizations are hiring SREs to improve the reliability of their systems by carrying out chaos testing.

This process is designed to simulate how systems will respond to failures in a safe and controlled environment. It is one of the key ways that engineers are improving the resiliency and reliability of these systems.

#### Chaos testing vs stress testing

Chaos testing is similar to stress testing in that its purpose is to create abnormal or unstable environments that are designed to uncover breaking points in a system.

However, while stress testing typically focuses on a few key components, chaos testing can focus on a wide variety of factors – many of which are outside the scope of what would be considered standard testing considerations.

## How does chaos testing work in DevOps?

![chaos engineer](/images/uploads/bench-accounting-c3v88boorom-unsplash.jpg "chaos engineer")

First, the team should ensure that the system works, and that they can define a 'steady state' that acts as a control to indicate the standard behavior of the system. The team should hypothesize that this steady-state will hold throughout the testing period.

The purpose of chaos testing is literally to break the system. However, it's important to minimize the disruption to your users as much as possible. To do this, the team should make sure that their testing is limited to specific areas to reduce the chances of bringing the entire system down.

They should aim to test in a production environment so that it doesn't directly affect the system's users. There should also be a team on standby for incident response in case it becomes necessary.

Once the necessary precautions are in place, chaos testing can begin. The idea is to gradually introduce different variables to simulate real-world scenarios, and ultimately disprove the initial hypothesis. Ultimately, this can help to build a more reliable system.

### Chaos testing for AWS

Chaos testing for Amazon Web Services (AWS) is done using AWS Fault Injection Simulator. Fault injection involves deliberately introducing errors into a system to see whether the system can withstand and recover from them.

Amazon's Fault Injection Simulator lets teams set up experiments using premade templates. This helps to make sure that they can generate their desired disruptions.

These experiments can be run sequentially, and gradually build over time in an attempt to find hidden weaknesses. If specific conditions are not met, then the experiment is automatically stopped or rolled back.

### Chaos testing in production

Once adequate test coverage has been achieved, it is time to make sure that tests are run and mimicked in production. Production is the environment that users are in, which means that the traffic load is real.

Chaos testing in production is vital when it comes to testing the resilience of a production system, and it can provide vital insights. However, it is important to put measures in place to limit the potential impact of testing in production.

The engineering team can do this by carrying out small-scale experiments that are limited to a specific area of your software. This way, if something does go wrong, the impact will be minimized.

### Chaos testing microservices

Microservices are a type of architecture specifically designed to enable the fast, reliable delivery of complex applications. They increase scalability and distribute complexity more evenly by giving developers a smaller, more focused codebase to work with.

However, having many different services makes it increasingly difficult to predict the behavior of the system and understand it. Chaos engineering can help to do this, and ultimately build a more resilient microservices architecture.

At the beginning of the testing process, it is important to try and minimize the 'blast radius'–the proportion of containers that the team is running the experiments on–and then gradually increase it as the experiment increases and you get more comfortable.

### Chaos Monkey testing

['Chaos monkey testing'](https://netflix.github.io/chaosmonkey/) was created by Netflix to help them to perform consistent testing. The idea behind this is that there are multiple 'chaos monkeys' and that each one is added into the system to introduce a specific issue.

For instance, the 'Latency Monkey' is designed to introduce artificial delays, the 'Janitor Monkey' is designed to remove unused resources, and the 'Conformity Monkey' is designed to find instances that don't adhere to best practices.

### Examples of chaos tests

![chaos engineering](/images/uploads/mohammad-rahmani-_fx34keqiew-unsplash.jpg "chaos engineering")

Here are some examples of common chaos tests:

#### Simulating a high CPU load and sudden increase in traffic

This is known as 'load testing'. It is designed to simulate the actions of multiple people using a program or website.

The test results will reveal the response time and the throughput of the system. These can be compared to the system benchmarks to see whether the system is performing to the required standard.

#### Simulating the failure of an AWS Availability Zone (AZ)

This is known as the 'AZ failure injection'. It simulates a critical problem with one of [Amazon's availability zones](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/). If an application is reliable, then it should be resilient against these failures.

#### Simulating the failure of a micro-component

Building micro-components is a relatively simple process – the difficulty is making them resilient to failure.

Simulating the failure of micro-components is vital, and it can help you to figure out whether a failure will have a wider effect on the rest of your application before something goes wrong.

#### Injecting latency between services

Latency spikes are inevitable, which means you must design your system for them to minimize the impact on your users as much as possible.

Artificially injecting latency between services can help you to make sure that the inter-service communications within your system have the correct timeout values.

## Advantages and disadvantages of chaos testing

### Advantages

Chaos testing is almost a necessity when it comes to strengthening the integrity of large, complex systems. This is because there is a significant gap between how many engineers think their systems will fail, and how they actually fail.

Chaos testing helps to reduce this gap by helping IT teams quickly identify and resolve issues that might have otherwise gone unnoticed and spiraled into larger issues down the line. Making the system more[resilient](https://reliably.com/blog/what-does-it-mean-to-build-resilient-service-applications/) to failures means that unplanned downtime and outages are less likely to occur, which typically improves the user experience.

For instance, PagerDuty's 2021 report revealed that IT teams experienced an average of [105 critical incidents](https://www.pagerduty.com/assets/The-State-of-Digital-Operations-Report-2021.pdf) per month in 2020. The average annual cost per organization for these incidents is $158,760.

### Disadvantages

Chaos testing can take a lot of time and resources, which means that it is usually very expensive to implement. As a result, it is typically not appropriate for smaller systems, or for systems that are not critical to business success.

This means that if failures are acceptable and don't need to be resolved until the end of the day, or if the SLAs don't stipulate an extremely high level of uptime, chaos testing may be unnecessary.

In addition, implementing chaos testing carelessly or incorrectly can result in things going wrong that can impact users, which could prevent the organization from meeting its SLAs.

## Tools to get started with chaos testing

The growth of chaos testing has led to the development of several commercial and open-source tools that are designed to make the process easier.

Some of the tools that organizations can leverage to get started with chaos testing include:

- [Chaos Toolkit](https://chaostoolkit.org/) – an open-source tool with many extensions that let you fine-tune your experiments.
- [Gremlin Chaos](https://www.gremlin.com/chaos-engineering/) – a tool designed to test the reliability of cloud infrastructure and applications.
- [Litmus Chaos](https://litmuschaos.io/) – an open-source tool that induces chaos tests in a controlled way to help teams to identify weaknesses.
- [Chaos Monkey](https://netflix.github.io/chaosmonkey/) – a tool that randomly terminates instances in production to make sure that they have been designed to be resilient against these failures.
- [Reliably](https://reliably.com/product/) – a developer-centric platform where chaos engineering meets service reliability, which integrates quickly and easily with your developer workflow.




