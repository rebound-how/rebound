import time
from concurrent import futures
import grpc

# Import the generated gRPC classes
import plugin_pb2
import plugin_pb2_grpc

# typing is not yet supported by the gRPC library
# see https://github.com/grpc/grpc/issues/29041
class PluginService(plugin_pb2_grpc.PluginServiceServicer):
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
        """Returns the capabilities of this plugin."""
        return plugin_pb2.GetPluginCapabilitiesResponse(
            can_handle_http_forward=True,
            can_handle_tunnel=True,
            protocols=[plugin_pb2.GetPluginCapabilitiesResponse.SupportedProtocol.POSTGRESQL]
        )

    def ProcessHttpRequest(self, request, context):
        """
        Processes an incoming HTTP request.
        In this example we simply echo the request back,
        indicating no modification.
        """
        return plugin_pb2.ProcessHttpRequestResponse(
            action=plugin_pb2.ProcessHttpRequestResponse.Action.CONTINUE,
            modified_request=request.request,
            # abort_response is left empty since we're not aborting.
        )

    def ProcessHttpResponse(self, request, context):
        """
        Processes an outgoing HTTP response.
        Here, we simply pass the response through unchanged.
        """
        return plugin_pb2.ProcessHttpResponseResponse(
            action=plugin_pb2.ProcessHttpResponseResponse.Action.CONTINUE,
            modified_response=request.response,
        )

    def ProcessTunnelData(self, request, context):
        """
        Processes a chunk of tunnel (TCP/TLS) data.
        For demonstration, if the chunk is small (< 100 bytes) we ask for buffering,
        and if it's large enough we reverse the chunk and send it back.
        """
        return plugin_pb2.ProcessTunnelDataResponse(
            action=plugin_pb2.ProcessTunnelDataResponse.Action.PASS_THROUGH,
            modified_chunk=request.request,
        )

def serve():
    # Create a gRPC server with a thread pool.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Register the service.
    plugin_pb2_grpc.add_PluginServiceServicer_to_server(PluginService(), server)
    
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
