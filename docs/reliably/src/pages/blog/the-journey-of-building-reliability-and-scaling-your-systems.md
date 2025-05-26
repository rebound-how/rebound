---
title: The Journey Of Building Reliability And Scaling Your Systems
description: >
  Scaling your systems to serve billions of requests per month is never an easy
  path, so how do you build the right technology infrastructure for your
  services?
category: Reliability
author: Stoyan Yanev
author_role: Principal DevOps Engineer
author_image: /images/uploads/1650738059580.jpeg
date: 2022-05-14T12:42:02.457Z
featured_image:
  src: /images/uploads/chris-ried-ieic5tq8ymk-unsplash.jpg
  alt: building reliability
excerpt: Scaling your systems to serve billions of requests per month is never
  an easy path, so how do you build the right technology infrastructure for your
  services?
layout: ../../layouts/PostLayout.astro
---
Starting small and scaling your systems to serve billions of requests per month is never an easy path, so how do you build an infrastructure whilst making the right decisions and compromises for your services?

Choosing the right technology stack and ensuring your CI/CD pipeline is reliable are two key steps towards this which we will explore.

## Technology Ecosystems

Huge corporations are underpinned by a number of technology teams and each company requires a number of performance tables and customer-friendly websites which are built using a collection of different interface components.

For example, when [The Times](https://www.thetimes.co.uk/) decides that they want to build an index page, that page will be constructed using a variety of article cards. This same need exists for many other global corporations.

Multiple product teams will spend resources on building an article card component in their own unique way to satisfy the needs of their business stakeholders.

These components have traditionally looked and behaved a little differently but in essence, the variation of a common base component is how the creation of an ecosystem of products is decided upon.

## Which Technologies Are Typically Used?

![building reliability](/images/uploads/alexander-sinn-kgltfcgfc28-unsplash.jpg "building reliability")

[Typescript](https://www.typescriptlang.org/), [Node.js](https://nodejs.org/en/), and [GraphQL](https://graphql.org/) are common tech stacks used (particularly in publishing).

Most infrastructures typically reside in AWS and due to the high traffic and scaling needs, [Kubernetes](https://kubernetes.io/) and [Amazon EKS](https://aws.amazon.com/eks/) are the go-to choice.

This type of infrastructure can make use of [Terraform](https://www.terraform.io/) which can help support serving traffic that receives approximately several billion requests per month.

### Avoiding downtime when making technology choices

Guaranteeing high availability, with no downtime and no performance issues are critical when making technology decisions - each mistake or a minute of downtime is costly.

Ensuring optimal test coverage, unit tests, integration tests, small tests, end-to-end tests and load tests is important.

The concept of PR environments should also be considered. Each new pull request creates a whole new environment that can be used to test and verify application behavior.

The automation of these processes creates ease for [engineers](https://reliably.com/blog/what-is-a-site-reliability-engineer-and-why-you-need-one/) as they require minimal human interaction.

## How do you ensure your CI/CD pipeline is reliable?

### 1. Husky and Git Hooks

The first step to ensure your CI/CD is reliable is to put git hooks in place.

There is a useful tool called [Husky](https://typicode.github.io/husky/#/) which is incremental in linking your commit messages to run tests and linking your code. This can all be done when you commit or push.

You can use pre-commit hooks and pre-push hooks with Husky. This ensures that all engineers have taken care of their test coverage and linting on their changes every time they introduce a new change to the project.

### 2. Environments

Developers will tend to have a lot of environments - request environment, deaf environment, staging, and production environments to name a few.

Environments enable you to test your features in live conditions easily.

The pull request environment is created by a trigger from Github whenever a pull request is opened, pointing to some external services and resources being live in the developer environment.

Engineers can easily test the new features they introduce before even merging their code into the master branch. As a result, the PR environment resembles the deaf environment and the staging improvisation environments are almost 100% identical with a few exceptions.

### 3. Helm Umbrella Tag Triggers

[Helm charts](https://helm.sh/) are useful within your Skit API as it is helpful when deploying.

You should make use of the tags that are generated to check which pieces of the application are updated when a pull request is created.

You can then trigger only the necessary workflows inside of circle CI which results in no unnecessary redeployments of resources. This allows you to only deploy what you have changed every time.

Making use of a federated [GraphQL](https://graphql.org/) schema on each deployment, you can compare the changes within the GraphQL schema of each wrapper that you have plus the federated schema in the gateway.

For these checks, you can use the tool [GraphQL inspector](https://www.graphql-inspector.com/) to prevent pushing breaking changes to the schema which result in queries or mutations that refuse to work properly.

You can also make use of [Lerna](https://lerna.js.org/) which is a tool created to generate change locks on each release made. Lerna also aids in managing monorepo with Git and uses it to burn the versions of the underlying packages in the project based on the changes made.

Instead, strict versions on dependencies inside the project are used as splitting up large codebases into separate independent version packages is extremely useful for code sharing between all the packages inside of the monorepo.

## Testing Strategies You Should Use For Better Reliability

### Unit Tests

Unit Testing involves checking code to deliver information early and often, speeding your testing strategies.

You should aim for 100% coverage of unit tests and functional tests on all of the wrappers you have, plus the gateway which keeps the super graph, which is the federated schema.

### Wall Tests

You can use [Taurus](https://gettaurus.org/) and [BlazeMeter](https://www.blazemeter.com/blog/test-automation-in-practice-a-tutorial) to carry out wall tests which are automation tools that use different executors.

They create a test scenario whereby the tool starts to simulate requests from a lot of users to select services. These services possess different intensities like concurrency, a ramp-up of traffic, iterations, and other modifications.

BlazeMeter is the tool that is used to read the reports that come from different test runs that Taurus did which makes the process extremely visible to engineers.

### Schema Tests

Schema tests should be completed for all subgraphs in each wrapper. In the federated supergraph, you should have contract testing where you can use pact.

A pact is a schema contract between two services. They are tests where you create a contract between two services which is essentially a stop request-response.

When you deploy a service, you verify your service response against this contract to make sure that the other service is subscribed and therefore, invalid or wrong messages will not be received.

### Federation End-To-End Tests

Federation end-to-end tests can be used on the gateway. These are tests that use life instances of the gateway whenever all images are spun up and running.

A real request is sent to the gateway in which engineers can use fields that are federated between at least two services. For example, Service A and Service B ensure that federated types are working correctly. There are no stops or mocks involved in these tests, they're just using live data. The engineers can then receive a real response from their underlying data sources.

## Leveraging Health Checks For Reliable Deployment

It's important to leverage health checks on deployment as they allow engineers to implement safeties into your applications such as user measures. User measures can prevent users from getting served incorrect data or the supergraph failing to be built correctly.

Health checks also account for a wide range of arrow conditions in which an application can become unhealthy. For example, resource exhaustion or a failure to connect to the upstream services due to network conditions may be an indication that a service is unhealthy.

This may be due to the gateway being dependent on the other services to build its own supergraph and therefore, Kubernetes services generally will not add a pot to the pots that are routable until the pods enter a status that shows that they are ready. This is determined by Kubernetes and the ready status is based on the health checks being set up, otherwise, this means that all of the containers in the pots are running.

You can execute health checks by making an HTTP request against the TCP at the configure 10 points of where the pods are. A status between 200 and 400 is desirable which allows the application to be clear about its health and generates a lock that could be pretty useful when you debug issues.

Health checks are essential because before the gateway is ready to be started, all the required parts that provide subgraphs are running so the super graph could be composed without any hassle.

## Monitoring Your Services

For monitoring, there are many tools that offer excellent observability such as [New Relic](https://newrelic.com/) with its APM, dashboards, and alerts.

The most used features are the distributed tracing, error rates and logs. These enable engineers to see a large amount of throughput information and to have visibility over the Kubernetes spots health and utilization. For example, the percentage of CPU or memory is utilized and these facts and figures can easily be analyzed what is happening within the pots as they have customized this GraphQL plugin for the new railing.

As a result, engineers can have separate dashboards for each different wrapper they have, which provides a lot of insights on how they are scaling and what traffic is going through each one of them. This can be used to narrow investigations if any problems occurred.

## Disaster Recovery

Alerting can be used to send messages and notifications to the teams responsible for the services which are failing. Alerts are mostly relying on slack channels and these live channels are set up specifically for that purpose.

When a notification from [Slackbot](https://slack.com/intl/en-gb/help/articles/202026038-An-introduction-to-Slackbot) is sent, an engineer should investigate what the issue might be.

Notifications are helpful as they provide a link leading directly to the issue that triggered the alarm, making it easier to recognize where the problem might be and ensuring that the reaction time from engineers is even faster.

An on-call rota can be used in which engineers are available outside working hours.

Each team has a run book which is a document with the most commonly occurring problems providing a step-by-step solution for them which enables all engineers from other teams to provide support to different teams whenever there is an issue.