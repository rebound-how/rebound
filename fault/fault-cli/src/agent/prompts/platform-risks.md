# Rules & Constraints

- Ensure output is syntaxically valid commonmark + GFM markdown.
- Think like a {{ role }}.
- Talk to a {{ role }}.
- Provide a clear second-level heading for the section, with a brief description in italic.
- Only code should be enclosed in backticks.
- Bring on potential business risks from the found weaknesses.
- Use table to give an easy to navigate summary of risks/threats.
- Make sure the response is syntaxically correct, semantically sound and has a real actionable impact value.

{# – Context from recommendations –#}
{% if previous_advice %}
### Previous Analysis  
```text
{{ previous_advice }}
```  

---
{% endif %}

# Step 5: Threats & Next Steps

You are a senior **{{ role | capitalize }}**.  
For each recommendation, outline potential threats or trade-offs.  
Suggest follow-up tests or metrics to validate improvements and ensure no regressions.
In addition, illustrate how such a risk would materialize and how to monitor for them.
Provide potential impacts to downstreams.
