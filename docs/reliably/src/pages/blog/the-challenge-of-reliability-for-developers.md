---
title: The challenge of reliability for developers
description: Companies are more dependent on uptime than ever before. And yet it
  still sucks, despite the shift to DevOps and the emergence of so much great
  new tech.
category: DevOps
author: Reliably
author_role: The Reliably Team
author_image: /images/uploads/reliably-r.png
date: 2021-03-22T14:13:56.460Z
featured_image:
  src: /images/uploads/blog-categories-devops-1200.jpg
  alt: challenge of reliability
excerpt: Companies are more dependent on uptime than ever before.
layout: ../../layouts/PostLayout.astro
thumbnail: /images/uploads/blog-devops-1200.jpg
---
Companies are more dependent on uptime than ever before. And yet it still sucks. I ask why this is the case in 2021, despite the shift to DevOps and the emergence of so much great new tech.

## TL;DRs

* DevOps is great, but reliability isn’t up to speed yet
* Dev teams need help to fix it
* We need a more proactive approach
* We need to focus on reliability from day one
* Overcoming the hurdles to automated reliability is key

Well, we’ve made it to 2021. I guess it’s safe to say it now: the world has *officially* and *successfully* shifted to DevOps. Great! Anyone who works in the industry (or anywhere near it) will know the myriad benefits that come with the territory. I’m not here to restate them for the umpteenth time.

Instead, this year I’m ready to reflect a little bit on where we are in the industry, and what impact the emergence of DevOps has had on the changing role of development teams. And if you know me at all, you’ve probably guessed it: I’m interested specifically in **reliability**.

For all the wonder of the modern DevOps team, one fact remains all too clear: outages are still happening too often, with the latest example being french cloud provider OVH only a few days ago. So, what’s going on?

## Development teams are over-worked

If you’re wondering why outages are happening, the simplest answer is probably the best: the team behind that system probably *doesn’t have the time* to make it more reliable.

It’s about time we acknowledged it: delivery teams are being worked to the bone. The growing complexity of modern systems (made possible, in part, by the emergence of DevOps culture) means that workload has increased considerably in recent years. This means dev teams are often spread pretty thin. And this, despite the fact that DevOps was supposed to make life easier, more streamlined, more efficient. Go figure.

I’ll say it because no one else will: devs need help.

And this isn’t just a *major cause* of reliability issues. It also goes some way to explaining why the problem hasn’t been fixed. There is a perception that dev teams need one less thing to do, rather than one more thing. Shunted down the pecking order, beneath the ‘shinier toys’ of speed and [security](https://reliably.com/blog/choosing-between-reliability-and-security/), reliability has lately developed an unfair reputation as a bit of an afterthought or late-stage add-on. Which makes it easy to write off. But now, too many firms are paying the price for that neglect.

## The reactive approach isn’t working

The outcome of an over-worked development team is obvious. With so much on their plates, it’s easy for teams to fall behind. And we all know what that means: firefighting. Now, problem solving may be at the heart of the developer’s mindset, but that doesn’t mean a day spent putting out fires is a day well spent.

I think back to one of the major SRE publications of last year – <a href="https://www.oreilly.com/library/view/chaos-engineering/9781492043850/" target="_blank" rel="noopener noreferer">Chaos Engineering: System Resiliency in Practice</a>. Casey Rosenthal and Nora Jones did a great job telling us all about the importance of learning from every outage. *Never let an outage go to waste* was the mantra – and a great one! But I’d now go a step further than that: we need to learn these lessons *earlier*. So, my mantra for 2021:

> Learning *from* an outage is good;<br />
> learning *before* an outage is even better.

In other words, the prevention can be better than the cure. In my experience, the most reliable systems are run by the most proactive devs – those who are constantly looking *forward* to pre-empt and avert their next outage. The best development teams are committed to finding problems **before they become problems**.

And so, the world of reliability needs a significant culture shift. We should be talking in positive terms, not negative. And we should be doing all we can to get ahead of the game. Because reactive reliability is a false economy.

## Let’s be proactive, but not at any cost

I know, I know – criticism is easy. If the problems with reliability are so plain for us all to see, why isn’t something being done? Well, it isn’t for want of trying.

Reliability is perhaps more important than ever before. The power of software today means we’re seeing more large companies dealing with unprecedented amounts of data, and putting huge amounts of pressure on uptime. *Companies do want their systems to be more reliable!* And the push towards a more proactive approach makes a lot of sense to everyone involved. The problem? It isn’t as simple as just asking dev teams to be more proactive.

Yes, a proactive approach is great – necessary, even – but doing things manually isn’t the answer. Why? Well, because – much like reactive firefighting – manual proactivity is a waste of everybody’s time. Time devs don’t have in the first place. Let me explain.

## The needle in the haystack

Look at it like this: a system with 96% or 97% uptime isn’t good enough for most successful companies. Statistically, this is a system that is *almost* perfect. But that isn’t good enough.

The upshot is that we’re looking for something that’s incredibly hard to find. Indeed, looking for errors in a system that is *almost* perfect is the developer’s equivalent of looking for a needle in a haystack. It’s time-consuming, and complex. It takes hours of menial, repetitive labour – very little of which bears any actual fruit.

Most successful companies today would agree that people are their most important asset, particularly in a DevOps environment, comprising highly-skilled individuals. Certainly, that’s always been the case for my teams. Simply put, I don’t want my devs wasting their time on repetitive, menial tasks. They should be engaging their brains, challenging themselves, and finding ways to innovate.

So, I know I’ve said this before but I really can’t stress this point enough: *devs need help!* To my mind, if there’s a solution to reliability’s blatant need for proactivity, it has to lie in automation.

## Why aren’t we there yet?

Of course, automating site reliability engineering is no cakewalk. And perhaps one of the biggest hurdles is the sensitivity of data.

Company data is often sensitive. So businesses are reluctant to involve a third party or to send any such information outside of their company’s perimeter.

To those of us in the world of DevOps, none of the above problems for reliability come as a surprise.
So, if we’re to build a new future for reliable systems, we need to give reliability the attention it deserves. We need to put reliability at the forefront of our approach to development. Because hope alone is not a strategy.