---
title: How To Reduce Technical Debt
description: How can we reduce technical debt? Many companies end up acquiring
  lots of technical debt without even realizing it. Here are 17 ways to reduce
  technical debt.
category: Technical Debt
author: Aimee Pearcy
author_role: Technical Writer
author_image: /images/uploads/aimee-profile-photo.jpeg
date: 2022-05-02T13:40:53.648Z
featured_image:
  src: /images/uploads/wes-hicks-4-eetnac1s4-unsplash.jpg
  alt: reduce technical debt
excerpt: How can we reduce technical debt? Many companies end up acquiring lots
  of technical debt without even realizing it. Here are 17 ways to reduce
  technical debt.
layout: ../../layouts/PostLayout.astro
---
## What is technical debt?

Technical debt is the implied cost of the additional work that is required when a team chooses a quick, easy solution that is limited, instead of a more well-thought-out, higher-quality solution that would take longer. Essentially, it's what happens when teams prioritize speed over quality.

Examples of technical debt include untested code, unreadable code, dead code, duplicated code, or outdated documentation.

### Why is it important to reduce technical debt?

It is important to reduce technical debt because it can quickly build up and accumulate 'interest' if it is not dealt with. This is because time and resources are spent writing new code on top of code that doesn't work as it should. Often, undoing these mistakes will require rewriting code from scratch.

### What causes technical debt?

* **Time pressure:** leads development teams to take shortcuts when writing code, skip testing, or releasing software that doesn't have key capabilities.
* **The fast-paced nature of the software industry:** means that software might already be outdated by the time it is released to the marketplace.
* **Outdated technology:** programming languages, frameworks, and libraries that are no longer supported.

### How much technical debt is acceptable?

