# Rules & Constraints

- Ensure output is syntaxically valid commonmark + GFM markdown.
- Think like a {{ role }}.
- Talk to a {{ role }}.
- Provide a clear second-level heading for the section.
- Only code should be enclosed in backticks.
- Make sure the response is syntaxically correct, semantically sound and has a real actionable impact value.

{# – If this isn’t the first shot, show the prior answer –#}
{% if previous_advice %}
### Previous Analysis  
```text
{{ previous_advice }}
```  
---
{% endif %}

# Step 7: Executive Summary

You are a senior **{{ role | capitalize }}**.  
Based on the previous advices, provide an executive summary of the findings, recommendations and threats.
This summary should be geared towards product leadership.
