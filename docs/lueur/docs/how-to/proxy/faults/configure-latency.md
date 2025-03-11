# Introducing Latency Fault Into Your Flow

This guide will walk you through introducing network latency into your
application using lueur proxy capabilities.

## What You'll Achieve

In this guide, you’ll learn how to deliberately inject network latency into your
application flow using lueur’s proxy features. By exploring different latency
[distributions](../../../explanations/fault-injection-basics.md), you'll gain insights
into how your system behaves under varying network conditions.

## Normal Distribution - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with a normal distribution latency

    ```bash
    lueur run \
        --with-latency \ # (1)!
        --latency-distribution normal \ # (2)!
        --latency-mean 300 \ # (3)!
        --latency-stddev 40 # (4)!
    ```

    1.  Enable the latency fault support
    2.  Use the {==normal==} distribution
    3.  Introduce a latency of {==300ms==} on average
    4.  Add {==40ms==} of jitter

## Uniform Distribution - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with a uniform distribution latency

    ```bash
    lueur run \
        --with-latency \ # (1)!
        --latency-distribution uniform \ # (2)!
        --latency-min 300 \ # (3)!
        --latency-max 500 # (4)!
    ```

    1.  Enable the latency fault support
    2.  Use the {==uniform==} distribution
    3.  Introduce a latency of at least {==300ms==}
    4.  Set the maximum latency to {==500ms==}


## Pareto Distribution - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with a Pareto distribution latency

    ```bash
    lueur run \
        --with-latency \ # (1)!
        --latency-distribution pareto \ # (2)!
        --latency-scale 20 \ # (3)!
        --latency-shape 1.5 # (4)!
    ```

    1.  Enable the latency fault support
    2.  Use the {==pareto==} distribution
    3.  Set a scale of {==20ms==}
    4.  Set the shape of the distribution to {==1.5==}

## Pareto Normal Distribution - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with a Pareto distribution latency

    ```bash
    lueur run \
        --with-latency \ # (1)!
        --latency-distribution pareto \ # (2)!
        --latency-scale 20 \ # (3)!
        --latency-shape 1.5 \ # (4)!
        --latency-mean 50 \ # (5)!
        --latency-stddev 15 # (6)!
    ```

    1.  Enable the latency fault support
    2.  Use the {==pareto==} distribution
    3.  Set a scale of {==20ms==}
    4.  Set the shape of the distribution to {==1.5==}
    5.  Set a mean of {==50ms==} on average
    6.  Add {==15ms==} of jitter

## Latency On Ingress Only - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with any distribution and set the direction to {==ingress==}.

    ```bash
    lueur run \
        --with-latency \ # (1)!
        --latency-direction ingress \ # (2)!
        --latency-mean 50
    ```

    1.  Enable the latency fault support
    2.  Set the latency to take place in {==ingress==}

## Latency On Egress Only - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with any distribution and set the direction to {==egress==}.

    ```bash
    lueur run \
        --with-latency \ # (1)!
        --latency-direction egress \ # (2)!
        --latency-mean 50
    ```

    1.  Enable the latency fault support
    2.  Set the latency to take place in {==egress==}

## Latency On Client-Side Only - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with any distribution and set the side to {==client==}.

    ```bash
    lueur run \
        --with-latency \ # (1)!
        --latency-side client \ # (2)!
        --latency-mean 50
    ```

    1.  Enable the latency fault support
    2.  Set the latency to take place on {==client==} side

## Latency On Server-Side Only - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with any distribution and set the side to {==server==}.

    ```bash
    lueur run \
        --with-latency \ # (1)!
        --latency-side server \ # (2)!
        --latency-mean 50
    ```

    1.  Enable the latency fault support
    2.  Set the latency to take place on {==server==} side


## Latency On Ingress From Server-Side Only - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with any distribution and set the direction to {==ingress==} and the side to {==server==}.

    ```bash
    lueur run \
        --with-latency \
        --latency-direction ingress \
        --latency-side server \
        --latency-mean 50
    ```
