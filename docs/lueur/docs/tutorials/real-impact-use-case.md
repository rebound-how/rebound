# Exploring Network Fault Impact

## Introduction

**Context**:  
  Introduce the idea that modern applications often rely on third-party APIs over HTTPS.  
  Explain that this tutorial will walk the reader through simulating various network faults using Lueur to understand how their own application behaves under non-ideal conditions.
  
**Goal**:  
  By the end of this tutorial, the reader will:
  - Configure Lueur to apply multiple types of faults (latency, errors, bandwidth limits) to an outbound HTTPS call.
  - Run a defined scenario that systematically applies these faults.
  - Observe the application’s behavior and interpret the resulting report.

## Prerequisites

**Tools & Setup**:

  - Lueur installed on your local machine.
  - An existing application or a simple test client that makes HTTPS calls to a known third-party endpoint (e.g., `https://api.example.com`).
  - Basic familiarity with setting `HTTP_PROXY` or `HTTPS_PROXY` environment variables.
  
**Assumptions**:  
  The tutorial assumes the reader has followed the *Getting Started* tutorial and understands how to launch Lueur in basic mode.

## Step 1: Choosing the Third-Party Endpoint

- Explain how to pick a stable third-party endpoint (e.g., a public API or a test endpoint) for demonstration.  
- Suggest `https://api.example.com` as a placeholder.  
- Verify the application makes a simple GET request to this endpoint under normal conditions.

## Step 2: Creating a Scenario File

- Introduce the scenario file (`scenario.toml`) and explain its purpose in defining multiple, sequential tests.  
- Provide a sample `scenario.toml` snippet that includes a variety of faults:
  - A run with added latency (e.g., 300ms mean).
  - A run that simulates packet loss (e.g., 2%).
  - A run that injects occasional 500 errors.
  - A run that limits bandwidth to a low rate.
  
- Show how to write these steps in a way that Lueur’s scenario runner can understand.

## Step 3: Configuring Your Application and Environment

- Instruct setting `HTTPS_PROXY` to `http://127.0.0.1:8080` so all outbound HTTPS calls route through Lueur.
- Confirm that your application still functions normally without faults before running the scenario.

## Step 4: Running the Scenario

- Demonstrate the command:
  ```bash
  lueur scenario run --scenario scenario.toml --report scenario-report.json
  ```
- Explain what Lueur is doing: it launches a proxy, applies each set of defined faults in sequence, and captures metrics and logs.

## Step 5: Observing Logs and Output

- Show how Lueur’s console output reports requests, injected faults, and response times.
- Emphasize what to look for:
  - Increased latency in responses.
  - Occasional HTTP 500 errors injected by the scenario.
  - Impact of packet loss or bandwidth constraints on perceived throughput.

## Step 6: Analyzing the Generated Report

- Introduce the `scenario-report.json` file:
  - Show how to open it and what data to look for.
  - Highlight metrics like total request counts, success vs. error rates, average latency, and other relevant stats.
- Discuss interpreting this data to identify how resilient the application is to each type of fault.

## Step 7: Identifying Areas for Improvement

- Encourage the reader to reflect on what they’ve observed:
  - Did the application handle latency gracefully, or did requests time out?
  - Did error handling and retries come into play when faced with injected 500 errors?
  - How did the application behave when bandwidth was limited?
  
- Suggest actionable improvements:
  - Consider adding retry logic or timeouts.
  - Improve error handling to degrade gracefully when encountering random faults.
  - Optimize for slower networks if necessary.

## Next Steps

- Point to other How-To guides for fine-tuning scenarios or integrating Lueur into CI pipelines.
- Suggest expanding the scenario file with more complex tests or different endpoints.
- Encourage experimenting with different fault profiles to continuously challenge and improve the application’s resilience.

## Conclusion

- Summarize what was achieved:
  - The reader learned how to define and run a scenario that simulates multiple network faults on a real HTTPS call.
  - They observed how their application responded under stressed conditions and gathered data to guide improvements.
  
- Reinforce that this practice helps catch issues earlier, ensuring a smoother path to production.

