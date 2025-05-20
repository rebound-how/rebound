# Run fault as a Reliably Plan

This guide will walk you through running fault as part of a
[Reliably Plan][reliably].

[reliably]: https://reliably.com

??? abstract "Prerequisites"

    This guide assumes you have an account on a Reliably platform instance.

## Run as part of a Reliably Plan

-   [X] Create the Reliably Experiment

    To create the Experiment, go to the {==Builder==} page. Look for the
    {==Rebound fault==} target and select the {==Run Network Fault Proxy==}
    action.

    ![Reliably Builder](/assets/guide-reliably-builder.png)

    Once select, a new page opens and allows you to fill the details of your
    experiment.

    * Set a meaninful title and description
    * Set tags that will allow members to filter experiments
    * Set contributions which define the dimensions impacted by the experiment
  
    Next, fill the experiment's activities:

    ![Reliably Experiment Form](/assets/guide-reliably-experiment-form.png)

    Pass the [proxy CLI arguments](../reference/cli-commands.md#run-command-options)
    as you would to the `fault run` command itself. For instance, let's use the
    following argument line:

    ```bash
        --with-latency \ # (1)!
        --latency-mean 300 \ # (2)!
        --latency-sched "duration:10s;start:25s,duration:17s" # (3)!
    ```

    1. Run fault with a `latency` fault
    2. Inject a `300ms` delay on responses
    3. Inject the fault only for around 60% of the total duration of the run

    We suggest you run the action in background so that other activities can
    take place while it is running.

    Finally, if you did not set the `--duration` flag, you want to keep the
    {==Stop Network Proxy==} action so that your proxy is properly terminated.
    In such case, remember you can only set
    [fixed schedules](../how-to/proxy/lifecycle.md#scheduling).

    At that stage you may want to insert new activities once the proxy has
    started by clicking the little `+` icon on the right of the
    {==Run Network Fault Proxy==} activity.

    For instance, you could run a basic load test and send its traffic via
    the proxy. Choose the {==Run Simple Load Test==} action from the Reliably
    target provider. Fill the target URL and, at the bottom of the action,
    set the proxy url to `http://localhost:3180` which is the proxy's address.

    Save now the experiment which redirects you to its page.

    ![Reliably Experiment](/assets/guide-reliably-experiment.png)

-   [X] Schedule the Reliably Plan

    Click now on the {==Run experiment==} button which leads you to the
    Reliably Plan form.

    ![Reliably Plan Form](/assets/guide-reliably-plan-form.png)

    Select now the appropriate deployment to run the experiment. If, you need
    to pass specific Environment variables, you may set the {==Environment==}
    as well.

    On this example, we also enable the {==Open AI==} extension which will
    send the experiment's questions to [OpenAI](https://platform.openai.com)
    while the plan runs.

    !!! info

        No other information is ever sent to OpenAI.

    The plan will then be scheduled to start immediately.

    ![Reliably Plan](/assets/guide-reliably-plan.png)

-   [X] Review the Reliably Execution

    Once the plan has completed, you may review its execution. Below is the
    timeline of this execution:

    ![Reliably Execution Timeline](/assets/guide-reliably-plan-timeline.png)

    Zooming into the {==Run Simple Load Test==} step, we can indeed see how
    around 60% of the requests were impacted by our latency.

    ![Reliably Plan Load Test](/assets/guide-reliably-plan-load-test.png)

    As a bonus point, we can also see that our questions to OpenAI were keenly
    answered:

    ![Reliably Plan Assistant](/assets/guide-reliably-plan-assistant-1.png)

    The assistant exposes the theory behind exploring latency and moves on
    to show us a Chaos Toolkit experiment. Remember that a Chaos Toolkit
    experiment can be imported and used as a Reliably Experiment.

    !!! warning "Critical thinking remains your best strategy"

        LLM models are known to hallucinate at times. More than often, the LLM
        will suggest Chaos Toolkit activities that don't exist. Nonetheless,
        it's a valuable discussion starting point.

    ![Reliably Plan Assistant Follow up](/assets/guide-reliably-plan-assistant-2.png)

    The assistant expands on its reply with more useful context about what to
    look for as your run such an experiment.

    Overall, the assistant is here to support your own analysis and you should
    use it as a data point only, not as the one truth.

    Finally, the assistant also responds to the question about well-known
    incidents, which may help put your experiment into context:

    ![Reliably Plan Assistant Past Incidents](/assets/guide-reliably-plan-assistant-3.png)



## Next Steps

- **Explore [Reliably](https://reliably.com)** to understand how you can run
  a plan on various deployment targets.

