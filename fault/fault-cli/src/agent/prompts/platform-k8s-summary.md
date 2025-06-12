# Rules & Constraints

- Ensure output is syntaxically valid commonmark + GFM markdown.
- Think like a {{ role }}.
- Talk to a {{ role }}.
- Provide a clear second-level heading for the section.
- Only code should be enclosed in backticks.
- Make sure the response is syntaxically correct, semantically sound and has a real actionable impact value.

# Step 1: High-Level Kubernetes Resources Overview

You are a senior **{{ role | capitalize }}**.  
Based on the following set of Kubernetes resources, provide a concise (2–3 sentence) summary of the overall service resilience, reliability and performance posture.

```yaml
{{ resource }}
```
