# My Technical Journey Through <span class="f">fault</span>

## Where it all started

I've been coding for a rather long time but I still consider I learn everytime
I add, change or delete a new line of code.

Software development is a flow.

### My past paved my way here

In my early career days, I had an opportunity to work in a different role
altogether, as a performance testing engineer. I had a blast and it taught me to
look at software from three different perspectives.

First, I realized software was part of a bigger ecosystem. As developers, you
wrote, at the time anyway, generally a fairly large standalone program, maybe
an API. From that angle, where the software was used could be so far away
that you didn't realise you shared time, resources and capacity with others.

This led me to appreciate I should start paying more attention at the end to
end life of the system.

This experience finally taught me to not ignore nor fear stakeholders. I was
still young and not closely to working this way. What an awesome learning
experience that was.

### Adopting a system view

Anyway, what does this have to do with <span class="f">fault</span>? Well,
as a performance engineer, I looked at the system first, before its individual
components. I was trying to answer the question "can we sustain the objectives
we've set ourselves?".

Over the years, these types of questions remained close to my approach of
writing software. There's a saying in our industry that we should
avoid premature optimisation. For the most part, I agree with this but it
doesn't mean we shouldn't pay attention to the dimensions by which our
software may impact other parts of the system, or more directly our users.

### Complexity is everywhere, so is uncertainty