It's unrealistic to expect to completely eradicate technical debt, and the debt doesn't necessarily have to be a bad thing. The 'acceptable' level of technical debt depends on the project in question. The most important thing is that managers understand [how to measure the technical debt](https://reliably.com/blog/how-do-you-measure-technical-debt-a-guide/) and make informed decisions about it.

## Types of technical debt

![reduce technical debt](/images/uploads/oskar-yildiz-gy08fxem2l4-unsplash.jpg "reduce technical debt")

The four key types of technical debt are:

* **Architectural debt,** which refers to the design of the system.
* **Code debt,** which refers to issues within the source code.
* **Infrastructure debt,** which refers to issues related to the operating environment.
* **Test debt,** which refers to a lack of testing, or bad test coverage.

### Are bugs technical debt?

Bugs are not technical debt. Technical debt is something that we incur by choice. Because we do not keep bugs in our code by choice, they do not count as technical debt.

### Is documentation a technical debt?

A lack of software documentation can be a significant form of technical debt.

## How can we reduce technical debt?

### 1. Acknowledge technical debt

Many companies end up acquiring lots of technical debt without even realizing it. While a small amount of technical debt isn't necessarily a bad thing, ignoring technical debt means that it can quickly build up without teams even noticing it.

According to a [2021 survey](https://assets.website-files.com/5f922f81cc30586744dc7122/60e306c6db6224328eaf47a3_Tech%20debt%20report.pdf) by stepsize that surveyed over 200 engineers, engineering leads, and CTOs in an attempt to understand the impact of technical debt, 52% of engineers said that they believed technical debt negatively impacts their team's morale.

Acknowledging technical debt earlier and being aware of it means that it can be acknowledged and tackled quickly before it has too much of an impact.

### 2. Measure the technical debt

Measuring how and when your team is being slowed down by technical debt can help you to identify the business impact of the technical debt.

To measure technical debt, you first have to make sure that you document it correctly. You should be sure to track the type of issue you are experiencing, the person responsible for addressing it, as well as the consequences of not paying off this debt.

This can help to transform the debt from an abstract concept, into a series of measurable, achievable tasks.

### 3. Define a strategy to manage technical debt

The approach you take to manage technical debt largely depends on the amount of technical debt you have.

If your technical debt allows you to reach your business goals then you may choose to do nothing. If you are dealing with a complex legacy system, then the best option may be to replace the whole system. If your debt falls in between these two extremities, then you may choose incremental refactoring, which focuses on dedicating time and resources to reducing technical debt every single sprint.

### 4. Use best practices

You should make sure that your team is aware of the [best practices for code refactoring](https://www.altexsoft.com/blog/engineering/code-refactoring-best-practices-when-and-when-not-to-do-it/) and reducing technical debt. This often requires adopting a new approach that facilitates long-term thinking, instead of a short-term approach that simply focuses on delivering projects on time.

This may be particularly difficult if you're in the process of modernizing legacy applications – you'll need to strike a balance between remaining consistent with existing approaches, and maintaining best practices.

### 5. Educate non-technical stakeholders

![non-technical stakeholders](/images/uploads/sigmund-im_cq6hqo10-unsplash.jpg "non-technical stakeholders")

Often, the people in charge of making the decisions don't fully understand what technical debt is – let alone how to go about reducing it, or the importance of reducing it. In many cases, non-technical stakeholders can view the process of reducing technical debt as an annoyance that takes time away from delivering new features.

If you can clearly explain the importance of managing technical debt to non-technical stakeholders, then you're more likely to get them on your side.

### 6. Choose a flexible architecture

Choosing the right architecture is vital, and there are many factors that you must take into account. You should make sure that the architecture you choose is flexible enough to accommodate changes, and that it is also scalable and secure.

You should also make sure that the architecture you select will not require constant refactoring, as this can quickly send your team down a rabbit hole and eat up lots of time, money, and resources that would be best spent elsewhere.

Choosing a flexible, easily-scalable architecture will allow you to extend it at the beginning of each iteration when you're adding new features.

### 7. Carry out routine code reviews

Although code reviews are often overlooked, they are an important part of reducing technical debt because they can significantly improve the quality of code. Code reviews can also be a valuable learning experience for your team.

To simplify the process as much as possible and make sure that code reviews do not become a burden, managers should make sure they are scheduled frequently.

A large-scale [study](https://www.michaelagreiler.com/wp-content/uploads/2019/03/Code-Reviewing-in-the-Trenches-Understanding-Challenges-Best-Practices-and-Tool-Needs.pdf) on code reviews at Microsoft that observed and surveyed over 900 developers about their code review practices revealed that 36% of the developers said they perform code reviews multiple times a day.

Another 39% of the developers said they do code reviews at least once per day. 12% do code reviews multiple times a week, and only 13% said they did not do a code review in the past week.

Developers should ensure that they break down large pull requests into smaller, simplified requests that do not appear too intimidating. All developers should also have access to a coding style guide so that time and resources are not wasted on trying to agree on minor details.

### 8. Track and monitor debt backlogs

To make sure your team is staying on top of your technical debt and consistently working to pay it off, you should make sure that technical debt is tracked in your backlog. This will make sure it always remains a priority, and that it does not end up being endlessly looked over.

Debt backlogs should be consistently tracked and monitored to make sure that tasks are being completed.

### 9. Automate testing

Test automation typically helps teams to uncover issues much more quickly and precisely compared to manual testing, which is largely inefficient.

For long-term projects that have a significant amount of technical debt, automated testing that can scan the code to find issues each time a module is updated can prove invaluable.

For instance, developers can use automated unit testing to make sure that each individual part of a system works as it should, and automated regression testing to make sure that the entire system hasn't been thrown into disarray by changing one small section of code.

### 10. Implement best practices in a project's early stages

By outlining best practices in the early stages of a project and encouraging team members to implement them as early as possible when they are still getting to grips with the processes, you can drastically increase your chances of success.

Developers should all have access to a document that outlines the coding standards and best practices that they should follow. This should be organized as soon as possible after a new project has begun, and all new team members should be given access to it as soon as possible.

If you started your project a while ago and it seems too late for that – you can still build a plan and work on gradually implementing it in each iteration.

### 11. Categorize and document technical debt

![technical debt documentation](/images/uploads/sigmund-cdmau_x9mxy-unsplash.jpg "technical debt documentation")

Categorizing and documenting technical debt increases transparency within the team. It also helps teams to understand the debt more clearly, which means that they can make more well-informed decisions about it.

Unfortunately, this documentation rarely exists. If it does exist, it is rarely ever updated by engineering teams.

To stay on top of the debt, teams should document it in a project tracking platform such as [Jira](https://www.atlassian.com/software/jira), and then tackle it during quieter periods when there is less time pressure to complete other tasks.

### 12. Keep a record of changes

Keeping a thorough record of changes and making it publicly available to the entire team means that problems can be solved more quickly. This is because developers will be able to trace the source of a problem much more efficiently.

It can take a while to create this habit within a development team, but the payoff is worth it.

### 13. Communicate about technical debt

Given that reducing technical debt is vital to the long-term success of a project, it is important that everyone understands what it means, and why it is important.

When communicating about technical debt with business stakeholders, you should begin the conversation with the aim of improving understanding between both parties. You should be able to back up any claims to make with data and anecdotal evidence, and you should already have a short list of key technical debt items that you have identified. You should also have a flexible plan that you can put forward to resolve these issues, and an idea of how long the plan will take to execute.

Throughout this process, you should be willing to share progressive reports as the technical debt is being paid off.

Finally, you should have a plan in place to ensure that technical debt causes less of a problem in the future.

### 14. Pay off the technical debt

Once the key decision-makers within the organization understand the concept of technical debt and are on board with paying it off, then it's time to begin reducing the amount of technical debt.

The overall goal here is to reduce the debt as much as possible, without compromising the ongoing progress.

For most organizations, the most effective way to pay off technical debt is to figure out what work needs to be done, and then divide it up into smaller, more achievable milestones. Then, managers can focus on gradually integrating these milestones into the team's normal workflow. This can help to gradually pay off the technical debt over time, without compromising their normal workflow or missing deadlines.

### 15. Minimize with Agile practices

Agile development relies on speed. When teams are encouraged to work quickly to meet deadlines, the quality of their code can slip. This can make it more likely that technical debt will accumulate.

However, adopting Agile practices can also help to reduce technical debt. Given that Agile is an iterative approach to software development, managers can help to reduce technical debt by ensuring that some time is allocated to paying off a manageable amount of technical debt is prioritized in each cycle.

If anyone finds something wrong with the system at any point during a sprint, they should also be encouraged to report it right away before it becomes a bigger problem.

### 16. Deliver a cost-benefit analysis

Creating and delivering a clear cost-benefit analysis means that organizations are better able to prioritize and plan the payment strategy.

For instance, it may be helpful to put a price tag on a problem to demonstrate how much the debt is affecting the problem, and to help others to understand why paying the debt off within a realistic timeframe is important.

This transparency can ensure that everyone has an understanding of the issues faced, and increases the likelihood of everyone being on board with the repayment plan.

### 17. Alter the organizational mindset

![organizational mindset](/images/uploads/sigmund-axapuirwhgk-unsplash.jpg "organizational mindset")

One of the most difficult – and yet, most effective – parts of reducing technical debt is altering the organizational mindset within your team. This won't happen overnight, and it will take consistent effort from everyone on the team – but the payoff is worth it.

To do this, managers should consistently ask themselves questions such as:

* Are teams thinking about what is the best long-term strategy, or are they using short-sighted approaches?
* Are teams completing projects simply to try and meet a deadline as quickly as possible, or are they considering how they – or other teams – could leverage this work for future projects?

By consistently deciding to balance out speed and quality instead of focusing on one at the expense of the other, organizations can slowly begin to reduce their technical debt – and reduce the chances of it building up to unmanageable levels again in the future.