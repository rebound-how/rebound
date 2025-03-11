# Introducing HTTP Fault Into Your Flow

This guide will walk you through emulating application level HTTP errors into your
application using lueur proxy capabilities.

## What You'll Achieve

In this guide, you’ll learn how to deliberately inject HTTP errors into
your application flow using lueur’s proxy features.

## Constant Internal Server Error - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with HTTP Error 500 from the remote server

    ```bash
    lueur \
        --with-http-response \ # (1)!
        --http-status 500 \ # (2)!
        --http-response-trigger-probability 1  # (3)!
    ```

    1.  Enable the HTTP error fault support
    2.  Set the {==status==} to 500
    3.  Set the error on all responses

## Intermittent Service Unavailable Errors - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with HTTP Error 503 from the remote server

    ```bash
    lueur \
        --with-http-response \ # (1)!
        --http-status 503 \ # (2)!
        --http-response-trigger-probability 0.5  # (3)!
    ```

    1.  Enable the HTTP error fault support
    2.  Set the {==status==} to 503
    3.  Set the error on half of the responses

## Intermittent Not Found Errors - Step-by-Step

-   [X] Install lueur
    
    Follow the procedure to [install](../tutorials/install/) lueur on your
    machine.

-   [X] Start the proxy with HTTP Error 404 from the remote server

    ```bash
    lueur \
        --with-http-response \ # (1)!
        --http-status 404 \ # (2)!
        --http-response-trigger-probability 0.5 \ # (3)!
        --http-body '{"error": "true"}' # (4)!
    ```

    1.  Enable the HTTP error fault support
    2.  Set the {==status==} to 404
    3.  Set the error on half of the responses
    4.  Set a JSON response body
