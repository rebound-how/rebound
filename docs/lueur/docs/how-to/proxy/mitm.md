# Capture and Model Traffic With MITM Plugins

lueur's fault are internally managed by design. To support any bespoke
scenarios you may need to explore, lueur offers an extension mechanism via
remote plugins.

In this guide, you will learn how to create a simple echo plugin before moving
to a more advanced use case by analyzing SQL queries on the fly.

??? abstract "Prerequisites"

    -   [X] Install lueur

        If you haven’t installed Lueur yet, follow the
        [installation instructions](../../install.md).

## Create a basic plugin with Python

-   [X] Get the lueur gRPC protocol file

    Download the [gRPC protocol file](https://github.com/rebound-how/rebound/blob/main/lueur/lueur-cli/src/plugin/rpc/protos/plugin.proto)
    on your machine.

-   [X] Install the Python dependencies with `uv`

    === "pip"

        ```bash
        pip install grpcio-tools
        ```

    === "uv"

        ```bash
        uv tool install grpcio-tools
        ```

-   [X] Generate the gRPC Python implementation from the Protocol file

    ```bash
    python -m grpc_tools.protoc \  # (1)!
        --python_out=. --grpc_python_out=. \  # (2)!
        -I . \  # (3)!
        plugin.proto  # (4)!
    ```

    1. Execute the gRPC tool to convert the protocol file into a Python source file
    2. The directory where to save the generated modules
    3. The include directory, this is the directory where the `plugin.proto` file lives
    4. The lueur protocol file you just downloaded

    This command should generate two files:

    * `plugin_pb2_grpc.py` the gRPC client and server classes
    * `plugin_pb2.py` the protocol buffer definitions

-   [X] Create your echo remote plugin

    Now that you have generated the Python modules implemtning the plugin
    protocol definition, you can implement your first plugin.

    ```python  title="plugin.py"
    import time
    from concurrent import futures
    import grpc

    # Import the generated gRPC classes
    import plugin_pb2
    import plugin_pb2_grpc


    class EchoPlugin(plugin_pb2_grpc.PluginServiceServicer):
        def HealthCheck(self, request, context):
            """Returns the current status of the plugin."""
            return plugin_pb2.HealthCheckResponse(
                healthy=True,
                message=""
            )

        def GetPluginInfo(self, request, context):
            """Returns plugin metadata."""
            return plugin_pb2.GetPluginInfoResponse(
                name="EchoPlugin",
                version="1.0.0",
                author="John Doe",
                url="https://github.com/johndoe/echoplugin",
                platform="python",
            )

        def GetPluginCapabilities(self, request, context):
            """
            Returns the capabilities of this plugin.
            
            Capabilities define the features supported by this plugin. Here, our
            echo plugin supports all of them.
            """
            return plugin_pb2.GetPluginCapabilitiesResponse(
                can_handle_http_forward=True,  # support HTTP forwarding
                can_handle_tunnel=True,  # support HTTP tunneling
                protocols=[]  # support any TCP protocol
            )

        def ProcessHttpRequest(self, request, context):
            """
            Processes an incoming HTTP request.
            In this example we simply echo the request back,
            indicating no modification.
            """
            print(request.request)
            return plugin_pb2.ProcessHttpRequestResponse(
                action=plugin_pb2.ProcessHttpRequestResponse.Action.CONTINUE,
                modified_request=request.request,
            )

        def ProcessHttpResponse(self, request, context):
            """
            Processes an outgoing HTTP response.
            Here, we simply pass the response through unchanged.
            """
            print(request.response)
            return plugin_pb2.ProcessHttpResponseResponse(
                action=plugin_pb2.ProcessHttpResponseResponse.Action.CONTINUE,
                modified_response=request.response,
            )

        def ProcessTunnelData(self, request, context):
            """
            Processes a chunk of tunnel (TCP/TLS) data.
            """
            # chunk is a piece of the stream as bytes
            print(request.chunk)
            return plugin_pb2.ProcessTunnelDataResponse(
                action=plugin_pb2.ProcessTunnelDataResponse.Action.PASS_THROUGH,
                modified_chunk=request.chunk,
            )

    def serve():
        # Create a gRPC server with a thread pool.
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        # Register the service.
        plugin_pb2_grpc.add_PluginServiceServicer_to_server(EchoPlugin(), server)
        
        port = 50051
        server.add_insecure_port(f'[::]:{port}')
        server.start()
        print(f"Plugin gRPC server is running on port {port}...")
        
        try:
            # Keep the server running indefinitely.
            while True:
                time.sleep(86400)
        except KeyboardInterrupt:
            print("Shutting down server...")
            server.stop(0)

    if __name__ == '__main__':
        serve()
    ```

    !!! note

        This code does not have any typing set on the variables and functions
        because the gRPC Python generator does not support them yet. This
        [issue](https://github.com/grpc/grpc/issues/29041) is a good place to
        track the effort towards adding typing.


-   [X] Run your echo plugin

    ```bash
    python plugin.py
    ```

    The plugin now listens on port `50051`

-   [X] Start the lueur's demo server

    ```bash
    lueur demo run
    ```

    We'll send traffic to this server via the proxy as an example of a target
    endpoint. Of course, you can use any server of your choosing.

-   [X] Use the echo plugin with lueur

    ```bash
    lueur run --grpc-plugin http://localhost:50051 --with-latency --latency-mean 300 --upstream '*'
    ```

    Use lueur as you would without the plugin. All the other flags support
    work the same way. Here lueur will forward traffic to your plugin but
    also apply the latency fault.

-   [X] Explore the plugin's behavior

    First, let's use the forward proxy:

    ```bash
    curl -x http://localhost:3180 http://localhost:7070
    ```

    This will show the request and responses in the plugin's console window.

    Next, let's use the tunnel proxy:

    ```bash
    curl -x http://localhost:3180 http://localhost:7070 -p
    ```

    This will show the stream of data as bytes as received by the plugin.