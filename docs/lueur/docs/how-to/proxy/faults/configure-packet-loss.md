# Introducing Packet Loss Fault Into Your Flow

This guide will walk you through emulating network packet loss into your
application using lueur proxy capabilities.

## What You'll Achieve

In this guide, you’ll learn how to deliberately inject network packet loss
issues into your application flow using lueur’s proxy features.

## Client Packet Loss - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with packet loss from client side

    ```bash
    lueur \
        --with-packet-loss \ # (1)!
        --packet-loss-side client # (2)!
    ```

    1.  Enable the packet-loss fault support
    2.  Apply the fault on {==client==} side

## Server Packet Loss - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with packet loss from server side

    ```bash
    lueur \
        --with-packet-loss \ # (1)!
        --packet-loss-side server # (2)!
    ```

    1.  Enable the packet-loss fault support
    2.  Apply the fault on {==server==} side
