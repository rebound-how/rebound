# Introducing Bandwidth Fault Into Your Flow

This guide will walk you through emulating network bandwidth degradation into your
application using lueur proxy capabilities.

## What You'll Achieve

In this guide, you’ll learn how to deliberately inject network bandwidth
constraints into your application flow using lueur’s proxy features.

## Severe Upstream Slowdown - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with bandwidth set from server-side ingress

    ```bash
    lueur \
        --with-bandwidth \ # (1)!
        --bandwidth-side server \ # (2)!
        --bandwidth-direction ingress \ # (3)!
        --bandwidth-rate 500 \ # (4)!
        --bandwidth-unit kbps
    ```

    1.  Enable the bandwidth fault support
    2.  Apply the fault on {==server==} side
    3.  Apply the fault on {==ingress==}
    4.  Set a very limited bandwidth to 500kbps

## Light Client Slowdown - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with bandwidth set from client-side both ingress and egress

    ```bash
    lueur \
        --with-bandwidth \ # (1)!
        --bandwidth-side client \ # (2)!
        --bandwidth-direction both \ # (3)!
        --bandwidth-rate 1 \ # (4)!
        --bandwidth-unit mbps
    ```

    1.  Enable the bandwidth fault support
    2.  Apply the fault on {==client==} side
    3.  Apply the fault on {==ingress==} and {==egress==}
    4.  Set a reduced bandwidth to 1mbps

## Throughput Degradation - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with bandwidth set from server-side both ingress and egress

    ```bash
    lueur \
        --with-bandwidth \ # (1)!
        --bandwidth-side server \ # (2)!
        --bandwidth-direction both \ # (3)!
        --bandwidth-rate 2 \ # (4)!
        --bandwidth-unit mbps
    ```

    1.  Enable the bandwidth fault support
    2.  Apply the fault on {==server==} side
    3.  Apply the fault on {==ingress==} and {==egress==}
    4.  Set a reduced bandwidth to 2mbps
