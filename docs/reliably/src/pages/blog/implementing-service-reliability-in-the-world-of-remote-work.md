---
title: Implementing Service Reliability In The World Of Remote Teams
description: >
  Implementing service reliability in the world of remote teams means that teams
  face new challenges, so what does implementing service reliability look like?
category: Reliability
author: Steve Wade
author_role: Kubernetes Consultant
author_image: /images/uploads/1630758024864.jpeg
date: 2022-03-23T10:14:52.441Z
featured_image:
  src: /images/uploads/pexels-elina-fairytale-4008702.jpg
  alt: implementing service reliability
excerpt: Implementing service reliability in the world of remote teams means
  that teams face new challenges, so what does implementing service reliability
  look like?
layout: ../../layouts/PostLayout.astro
thumbnail: /images/uploads/charlesdeluvio-bxqomf5tvdk-unsplash.jpg
---
In this new era that we are moving into, what does successful reliability look like for modern teams and what are the requirements that will enable us to bring better reliability to our applications and system?

With new ways of working, we explore how organizations should implement better service reliability and the different [challenges](https://reliably.com/blog/the-challenge-of-reliability-for-developers/) teams are facing.

## What Is Reliability?

Reliability is not just about the availability of services, but how important those services are to users. Different business functions will think about reliability differently and how it impacts user satisfaction.

Decisions made by marketing and sales teams, for example, don't directly impact the user experience for a product, however, they do impact the user's perception of how good the product is which can change where the satisfactory point is.

On the other hand, lowering expectations will also lower interest in your product. Even revenue teams have to align their goals with making sure that they don't sacrifice reliability or a customer's perception of reliability.

Finding the connection point through reliability and user satisfaction across all of the functions of a business is critical to driving decisions. Whether those decisions are bottom-up or top-down, it allows you to understand what the impact of the decision is and the goals that it's going to have with every team.

### Who Needs To Care About Reliability?

We often talk about reliability from the context of software engineering but when organizations face outages it becomes immediately obvious that the reliability of an online service or application is something that impacts the entire business - with significant costs.

Let's compare two different incidents.

Incident one causes lag briefly for a service that everyone, including your most valuable customer base, uses.

Incident two causes a total outage for an hour but just for a service with a very small percentage of users, on a low-tier subscription and very rarely access this piece of software.

Which one causes more damage to a user's perception of reliability?

Being able to answer this question is key to having teams know and think about reliability. Building a framework to answer these important questions is fundamental to the entire business. Engineers alone shouldn't be the ones thinking and planning for reliability. Reliability should inform the decisions that every team cultivates.

## The Reliability Spectrum

![reliability spectrum](/images/uploads/reliability-spectrum.png "Reliability Spectrum")

Thinking about reliability across an entire organization and not just individual engineering teams sits you in the strategic and visionary phases of what Google calls the [reliability spectrum](https://cloud.google.com/blog/products/devops-sre/the-five-phases-of-organizational-reliability).

Reliability isn't about checking off certain milestones. It's about working as a team and looking at the benefits as a whole. You must think about how you can implement objectives across your entire organization - not just your codebase.

### Teams And Perspectives Of Reliability

Different teams within an organization can have very different perspectives and priorities.

Let's take a look at 3 different teams and their goals:

* A product team hoping to release an important new feature as soon as possible
* An operations team looking to reconfigure the CI/CD process
* A customer success team trying to drive a development roadmap in response to some customer feedback that they've had.

These goals all conflict with each other and each team's perspective and desire to complete their project as a priority is completely valid. So how do we as an organization come up with the answer to which one comes first?

All three teams have valid claims that their priority is essential to user happiness but these users are different. One is focused on the current customer base, one is focused on developer teams and the other is focused on prospective customers.

We can't simply compare the number of users affected to how important or how reliable this new feature is going to be. We need a common way of making decisions.

Questions you might ask to determine reliability service priorities:

* What are the types of users that are likely to be affected?
* What is the frequency of the affected user experience?
* What's the importance of the aspect of the user feature?
* How important is it to the user?
* What is the business importance of making sure that the affected user is constantly satisfied?

The ultimate goal is to have a metric that encompasses how much user satisfaction could change based on a decision that you are about to make. This metric would apply not just only to code changes but to decisions by any team, at any level of the organization.

By having a decision-making process, you can create a universal language that can be used to discuss user satisfaction levels and therefore business impacts.

Once you've established this definition of reliability that everybody in the organization understands, organizations will be in a much better position to prioritize each project and each team's desires based on the impact and overarching goals.

This might not be just as simple as seeing which ones make the biggest positive impact or the ones that have the potential lowest negative impact - you need to have a way of baselining these.

### How Do You Improve Service Reliability?

![culture of resiliency](/images/uploads/surface-8hplpr3hebu-unsplash.jpg "Culture of resiliency")

Improving the reliability of a service that users are happy with may not be appreciated or even noticed by the majority of your user base, so trying to indefinitely improve reliability has rapidly mounting costs and potentially diminishing returns.

What's important is the ability to be able to maintain reliability at a level that doesn't cause user pain or friction. If you are causing user pain or user friction then you are making the product be deemed less reliable and therefore giving the customer or user a worse customer experience.

### 1. Service Level Objectives

Finding a way to obtain information about the changes that you are making and what impacts they have on your customers is critical.

It's important not just to agree on what reliability looks like from different user experiences but also to determine the point at which each user experience becomes too unreliable. This is why service level objectives are so important.

How each user experience is being compared to that agreed-upon objective determines how you should prioritize changes across the business or your team.

Having a framework and a language that you can talk about throughout the organization can provide you with a view of what reliability means for your customers. This is critical to quantifying and weighing up decisions at all the different levels of your organization.

It also gives you the ability to plan investment payback meaning anything that you do at an organization has some kind of investment behind it.

### 2. Technical Debt

Reworking the term 'technical debt' is a critical factor in implementing successful reliability. The word technical debt itself seems to bring fear to everybody.

Teams often view tackling technical debt as a major project that will impede all other features that are being developed.

In a healthy system, technical debt management should be a routine cleanse, where you should be sweeping up the technical debt behind you. You should not be leaving a mountain of technical debt that will never get dealt with.

The concept of debt is a total misdemeanor. If you think of it as debt, you'll think of it as the enemy of velocity or the enemy of innovation. In reality, it brings stability which will therefore be able to support innovation and velocity.

By taking the fear out of technical debt, companies can use it as an opportunity to support innovation while still optimizing and guaranteeing a reliable foundation.

### 3. Building A Culture Of Resiliency

It is important to make sure that all of our teams are safe psychologically and able to learn from their mistakes.

The next outage or major incident is going to happen. It's right around the corner and that's okay. That's the mindset that you've got to be in. Failure is going to occur, you just need to be able to deal with it.

New ways of working (WOW) have accelerated the urgency for digitalization and this creates a tremendous amount of pressure and stress on the people and teams who support digital services. This stress can lead to the blame game. 

Blame should not be directed at a person, it should be directed at the system. For example, why couldn't we access the data? Why was there no metric? Why was there no alert? Why was there no run book? As opposed to how did you not realize that we shipped this feature that caused this problem?

This concept of visibility will empower our safety with observability and enable teams to gain deep insight into these distributed systems, and better understand gaps in tools and processes; helping you move away from the blame game.



### 4. Bringing Observability To The Forefront

Bringing observability to the forefront empowers you to see into issues and learn from them in depth. Without an observability strategy, every team will be in the dark and have little idea what's going on, when it's going on or what's causing the problem.

To prevent this, it's important to encourage your organizations to focus on observability early and revise it often. Many tools and vendors provide you with the ability to bring [observability to the forefront](https://reliably.com/).

You need to allow engineers the ability to see the data, whether that be metrics, logs, or traces, and be able to get to the root cause of the issue.

To begin with, implementing observability you should encourage your teams to identify critical user journeys through the system, break them down and prioritize them into the top three categories of user flows. Teams must recognize the most crucial flows and implement observability based on them.

The more insight you have into those critical flows the more you can begin to understand how the user is using the system.

For teams looking for a place to start, why not try going and talking to the testing team? The testing team is likely to have a set of user flows that they've already got documented.

### 5. Continuous Documentation And Communication

As ways of working have changed (remote, hybrid, etc.), there is a need to support seamless collaboration through processes and tooling.

You need to communicate, interact, document, and make information available to everyone. This is even more important than it was two or three years ago and this concept of [asynchronous communication](https://resources.owllabs.com/blog/asynchronous-communication) is critical to success.

We now have people working and spanning different time zones, so documentation serves as a much-needed way of being able to gain understanding, without having to have a video conference call. It's more essential than ever to start writing things down and making sure that teams are aligned.

You can no longer rely on the person you'd call into an incident huddle because they know the most about this - that person may not be available at the time that incident happens. We can't rely on people being there anymore.

### The Cost Of Service Reliability

If you have ever hired new staff, implemented a new tool, or implemented new policies and procedures, they all require investment and each one of them has initial costs. You should ask yourself will the experience ultimately create value that is more valuable to the user than the cost that it takes to implement it?

We can't think about changes just in a narrow financial focus because it's hard to assign a pound or dollar value to many of the returns that you'll get from implementing reliability.

Potential challenges caused by this kind of investment could include:

* Issues caused by teams getting up to speed with a new policy
* Re-prioritizing other projects to implement a new tool
* Loss of resources that could have been spent working on user experience

An investment can look like it's going to have a big payoff but for a very small cost. If that small cost pushes the user experience over the edge and causes user pain then is it worth it is it worth implementing at all?

### Reliability In The New World Of Remote Work

![service reliability ](/images/uploads/hack-capital-uv5_bsypfum-unsplash.jpg "Service Reliability ")

Things have changed in the last couple of years. We're not all in the same office as a prime example. Regardless, we need to align with what will make the post-pandemic future more of a success for everybody.

Learning to thrive in this new remote working environment is going to be an act of resilience for all of us.

We must adapt and learn how to make our systems and people more capable of understanding all of the challenges along the way. You can do this by adopting observability early and revising it, focusing on documentation communication, and most importantly focusing on the people. In doing so we can enter into this new era stronger than we've ever been before.

Remember, reliability is a team sport.

It's so fundamental to business success that it can't just be the focus and responsibility of reliability of engineers. Instead, every team needs to align on what reliability means and how they can prioritize work and features based on it.