# Why lueur?

We are building lueur because we have met unexpected production
issues which forced us to scramble, patch code at the last minute, and hope
that live fixes will hold up, all under pressure.

lueur aims to change that story. It brings reliability testing right
into your daily development routine, so you’re not left guessing how your code
will behave under tough network conditions.

Instead of waiting until the final stretch—when the impacts are higher and fixes
cost more—lueur invites you to explore resilience as you go. It’s built to help
you identify weak spots early, reducing last-minute surprises and giving you
more time to craft thoughtful solutions.

**What’s in it for you?** Less stress. More confidence. And the freedom to
improve your application’s reliability before it ever reaches your customers.

## Features That Work With You

### Protocol Support

lueur slips into your workflow without demanding a big overhaul. Just point your
traffic through its proxy and test your application as normal:

- Forward and tunnel proxy modes
- HTTP and HTTPS
- HTTP/1.1 and HTTP/2
- Scenarii automation

### Real-World Faults at Your Fingertips

lueur simulates the kinds of hiccups you’ve seen (or worried about) in
production—right on your own machine:

- Inject HTTP errors to see if your app recovers gracefully.
- Add latency and jitter to gauge performance under slow networks.
- Test packet loss and bandwidth limits to discover scaling limits.
- Introduce random “bad gateway” responses and ensure robust fallback paths.

### Tailored for Your Needs

If your scenario demands more than the built-in faults, lueur’s gRPC interface
lets you customize your own conditions. Mold the tool to fit your environment,
not the other way around.

### Lightweight and Fast

lueur wants to help you, not slow you down. It’s a single binary that starts up
quickly and has minimal overhead. That means you can integrate it into your
daily workflow, tests, and continuous integration pipelines without feeling
weighed down.

Under the hood, lueur uses [Rust](https://www.rust-lang.org/) to ensure speed,
safety, and resilience—just like what you strive for in your own code.

## The Real-World Costs of Slowness and Unreliability

It’s not just about feeling “fast.” Slow or unreliable responses can have real
business and user engagement costs—even during early development phases. By
helping you pinpoint potential performance and reliability issues early, lueur
empowers you to avoid these pitfalls:

<div class="annotate" markdown>
- **Reduced Revenue:** Amazon famously found that every 100ms increase in page
  load time cost them about 1% in sales (1). Sluggish endpoints aren’t just an
  inconvenience; they hit the bottom line.

- **Higher Bounce Rates:** According to Google, over half of mobile users abandon
  a site if it takes longer than three seconds to load (2). Users today expect speed
  and smoothness from the start.
  
- **Decreased Engagement and Trust:** Akamai’s research highlights that a two-second
  delay in web page load time can cause bounce rates to skyrocket (3). Slow, error-prone
  services send a message of unreliability to your users—something that’s hard to
  rebuild once trust is lost.
</div>

1. Greg Linden’s Slides from Amazon on the cost of latency: *Marissa Mayer at Web 2.0*  
2. Google, *The Need for Mobile Speed: How Mobile Page Speed Impacts Customer Engagement* (2018)  
3. Akamai, *Akamai Online Retail Performance Report* (2017)

**What does this mean for you?** By injecting faults and testing
resiliency scenarios early with lueur, you’re investing in a smoother launch,
happier users, healthier on-calls and a product that stands strong under
real-world conditions. Instead of postponing issues discovery late—when they’re
costlier and more stressful to fix—you’ll tackle them when the code is fresh and
flexible.

## Rethinking How We Build Software

Traditionally, developers focus on crafting features and fixing bugs, leaving
resilience concerns to be uncovered later by SREs, performance engineers, or end
users in production. lueur challenges this status quo by inviting developers to
think differently—early, locally, and without guesswork—about the resilience of
their applications. This isn’t just a shift in tools; it’s a shift in
philosophy.

We want to help you move beyond a mindset where reliability is an afterthought.
Instead, imagine it as a first-class concern in your day-to-day coding routine,
as natural as running unit tests or linting your code. By experimenting with
realistic fault conditions before your application ever leaves your workstation,
you’re not just preventing outages—you’re nurturing a culture of forward-thinking
and robust engineering.

### New Indicators of Reliability

How can we talk about reliability in a way that resonates with developers? We
propose a set of new indicators that highlight different angles of resilience:

- **Latency Tolerance**: How gracefully does your application handle slow
  network responses? Identifying how long it can wait before timing out or
  degrading service helps you set meaningful SLOs (Service Level Objectives).

- **Failure Surface Awareness**: By injecting HTTP errors, packet loss, or
  bandwidth constraints, you gain clarity on where your code is most fragile.
  Measuring how many parts of your service break under each condition provides
  a new perspective on your “failure surface.”

- **Retry Overhead**: Discover the hidden costs of your application’s recovery
  strategies. Do you retry too aggressively, wasting resources and time?
  Tracking how your code responds to fault scenarios reveals whether your
  fallback paths are efficient or need fine-tuning.

- **Resilience Debt**: Like technical debt, resilience debt accumulates when you
  postpone reliability fixes. Early detection and quantification of this debt
  helps prioritize improvements before they become expensive production
  firefights.

### A Daily Practice, Not a Crisis Response

Think of lueur as a steady practice in your development cadence. Just as TDD
(Test-Driven Development) encourages writing tests first, we envision a
Reliability-First Development approach: write a feature, inject a fault, and see
how it holds up. Adjust, refine, and proceed with a clearer understanding of how
your software behaves under stress.

This shift in mindset encourages you to proactively craft solutions that don’t
just work in ideal conditions—they thrive in real-world, sometimes messy,
environments. Over time, this practice becomes muscle memory, and resilience
testing transforms from an occasional chore into an integral part of building
software that users trust.

lueur isn’t just another tool on your belt; it’s a new way of thinking about and
measuring reliability. We’re here to help you see beyond happy paths, to embrace
uncertainty early, and to raise the bar on what “done” really means.


---

lueur is about making your life easier when it comes to building reliable
software. It puts you in the driver’s seat, letting you explore and solidify the
resilience of your applications before those big, stressful moments can occur.

---
