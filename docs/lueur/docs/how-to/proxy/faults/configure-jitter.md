# Introducing Jitter Fault Into Your Flow

This guide will walk you through emulating network jitter into your
application using lueur proxy capabilities.

## What You'll Achieve

In this guide, you’ll learn how to deliberately inject network jittering into
your application flow using lueur’s proxy features.

## Light Ingress Jitter - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with jitter on ingress

    ```bash
    lueur \
        --with-jitter \ # (1)!
        --jitter-amplitude 30 \ # (2)!
        --jitter-frequency 5 \ # (3)!
        --jitter-direction ingress # (4)!
    ```

    1.  Enable the jitter fault support
    2.  Set the {==amplitude==} (maximum delay applied to packets)
    2.  Set the {==frequency==} (how often jitter is applied per second)
    3.  Apply the fault on {==ingress==}

## Strong Egress Jitter - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with jitter on egress

    ```bash
    lueur \
        --with-jitter \ # (1)!
        --jitter-amplitude 50 \ # (2)!
        --jitter-frequency 10 \ # (3)!
        --jitter-direction egress # (4)!
    ```

    1.  Enable the jitter fault support
    2.  Set the {==amplitude==} (maximum delay applied to packets)
    2.  Set the {==frequency==} (how often jitter is applied per second)
    3.  Apply the fault on {==egress==}

## Bidirectional Jitter - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with jitter on egress and ingress

    ```bash
    lueur \
        --with-jitter \ # (1)!
        --jitter-amplitude 30 \ # (2)!
        --jitter-frequency 8 \ # (3)!
        --jitter-direction both # (4)!
    ```

    1.  Enable the jitter fault support
    2.  Set the {==amplitude==} (maximum delay applied to packets)
    2.  Set the {==frequency==} (how often jitter is applied per second)
    3.  Apply the fault on {==egress==} and {==ingress==}