When microservices bubbled up as a new architecture pattern in the mid-2010s,
what I found interesting from that discussion is that it showed that 
complexity existed within the large components we were building. Sure, we
introduced a new set of complexity, with network involved, but
we also revealed what essentially hidden away, namely dependencies. Russ Miles
explored this very neatly in its
[Antifragile Software book](https://leanpub.com/antifragilesoftware).

While microservices aren't as popular these days, the breaking down of large
components into smaller pieces is very much core to how we ship applications
these days. Which means, our need to consider the whole, not just the part
is critical to build, deliver and operate successful applications.

This is where <span class="f">fault</span> comes in. Reliable applications,
resilient teams & organizations, these properties are not static, they
emerge from the system and evolve with time.

The core idea behind <span class="f">fault</span> is to help you
practice for these properties to emerge.

### A great DX starts with an easy install

I'm a coder at heart. It's like colouring a mandala. My pen of choice is
Python. What a fantastic programming language that is.

Over the years I was lucky to try a variety of other languages: C, perl, C#,
erlang, TypeScript (I'll keep my limited use of Java 1.2 under the radar thank
you).

Python is the one language I always come to because it's so simple and
expressive. However, the language's nature has made distributing CLI programs
more painful than I've liked.

When I chose Python for the [Chaos Toolkit](https://chaostoolkit.org/) beck in
2017, I did it because I wanted to rapidly prototype and get to a working
product. But I was aware I was making its users pay the price of more
involved deployment. As of 2025, the Python ecosystem has greatly improved and
the work done by the [Pypa](https://www.pypa.io/en/latest/) working group or
companies such as [Astral](https://astral.sh/) are finally giving me hope we can
reach a point where this isn't an issue anymore.

When I started with <span class="f">fault</span>, this choice faced me again.
I made the decision I wanted to use this opportunity to learn rust. A language
that has attracted me for years. By moving to rust, I made the issue mine
as a packager and I removed the burden away from <span class="f">fault</span>'s
users.

## Coding is about figuring out your next move

### Oh boy, Python to rust is quite the jump

#### What's your type?

When you come from a dynamical language, even a strongly typed such as Python,
landing on a statically language which takes its typing system very seriously.

Python has typing annotations, they have been evolving quite a lot since their
early days and I use them whenever I write Python code these days.

However, they are forgiving by nature. Enforcing them will depend on the
tool used to verify them.

rust is much stricter and will now let you slip through any shenanigans. This
is not Haskell level yet but quite the leap when coming from Python.

I have to say, I'm still very much learning my ways around the typing system.
On Python side because it keeps getting more powerful, on the rust side, because
it's already so rich and capable.

#### The subtle art of memory management

The life of things in Python and rust differ quite a bit. When you arrive
in rust-land, you need to familiar yourself with ownership of data.
I can't say I ever had to think too much about this when writing Python
code. In rust, this isn't optional. You make that decision all the time.

This slowed me down a lot at first but we'll come back to this later.

In rust, you make a lot of decisions whereas in Python, enough magic occurs
for you to rely on the underlying VM to figure it out.

Both are respectable and I enjoy working with both mindset. This works fine
because I would say I don't use either languages for the same purpose.

#### Oh dear `Result`

When it comes to function's output, rust is loose in what you can return. But,
the typing system ensures consistency and strictness. You get the best of both
worlds. But, as Neo said "the problem is choice". Do you return the raw value?
An `Option`? A `Result`?

As I'll note later, this question of choice is a recurring debate I have
with rust.

### Learning about rust basics

There are plenty of ways to learn how to program in a new language. Some folks
will follow books, others will use online courses, now you may even use AI
to train you. What works for me is to have something to code about. I learn code
as I write code but I need a driver, a project of interest.

<span class="f">fault</span> has been that project.

The basics start with setting up a project structure. With rust this
began with [cargo](https://doc.rust-lang.org/cargo/guide/).

From there, it took me a bit of time to get in a cruise speed with working
with rust project and environments. I would say, I'm at the 
same speed as I was with Python yet. However, I've grown quite happier today
with my rust routines.

From there, I relied on a couple of books.

* [Programming rust](https://www.oreilly.com/library/view/programming-rust-2nd/9781492052586/). What an amazing book. I keep coming back to it on a daily basis.
* [Command-Line Rust](https://www.oreilly.com/library/view/command-line-rust/9781098109424/). A smart approach of learning the language, however I found it challenging to use it once I got going with my own project.
* [Implementing Service Level Objectives](https://www.oreilly.com/library/view/implementing-service-level/9781492076803/). I knew early on I wanted to tie to SLO and this book is a great resource.
* [Dans le cerveau du gamer](https://www.dunod.com/sciences-techniques/dans-cerveau-du-gamer-neurosciences-et-ux-dans-conception-jeux-video). A French book talking about applying neuroscience to help building engaging and ethical video games. Many of its chapters were essential to me in exploring ways to make <span class="f">fault</span> intuitive and expressive.

Next, I spent a lot time reading other projects code. I also asked a variety
of AI models for questions I struggled googling for. I thought OpenAI models
were the most useful to me but I also quickly learnt how to keep a strict
critical thinking approach as ChatGPT tends to be overly verbose.

Finally, let's face it, trial and error was my life for a long time. The rust
compiler and rust analyzer were essential to progress.

### Traits and fun

Why are interfaces (or say
[abstract classes](https://docs.python.org/3/glossary.html#term-abstract-base-class)
in Python) so important to a software like <span class="f">fault</span>?

When I was a student, we were taught [OOP](https://en.wikipedia.org/wiki/Object-oriented_programming)
using languages such as Java or C++. This left a bitter taste with me because
I thought this was so heavy and made my programming feel complicated almost
over the top.

At the time of early Python 2.x, this kind of design wasn't cleanly fleshed out.
But because I was thinking in terms of state rather than data, I heavily
relied on class-based design. One of the first language I was taught was
scheme so I knew about the functional strategy, but it's not only until around
2008 when I worked with erlang, that I came back to appreciate it. From there,
I gradually left the the object approach behind me and only used when
it made sense.

Thus, in 2017 I approached Chaos Toolkit with a functional approach, even
though Python is a pure functional language, I looked at the problem before
me with the idea I was merely manipulating data.

When I started working on <span class="f">fault</span>, I therefore considered
the problem, once again, as a functional one. The data I manipulate is merely
a stream of bytes.

I initially stayed away from `traits` because I feared I'd rely so much on
them I would revert back to old habits I felt weren't correct anymore.

I was wrong. I needed traits for a clean design. I'm glad I took the time to
appreciate them for what they may bring.

<span class="f">fault</span> comes with a set of network faults. Designing to
accomodate for their differences, yet providing a shared interface, was
achievable through traits.

Here is an extract of the injector trait:

```rust
pub trait Bidirectional: AsyncRead + AsyncWrite + Unpin + Send + Debug {}

#[async_trait]
pub trait FaultInjector:
    Send + Sync + Debug + Display
{
    async fn inject(
        &self,
        stream: Box<dyn Bidirectional + 'static>,
        event: Box<dyn ProxyTaskEvent>,
        side: StreamSide,
    ) -> Result<
        Box<dyn Bidirectional + 'static>,
        (ProxyError, Box<dyn Bidirectional + 'static>),
    >;
}
```

There is something of beauty when we find the right interface. The simplicity,
yet the power, of this simple trait is at the core of
<span class="f">fault</span>.

It describes enough to take a stream and returns a new stream. This new stream
implements a specific fault. For instance, `latency` is implemented as follows:

```rust
#[tracing::instrument]
async fn inject(
    &self,
    stream: Box<dyn Bidirectional + 'static>,
    event: Box<dyn ProxyTaskEvent>,
    side: StreamSide,
) -> Result<
    Box<dyn Bidirectional + 'static>,
    (ProxyError, Box<dyn Bidirectional + 'static>),
> {
    // not the configured side, let's bail now
    if side != self.settings.side {
        return Ok(stream);
    }

    let direction = self.settings.direction.clone();

    let (read_half, write_half) = split(stream);

    let _ = event.with_fault(FaultEvent::Latency {
        direction: direction.clone(),
        side: self.settings.side.clone(),
        delay: None,
    });

    // Wrap the read half if ingress or both directions are specified
    let limited_read: Box<dyn BidirectionalReadHalf> =
        if direction.is_ingress() {
            match LatencyStreamRead::new(
                read_half,
                self.clone(),
                Some(event.clone()),
            ) {
                Ok(lr) => Box::new(lr),
                Err(rh) => Box::new(rh)
            }
        } else {
            Box::new(read_half) as Box<dyn BidirectionalReadHalf>
        };

    // Wrap the write half if egress or both directions are specified
    let limited_write: Box<dyn BidirectionalWriteHalf> =
        if direction.is_egress() {
            match LatencyStreamWrite::new(
                write_half,
                self.clone(),
                Some(event.clone()),
            ) {
                Ok(lw) => Box::new(lw),
                Err(wh) => Box::new(wh),
            }
        } else {
            Box::new(write_half) as Box<dyn BidirectionalWriteHalf>
        };

    // Combine the limited read and write into a new bidirectional stream
    Ok(Box::new(LatencyBidirectional::new(limited_read, limited_write)))
}
```

From there, each directional side may apply latency to the stream
independently.

Without a trait, the code would have been less elegant in my book. With that
said, everything doesn't need to be behind a trait.

I've come across some Python projects which, I feel, take the new power
brought by typing annotations, one step too far. Everything becoming a generic,
making it somewhat more complicated to reason with.

Power and simplicity are gentle properties. It's easy to tip the balance
on either one.

Traits are wonderful. Use them. Don't abuse them.

### Async in rust can be cumbersome

<span class="f">fault</span> deals with I/O, it seemed to me that async
was an obvious design decision. I didn't have much choice either because most
of the ecosystem has developed around the [tokio](https://tokio.rs/) crate.

So on I went with `async`. I'm used to it as Python has the same way of
differentiating async and sync code path.

The trick is that it's pervasive. Once you start, you have to commit to it and,
sometimes, this makes the code quite verbose in ways. You end up with code that
reads like sync but which isn't. It doesn't bother me that much again because
I've followed the same approach with Python or TypeScript. Yet, there is
something oddly off with it.

It also took me a while to find the right design and machinery when it came
to share date across await points.

Moving from protecting shared data with Mutexes, then using channels.
I ended up with a mixture of a few powerful crates:

- [scc](https://crates.io/crates/scc): scalable concurrent containers (HashMap..)
- [oneshot](https://crates.io/crates/oneshot): spsc (single producer, single consumer) channel
- [kanal](https://crates.io/crates/kanal): multi-producer and multi-consumer channels

The near lock-free design of these crates has made a real difference under load.
They've also simplified some of the code when compared to mutexes.

async is wonderful. Use it. Don't abuse it.

### I'm cloning too much aren't I?

Oh my, this one will make me look a n00b. Due to the precious idea behind 
ownership. I often ended up cloning the heck out of everything. Looking
back at my code, I would say there are plenty of places where I'm cloning when
I could borrow instead.

### Stop calling `.unwrap()`

Enough said. That's one refactoring afternoon for me.

### My code is dead ugly

This leads to me this point. I cannot get the feeling off that my rust code is
currently dead ugly, or more nicely put, still in progress.

Coding is a learning experience. You refine your skills and your
philosophies evolve as you reflect on your past.

When I look back, I'm cringing at many facets of the code base.

### So much refactoring

This leads me to the fact that <span class="f">fault</span> has already
undergone many refactoring, some large, iterations. Sometimes because
I discovered I was wriging rust code the wrong way, sometimes a new features
led to a deeper change, sometimes because performances required it and at times
because the code was indeed ugly enough to warrant a refactoring.

### What is idiomatic rust after all?

Python is much older language than rust, it took time for the communities
to organize themselves around common grounds. One of these corner stone is the
beloved [pep8](https://peps.python.org/pep-0008/), all the way back to 2001,
after the language celebrated its tenth anniversary.

Yet, for a while, projects didn't have the tooling necessary to enforce
these conventions. However these gradually changed with the arrival of
projects such as pyflakes, pylint, pycodestyle. Then
[black](https://github.com/psf/black) really made a massive difference because
it freed developers from thinking about apply consistency manually. More
recently [ruff](https://astral.sh/ruff) brought a level of speed which
redistributed the cards entirely.

When you are pampered with a fantastic set of tools like this, you really
feel weakened when you move to a different ecosystem.

I naively assumed I'd find the same richness and vibrant projects in rust. But,
I'd say Python is much more comprehensive here. Sure, you can run `cargo fmt`
and ̀`cargo clippy`. That is a good starting point.

But I haven't found anything that captures quite what `black` or `ruff` offer.
The ability to say "this is how good rust code looks like". Clippy helps a lot
there of course but I might not be using it well enough yet.

Once more, you are facing the question of choice, even for the most basic
parts of writing rust.

### On the documentation of rust projects

rust has some amazing crates. One thing I should note is that the way rust
projects approach documentation is entirely different from the Python world.

In Python, most projects have documentation beyond their source codes. These
documentations are organized in meaningful ways (Getting Started, How-Tos, 
Advanced, References). They are rendered in a way that make them fantastic
to use. Projects like [mkdocs material](https://squidfunk.github.io/mkdocs-material/)
or [shibuya](https://shibuya.lepture.com/) demonstrate that documentation
doesn't have to be boring looking.

Oddly, aside from fairly rare cases (for instance tokio.
[clap](https://rust-cli.github.io/book/index.html) also tries to 
raise the bar a bit), rust projects default to the dry "source code comments
sprinkled with a few examples".

Sure, rust has a very powerful typing support but this doesn't mean you
can default to function signatures as a mean to document projects.

I think the rust ecosystem has some room for progress still there.

!!! tip

    If you're reading this and looking to improve your documentation, I suggest
    to explore some of the ideas developed on [Diátaxis](https://diataxis.fr/).

## At the end of the day, Python or rust?

**Both!**

I don't think it makes sense to pick one over the other in absolute manner.

rust and Python complement each other. If anything, we might see a future
where both work so natively and fluentely together than we won't even think
about it. Projects such [pyo3](https://github.com/PyO3/pyo3) are paving the way.

Just do yourself a favour, don't pick one, use both!

---

The rest will come soon...

## Bring on the features

### A proxy has a core feature

### Let's bring automation to developers, aka shift left reliability

### Scheduling a bit of a detour

### JSON is for machines, not for people

### Can we push the automation further?

## Deploying has to happen at some point, am I right?

