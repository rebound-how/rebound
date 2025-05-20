# How to Simulate HTTP Errors Using fault

This guide will walk you through emulating application level HTTP errors into your
application using fault proxy capabilities.

??? abstract "Prerequisites"

    -   [X] Install fault

        If you haven’t installed fault yet, follow the
        [installation instructions](../../install.md).

    -   [X] Basic Proxy Setup
        Be familiar with running fault run {==--with-[fault]==} commands from
        your terminal.

## Constant Internal Server Error

-   [X] Start the proxy with HTTP Error 500 from the remote server

    ```bash
    fault run \
        --with-http-response \ # (1)!
        --http-response-status 500 \ # (2)!
        --http-response-trigger-probability 1  # (3)!
    ```

    1.  Enable the HTTP error fault support
    2.  Set the {==status==} to 500
    3.  Set the error on all responses

## Intermittent Service Unavailable Errors

-   [X] Start the proxy with HTTP Error 503 from the remote server

    ```bash
    fault run \
        --with-http-response \ # (1)!
        --http-response-status 503 \ # (2)!
        --http-response-trigger-probability 0.5  # (3)!
    ```

    1.  Enable the HTTP error fault support
    2.  Set the {==status==} to 503
    3.  Set the error on half of the responses

## Intermittent Not Found Errors

-   [X] Start the proxy with HTTP Error 404 from the remote server

    ```bash
    fault \
        --with-http-response \ # (1)!
        --http-response-status 404 \ # (2)!
        --http-response-trigger-probability 0.5 \ # (3)!
        --http-response-body '{"error": "true"}' # (4)!
    ```

    1.  Enable the HTTP error fault support
    2.  Set the {==status==} to 404
    3.  Set the error on half of the responses
    4.  Set a JSON response body
