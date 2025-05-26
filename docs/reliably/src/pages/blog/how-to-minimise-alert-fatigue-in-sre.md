---
title: How To Minimise Alert Fatigue In SRE
description: Wondering how to minimise alert fatigue? Learn what it is, how it
  affects engineering teams, and how to minimise it in SRE.
seo:
  title: How To Minimise Alert Fatigue In SRE
  description: Wondering how to minimise alert fatigue? Learn what it is, how it
    affects engineering teams, and how to minimise it in SRE.
category: Alert Fatigue
author: Aimee Pearcy
author_role: Technical Writer
author_image: /images/uploads/aimee-profile-photo.jpeg
date: 2022-07-14T16:56:28.514Z
featured_image:
  src: /images/uploads/stephen-phillips-hostreviews-co-uk-ae0ix-blcjc-unsplash.jpg
  alt: alert fatigue
excerpt: Wondering how to minimise alert fatigue? Learn what it is, how it
  affects engineering teams, and how to minimise it in SRE.
layout: ../../layouts/PostLayout.astro
---
## What is Alert Fatigue?

Alert fatigue occurs when people become desensitized to the overwhelming number of alerts they receive and are expected to respond to.

Even though these alerts are typically easy to respond to, it is the sheer number of them that ultimately causes people to feel fatigued. The higher the number of alerts, the more likely it is that employees are likely to begin to ignore and potentially miss an important alert leading to bigger consequences.

Alert fatigue is a bigger problem than many people realize.

According to a [2022 survey](https://orca.security/resources/blog/2022-cloud-cyber-security-alert-fatigue-report/#:~:text=Alert%20Fatigue%20is%20Causing%20Burnout%20and%20Missed%20Critical%20Alerts&amp;text=Alert%20fatigue%20causes%20turnover%20and,internal%20friction%20in%20their%20organization.) by Orca Security that involved over 800 IT security professionals in five countries, 62% of respondents say that alert fatigue has contributed to turnover, and 60% of respondents said that alert fatigue has created internal friction in their organization.

### Common Sources of Alert Fatigue for SRE and DevOps Teams

DevOps teams and on-call site reliability engineers (SREs) are particularly prone to alert fatigue. Some of the main sources of alert fatigue in SRE include:

- **Duplicate alerts** that are typically a result of a redundant monitoring configuration. The first notification is enough to alert you of the issue, but the barrage of alerts that follow to remind you of the issue each time you open an application can quickly cause you to become irritated.

- **Low-priority alerts** that need to be addressed, but have been pushed further down in the queue in order to address higher priority alerts.

- **Irrelevant alerts** that are being handled by other teams and don't require your attention, but are not invasive enough for you to bother turning them off.

- **Flapping alerts** that change state regularly, resulting in an influx of problem and recovery notifications. This is typically a sign of configuration problems, and they can become a huge distraction when teams are trying to problem-solve.

### The Psychological Impact of Alert Fatigue

The more alerts you receive, the more likely you are to tolerate, normalize, and ultimately ignore them.

This is largely due to a psychological process known as 'habituation', which is designed to help us to tune out non-essential stimulation and focus on more important things that require our attention.

If you've ever tried to work with music playing in the background, you might notice that although it might be distracting at first, you eventually manage to tune out the noise and devote your focus to your work. This is how alert fatigue works, too – except, it can have much more significant consequences.

### The Risks of Alert Fatigue

![minimise alert fatigue](/images/uploads/hao-wang-pvq6yhmdptk-unsplash.jpg "minimise alert fatigue")


Alert fatigue can cause many problems for SRE teams. Some of the most common issues include:

#### Ignored alerts

One of the greatest risks of alert fatigue caused by a system that doesn't differentiate between minor and serious alerts is that employees can ultimately learn to tune out all alerts.

This can lead to a significant increase in incidents, which can decrease an organization's revenue, increase unexpected costs, and ultimately negatively impact its brand reputation that may have taken years to build.

#### Employee burnout

Given the events of the past couple of years, employee burnout has become a global concern. [A 2021 survey](https://www.apa.org/pubs/reports/work-well-being/compounding-pressure-2021) by the American Psychological Association (APA) involving 1,501 U.S. adult workers revealed that 79% of employees had experienced work-related stress in the month before the survey

Feeling like they constantly have to be on-call and available to respond to alerts – whether or not they are significant – can reduce employees' job satisfaction and increase feelings of burnout. This ultimately leads to a higher turnover rate for organizations.

#### Slower response times

Even if employees don't miss the alerts or decide to permanently ignore them, an increased number of alerts will typically lead to slower response times.

If you receive ten alerts every hour, there's no way you can drop everything you're doing and attend every single one of them.

## How to Minimize Alert Fatigue

While it's difficult to prevent alert fatigue altogether, there are a number of steps you can take within your organization to minimize it. Some of the key ways to minimize alert fatigue include:

#### Focus on creating specific, actionable alerts

Specific, actionable alerts that employees know exactly how to respond to require significantly less focus and attention than vague alerts with no clear outcome. For each alert, you might consider including an actionable checklist that matches the alert and provides the user with guidance on how to deal with it.

#### Reduce redundant alert reminders

A [2017 study](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5387195/) found that for every reminder of the same alert, the users' attention decreased by 30%. Reducing the number of redundant alert reminders that are sent out to users can help to maintain users' attention.

#### Focus on continuously reviewing and managing alerts

One of the key ways to reduce alert fatigue in SRE is to prioritize continuously reviewing and managing the alerts that are sent out to your users. If alerts are getting missed or users have learned to tune out the design of your alerts, find out why – and then take steps to resolve this.

## The Benefits of Minimizing Alert Fatigue

Some of the key benefits of minimizing alert fatigue include:

- **Reducing chances of employee burnout** by making sure they're not constantly interrupted by pointless alerts. This in turn can help to make sure your employees are more focused, while also increasing employee retention rates.

- **Increasing the chances of employees being able to respond to important alerts** by reducing the number of false alarms.

- **Increasing employee productivity** by reducing the level of context switching that they are required to do and allowing them to focus on the task at hand.

- **Reducing the chances of important alerts being missed** by focusing on the most important alerts that are actionable and taking the focus away from redundant alerts.

## Alert Fatigue and SRE

![alert fatigue](/images/uploads/matthew-henry-2ts5hna67k8-unsplash.jpg "alert fatigue")

SRE is an exciting, but ultimately stressful job role. As a result, it is vital to reduce this stress where possible.

Reducing the number of alerts that SREs are required to deal with on a daily basis can significantly decrease alert fatigue. This can increase employee productivity and reduce the turnover rate within your organization.

### Reducing Ops and On-Call Anxiety

If you expect your team to constantly be working in high-alert mode, they will inevitably burn out.

To [improve team health](https://reliably.com/blog/improving-team-health-with-reliably/) and reduce on-call anxiety, you should focus on spreading the workload out across the entire team so that everyone takes a turn carrying the pager.

Finally, you should make sure that you consistently review your on-call schedule and communicate with your employees to make sure they are not overburdened.






