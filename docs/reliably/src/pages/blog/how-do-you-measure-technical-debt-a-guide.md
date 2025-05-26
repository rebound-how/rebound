---
title: How Do You Measure Technical Debt?
description: "Our ultimate guide on technical debt explores how you measure
  technical debt and the trade-offs software teams make to speed up development.
  "
category: Technical Debt
author: Kerem Gocen
author_role: Senior Software Engineer
author_image: /images/uploads/1626379469381.jpeg
date: 2022-04-29T08:06:01.342Z
featured_image:
  src: /images/uploads/peter-gombos-8y3e2m6apy4-unsplash.jpg
  alt: technical debt
excerpt: "Our ultimate guide on technical debt explores how you measure
  technical debt and the trade-offs software teams make to speed up development.
  "
layout: ../../layouts/PostLayout.astro
---
## What is technical debt?

Technical debt is one of the trade-offs today's software teams make to speed up development, which helps go-to-market time in return. That is mission-critical for most start-ups.

Instead of dwelling on implementation details, or trying to cover edge cases that may affect a small fraction of the end-users in an early development stage, agile teams prioritize early and continuous delivery. This approach aligns with the 'working software is the primary measure' principle of the [Agile Manifesto](https://www.agilealliance.org/agile101/12-principles-behind-the-agile-manifesto/).

Technical debt can be described as the residue of this fast-paced, deliver working software frequently mindset that is widely accepted among software teams.

### Why technical debt accrues?

The short answer is its part of the agile process. Not just as a side-effect of the software development lifecycle but also as deliberate decisions by the team, it's not uncommon to label a not-so-urgent task as tech debt and move it to the end of the backlog. This ensures the allocation of more resources to the mission-critical tasks and helps the team focus on the current objective where the standard [sprint cycle](https://www.atlassian.com/agile/scrum/sprints) duration is only two weeks.

Stakeholder expectations, limited resources including time, and the number of developers working on the project are some of the most obvious reasons why technical debt is produced.

Another factor could be poor alignment between IT and strategy, which is fueled by failure to measure the impact of IT initiatives on strategic imperatives and results in excess complexity or orphaned systems over time.

### What to measure?

![technical debt](/images/uploads/linkedin-sales-solutions-1a8yp_5msac-unsplash.jpg "technical debt")

While the definition of technical debt is abstracted behind each team's interpretation, this allows software teams the flexibility to gauge their debt metrics according to their needs and expectations. There are usually multiple correct answers to what should be measured as technical debt. Common ground would be that it's easier to identify the impact of technical debt.

[Reliability](https://reliably.com/blog/reliability-testing-for-sre/) metrics such as the uptime of the system, and resource consumption (CPU, memory, etc.) could be acknowledged as tech debt, and tackling them might help proactively brace for infrastructure issues. If your team is using an agile tool such as Jira, one obvious metric would be the number of tickets labeled as tech-debt. This would require an initial effort to identify and log technical debt regularly. Refactoring needs might also surface on changing product direction or simply because the technology used is getting old.

### What is considered technical debt?

Apart from the obvious software bugs and dependency issues, if your product strategy is to scale to millions of users, the initial stage infrastructure may be lacking the appropriate design. You might have prototyped on a small scale or cheaper solutions and now maybe it's not keeping up with the current amount of demand.

Test automation or even the basic tests may be overlooked. Documentation is another common victim of the early stage, fast-paced software development. Deprecated dependencies can expose unexpected attack surfaces or vulnerability issues.

#### Types of technical debt

* **Design:** early-stage design might be low quality such that its hard for the team to maintain it.
* **Automation:** lacking a smooth CI/CD pipeline would impact delivery to production and bug fixing time.
* **Monitoring:** not knowing basic metrics early on, or not having the confidence of knowing how reliable your system is can create ambiguity between product and technical direction.
* **Testing:** having meaningful integration test coverage is another overlooked source of confidence to ensure product expectations are met, [the earlier on the better](https://docs.microsoft.com/en-us/devops/develop/shift-left-make-testing-fast-reliable)
* Security: old versions of the tech stack or external dependencies no longer maintained are potential security risks, there might also be known issues.
* **Deprecation:** code that is no longer used or owned creates redundant complexity
* **Documentation:** not having useful and easy to read documentation around critical parts of the system makes it difficult to onboard new developers or retain the current knowledge.

## How to measure technical debt

While there is no single standard to measure technical debt, there are some commonly encountered opinions. One of them is the [technical debt ratio](https://medium.com/the-andela-way/what-technical-debt-is-and-how-its-measured-ff41603005e3) (TDR).

TDR is a ratio of the cost to fix a software system (remediation cost) to the cost of developing it (development cost).

**Here is the equation for TDR:**

***(Remediation Cost ÷ Development Cost) × 100 = TDR***

As the name implies, this metric was designed specifically for calculating the overall future cost of technical debt. This can be in terms of time, or some other resource. A high TDR value indicates poor code quality or a high cost of technical debt. The goal then for the team would be to keep this rating low or at least under an agreed threshold.

Even without using a specific formula, it is possible to measure the impact of technical debt on the overall development.

The obvious way is to keep track of technical debt tickets by labeling them in the backlog and monitoring the number of resources spent on those versus new product features. How many development hours your team is spending on those? Do you have development time dedicated to technical debt issues? How much time is spent on technical debt tickets between two release cycles?

Recording and observing these metrics could provide meaningful numbers. Even if they don't necessarily make sense initially, comparing them between each other over multiple sprints could indicate if the team is moving towards the designated direction in tackling the technical debt.

## Paying down your technical debt

![paying down technical debt](/images/uploads/ussama-azam-26h317_umym-unsplash.jpg "paying down technical debt")

It is uncommon to avoid technical debt tickets even for greenfield projects. Now that you are aware of the costs and impact of this debt, when do you pay it back?

### Impact on team velocity

By measuring the sprint cycle velocity versus estimation, lowered velocity may indicate an impact on delivery. The underlying root cause could be time spent on fixing bugs or keeping an old system running putting out fires left and right caused by pending tech debt.

### Impact on product quality

You may notice more incidents are spotted during Q&amp;A, as the codebase becomes more fragile over time. It may be getting more and more complicated to add small features and push them into production. This could be a good time to assess technical debt and a recovery strategy by adopting it into the development process or even prioritizing it higher than adding those new features temporarily for a saturated product.

Some teams prefer to keep a separate backlog for technical debt, while for others technical debt tickets are prioritized within the current backlog. As this is partially a product decision, involving the stakeholders in the process and dedicating a fixed amount of the sprint for technical debt is a healthy practice. While this may not be easy to pull off each sprint, some teams even dedicate entire sprint cycles for the tech debt during less demanding periods.

Incorporating tech debt tickets of 10-20% in each sprint could help keep the debt low and increase team morale who are working on an easy to maintain and highly reliable system.

This approach of course requires continuous monitoring of the technical debt and its causes. When acknowledged by the team what the current pending technical debt issues are, their impact on the system and their priority can be monitored. Tools such as [Reliably](https://reliably.com/) would help your team stay afloat by creating objectives towards a healthy reliability score and even set alarms to help tackle those objectives. It integrates seamlessly with your currently used tools so getting an alert message on slack upon reliability issues would make it harder to avoid potential unpaid technical debt impact.

## Technical Debt vs Business Value

The cost of ignoring tech debt on the business value is huge. According to [Gartner's research](https://www.gartner.com/en/publications/how-to-assess-infrastructure-technical-debt-to-prioritize-legacy-modernization-investments), Infrastructure &amp; Operations leaders who actively manage and reduce technical debt will achieve at least 50% faster service delivery times to the business. For team leaders and managers, it's no surprise that a considerable amount of time and resources goes into tech debt, whether it's for keeping legacy systems up and running or refactoring the operation.

Technical debt directly affects the business value and ignoring it long enough might require refactoring of entire systems. Unhappy developers drowned under huge technical debt will quickly drain the business value of the product either by causing eventual operational damage via security vulnerabilities or building features with low reliability.

## Useful tools to manage technical debt

Here are some useful tools to manage technical debt:

* **JIRA Software:** The beloved standard for issue tracking which allows teams to practice agile methods.
* **Stepsize:** This is an issue tracker that integrates with your favorite code editor (see: [VSCode extension](https://marketplace.visualstudio.com/items?itemName=Stepsize.stepsize)) and issue tracking software including JIRA, allowing you to create issues within the editor and they offer a [tech debt calculator tool](https://www.stepsize.com/tech-debt-calculator).
* **Velocity:** Code Climate's[Velocity](https://codeclimate.com/velocity/) claims 30% increased software shipping time by pulling data from tools such as Jira and turning them into actionable insights for your engineering teams.