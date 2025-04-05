#!/usr/bin/env python3
import time
import threading
from concurrent import futures
import grpc

# Import the generated gRPC classes
import service_pb2
import service_pb2_grpc

COUNT = 0
LOCK = threading.Lock()

class PluginService(service_pb2_grpc.PluginServiceServicer):
    def HealthCheck(self, request, context):
        """Returns the current status of the plugin."""
        print("health")
        return service_pb2.HealthCheckResponse(
            healthy=True,
            message=""
        )

    def GetPluginInfo(self, request, context):
        """Returns plugin metadata."""
        print("info")
        return service_pb2.GetPluginInfoResponse(
            name="MyAdvancedPlugin",
            version="1.0.0",
            author="John Doe",
            url="https://github.com/johndoe/myadvancedplugin",
            platform="python",
        )

    def GetPluginCapabilities(self, request, context):
        """Returns the capabilities of this plugin."""
        print("capabilities")
        return service_pb2.GetPluginCapabilitiesResponse(
            can_handle_http_forward=True,
            can_handle_tunnel=True,
            protocols=[service_pb2.GetPluginCapabilitiesResponse.SupportedProtocol.POSTGRESQL]
        )

    def ProcessHttpRequest(self, request, context):
        """
        Processes an incoming HTTP request.
        In this example we simply echo the request back,
        indicating no modification.
        """
        global COUNT, LOCK
        with LOCK:
            COUNT = COUNT + 1
            print(COUNT)
        return service_pb2.ProcessHttpRequestResponse(
            action=service_pb2.ProcessHttpRequestResponse.Action.CONTINUE,
            modified_request=request.request,
            # abort_response is left empty since we're not aborting.
        )

    def ProcessHttpResponse(self, request, context):
        """
        Processes an outgoing HTTP response.
        Here, we simply pass the response through unchanged.
        """
        return service_pb2.ProcessHttpResponseResponse(
            action=service_pb2.ProcessHttpResponseResponse.Action.CONTINUE,
            modified_response=request.response,
        )

    def ProcessTunnelData(self, request, context):
        """
        Processes a chunk of tunnel (TCP/TLS) data.
        For demonstration, if the chunk is small (< 100 bytes) we ask for buffering,
        and if it's large enough we reverse the chunk and send it back.
        """
        return service_pb2.ProcessTunnelDataResponse(
            action=service_pb2.ProcessTunnelDataResponse.Action.PASS_THROUGH,
            modified_chunk=request.request,
        )

def serve():
    # Create a gRPC server with a thread pool.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Register the service.
    service_pb2_grpc.add_PluginServiceServicer_to_server(PluginService(), server)
    
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
