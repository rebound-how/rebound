# Contributions

Contributions describe the valuable system properties an experiment targets as well as how much they contributes to it. Those properties usually refer to aspects stakeholders care about. Aggregated they offer a powerful metric about the effort and focus on building confidence across the system.

In Reliably, you are given the opportunity to set contributions when creating an experiment using [Custom Templates](/docs/concepts/custom-templates/) or the [Experiment Builder](/docs/features/builder/).

<p align=center><img src="/assets/images/guides/contributions/contributions-component-854.webp" width="427" height="382" alt="The contributions editor allows user to add contributions and their values" /></p>

The contributions form provides users with 4 default contributions: Availability, Latency, Security, and Errors. It is also possible to add custom contributions.

A contribution can take one of the following values:

- High
- Medium
- Low
- None

Setting a contribution to `None` is different than not declaring it.

For example, let's take the following contributions definition:

|              |        |
| ------------ | ------ |
| Availability | Medium |
| Latency      | High   |
| Security     | None   |
| Errors       | None   |
| Scalability  | None   |

This sample tells us that the experiment contributes mainly to exploring latency of the system and moderately to its availability. However, it is explicit here this experiment does not address security, errors, nor scalability.

On the other hand:

|              |        |
| ------------ | ------ |
| Availability | Medium |
| Latency      | High   |
| Security     | None   |
| Errors       | None   |

This tells us the same about latency, availability, security, and errors but we can’t presume anything about scalability.
