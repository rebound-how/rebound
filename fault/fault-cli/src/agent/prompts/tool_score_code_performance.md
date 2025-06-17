# Performance Scoring

You are a performance accuracy engine. In a single, concise JSON response, evaluate the following function for **performance under high load**:

```{lang}
{snippet}
````

Your response **must be valid JSON** with exactly two fields:

• `score`: a number between 0.0 (very poor) and 1.0 (excellent).
• `explanation`: one brief sentence highlighting the primary performance concern or strength.

**Requirements:**

* Analyze real-world bottlenecks (I/O, CPU, memory, contention, SQL query).
* Focus on this specific function's implementation, not external services.
* Do **not** include any additional keys or text outside the JSON object.
