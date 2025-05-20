# Extend fault with gRPC Plugins

fault's fault are internally managed by design. To support any bespoke
scenarios you may need to explore, fault offers an extension mechanism via
remote plugins.

In this guide, you will learn how to create a simple echo plugin before moving
to a more advanced use case by analyzing SQL queries on the fly.

??? abstract "Prerequisites"

    -   [X] Install fault

        If you haven’t installed fault yet, follow the
        [installation instructions](../../install.md).

    -   [X] Python 3

        While the guides here use Python as a demonstration. You may choose
        any language that has a good support for gRPC, which basically means
        most modern languages today.

## Register Plugins

Before you create your first plugin, let's review how they are registered
with fault's proxy.

Use the `--grpc-plugin` flag, multiple times one for each plugin, on the
`fault run` command:

```bash
fault run --grpc-plugin http://localhost:50051 --grpc-plugin http://localhost:50052 ...
```

??? note "Plugin connection management"

    fault will tolerate plugins to disconnect and will attempt to reconnect to
    a plugin that went away.

## Create a Basic Plugin with Python

??? question "Are plugins only written in Python?"

    fault's plugins are gRPC servers so you can write plugins in any languages
    that [support gRPC](https://grpc.io/docs/#official-support). 
    We use Python here but feel free to adjust to your own personal preferences.

-   [X] Get the fault gRPC protocol file

    Download the [gRPC protocol file](https://github.com/rebound-how/rebound/blob/main/fault/fault-cli/src/plugin/rpc/protos/plugin.proto)
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
    4. The fault protocol file you just downloaded

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

-   [X] Start the fault's demo server

    ```bash
    fault demo run
    ```

    We'll send traffic to this server via the proxy as an example of a target
    endpoint. Of course, you can use any server of your choosing.

-   [X] Use the echo plugin with fault

    ```bash
    fault run --grpc-plugin http://localhost:50051 --with-latency --latency-mean 300 --upstream '*'
    ```

    Use fault as you would without the plugin. All the other flags support
    work the same way. Here fault will forward traffic to your plugin but
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

## Intercept PostgreSQL Messages

This guide will show you how to intercept the low-level [PostgreSQL
wire format](https://www.postgresql.org/docs/current/protocol-message-formats.html)
to parse some messages. This could be a skeletton to change the values
returned by the database and observe the impacts on your application.

-   [X] Get the fault gRPC protocol file

    Download the [gRPC protocol file](https://github.com/rebound-how/rebound/blob/main/fault/fault-cli/src/plugin/rpc/protos/plugin.proto)
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
    4. The fault protocol file you just downloaded

    This command should generate two files:

    * `plugin_pb2_grpc.py` the gRPC client and server classes
    * `plugin_pb2.py` the protocol buffer definitions


-   [X] Create your remote plugin

    Now that you have generated the Python modules implementing the plugin
    protocol definition, you can implement your plugin.

    !!! warning

        We are using Python again for this plugin. In a real scenario, we
        suggest you use rust here as Python does not have a native library that
        parses the PostgreSQL wire format. For the purpose of this guide, 
        we write a few helper functions but they are a bit fragile.
        If you wanted something more robust,
        we could suggest you use rust + [pgwire](https://github.com/sunng87/pgwire).

    ```python  title="plugin.py"
    import struct
    import time
    from concurrent import futures
    import uuid

    import grpc

    import plugin_pb2
    import plugin_pb2_grpc


    ###############################################################################
    # Our PostgreSQL plugin
    # We only implement the necessary entrypoints
    # * the healthcheck
    # * the metadata info
    # * the capabilitues of the plugin
    # * any streamed data from and to the PostgreSQL server
    ###############################################################################
    class PostgreSQLPluginService(plugin_pb2_grpc.PluginServiceServicer):
        def HealthCheck(self, request, context):
            """Returns the current status of the plugin."""
            return plugin_pb2.HealthCheckResponse(
                healthy=True,
                message=""
            )

        def GetPluginInfo(self, request, context):
            """Returns plugin metadata."""
            return plugin_pb2.GetPluginInfoResponse(
                name="PostgreSQLPlugin",
                version="1.0.0",
                author="John Doe",
                url="https://github.com/johndoe/echoplugin",
                platform="python",
            )

        def GetPluginCapabilities(self, request, context):
            """Returns the capabilities of this plugin."""
            return plugin_pb2.GetPluginCapabilitiesResponse(
                can_handle_http_forward=False,
                can_handle_tunnel=False,
                protocols=[
                    plugin_pb2.GetPluginCapabilitiesResponse.SupportedProtocol.POSTGRESQL
                ]
            )

        def ProcessTunnelData(self, request, context):
            """
            Processes a chunk of tunnel (TCP/TLS) data and parse it as a
            PostgreSQL message (at least the ones we are interested in).

            Essentially we parse the simple query sent by the client and the
            response from the server. We do not do anything with these messages
            but in a real scenario, you could change the returned values to
            trigger a fault from your application)
            """
            try:
                # you can use this id to discriminate streams later on
                stream_id = parse_stream_id(request.id)
                print(f"Stream id {stream_id}")
                print(parse_messages(stream_id, request.chunk))
            except Exception as x:
                print(x)

            # we have processed the chunk, now let's return it as-is to continue
            # its life in the proxy
            return plugin_pb2.ProcessTunnelDataResponse(
                pass_through=plugin_pb2.PassThrough(chunk=request.chunk)
            )


    ###############################################################################
    # A few helper functions to parse some of the messages we are interested in
    # to read from the PostgreSQL wire format
    # https://www.postgresql.org/docs/current/protocol-message-formats.html
    ###############################################################################
    def parse_stream_id(stream_id: str) -> uuid.UUID:
        return uuid.UUID(stream_id, version=4)

    def parse_row_description(data: bytes) -> dict:
        """
        Parse a PostgreSQL RowDescription (type 'T') message from raw bytes.
        Returns a dictionary with keys:
        {
            "field_count": int,
            "fields": [ { ... per-field metadata ... }, ... ]
        }
        Raises ValueError if the message is malformed.
        """
        if not data or data[0] != 0x54:  # 'T' = 0x54
            return

        if len(data) < 5:
            raise ValueError("Data too short to contain RowDescription length")

        if len(data) < 7:
            raise ValueError("Data too short to contain RowDescription field_count")
        field_count = struct.unpack_from(">H", data, 5)[0]

        offset = 7
        fields = []

        for _ in range(field_count):
            # Parse one field
            field, offset = parse_field_description(data, offset)
            fields.append(field)

        return {
            "field_count": field_count,
            "fields": fields,
        }


    def parse_field_description(data: bytes, offset: int) -> tuple[dict, int]:
        """
        Parse a single FieldDescription from 'data' starting at 'offset'.
        Returns (field_dict, new_offset).
        A FieldDescription has:
        - name (null-terminated string)
        - table_oid (Int32)
        - column_attr (Int16)
        - type_oid (Int32)
        - type_len (Int16)
        - type_mod (Int32)
        - format_code (Int16)
        """
        # Read field name (null-terminated)
        name, offset = read_null_terminated_string(data, offset)

        # We now read 18 bytes of metadata:
        #   4 + 2 + 4 + 2 + 4 + 2
        if offset + 18 > len(data):
            raise ValueError("Data too short for field metadata")

        table_oid, column_attr, type_oid, type_len, type_mod, format_code = struct.unpack_from(
            ">ihihih", data, offset
        )
        offset += 18

        # Build a dictionary representing this field
        field_dict = {
            "name": name,
            "table_oid": table_oid,
            "column_attr": column_attr,
            "type_oid": type_oid,
            "type_len": type_len,
            "type_mod": type_mod,
            "format_code": format_code,
        }
        return field_dict, offset


    def parse_row_data(data: bytes) -> dict:
        """
        Parse a PostgreSQL DataRpw (type 'B') message from raw bytes.
        Returns a dictionary with keys:
        {
            "field_count": int,
            "fields": [ { ... per-field metadata ... }, ... ]
        }
        Raises ValueError if the message is malformed.
        """
        if not data or data[0] != 0x44:  # 'D' = 0x44
            return

        if len(data) < 5:
            raise ValueError("Data too short to contain DataRow length")

        if len(data) < 7:
            raise ValueError("Data too short to contain DataRow field_count")
        field_count = struct.unpack_from(">H", data, 5)[0]

        offset = 7
        fields = []

        for _ in range(field_count):
            # Parse one field
            field, offset = parse_field_data(data, offset)
            fields.append(field)

        return {
            "field_count": field_count,
            "fields": fields,
        }



    def parse_field_data(data: bytes, offset: int) -> tuple[dict, int]:
        """
        Parse a single FieldData from 'data' starting at 'offset'.
        Returns (field_dict, new_offset).
        A FieldData has:
        - length (Int32)
        - bytes
        """
        offset += 2
        length = struct.unpack_from(">i", data, offset)[0]

        offset += 4

        if length == -1:
            value = None
        else:
            value = data[offset:offset+length]

        offset += length

        # Build a dictionary representing this field
        field_dict = {
            "length": length,
            "value": value,
        }
        return field_dict, offset


    def read_null_terminated_string(data: bytes, offset: int) -> tuple[str, int]:
        """
        Reads a null-terminated UTF-8 (or ASCII) string from 'data' at 'offset'.
        Returns (string, new_offset).
        Raises ValueError if a null byte isn't found before the end of 'data'.
        """
        start = offset
        while offset < len(data):
            if data[offset] == 0:
                raw_str = data[start:offset]
                offset += 1  # move past the null terminator
                try:
                    return raw_str.decode("utf-8"), offset
                except UnicodeDecodeError:
                    raise ValueError("Invalid UTF-8 in field name")
            offset += 1
        raise ValueError("Missing null terminator in field name")


    def parse_messages(stream_id: uuid.UUID, data: bytes):
        offset = 0
        messages = []

        while offset < len(data):
            if offset + 5 > len(data):
                raise ValueError("Not enough bytes for message type+length")
            
            msg_type = data[offset]
            offset += 1
            length = struct.unpack_from(">i", data, offset)[0]
            offset += 4

            end = offset + (length - 4)
            if end > len(data):
                raise ValueError("Truncated message: length beyond data boundary")

            payload = data[offset:end]
            offset = end

            if msg_type == 0x54:  # 'T'
                # Rebuild a T message chunk: 1 byte + 4 byte length + +2 byte field count + payload
                fields_count = struct.unpack_from(">H", data, 5)[0]
                row_desc_msg = bytes([msg_type]) + struct.pack(">i", length) + struct.pack(">H", fields_count) + payload
                row_desc = parse_row_description(row_desc_msg)
                messages.append(("RowDescription", row_desc))
            elif msg_type == 0x44:  # 'D' DataRow
                fields_count = struct.unpack_from(">H", data, 5)[0]
                row_data_msg = bytes([msg_type]) + struct.pack(">i", length) + struct.pack(">H", fields_count) + payload
                row_data = parse_row_data(row_data_msg)
                messages.append(("DataRow", row_data))
            elif msg_type == 0x43:  # 'C' CommandComplete
                messages.append(("CommandComplete", payload))
            elif msg_type == 0x5A:  # 'Z' ReadyForQuery
                messages.append(("ReadyForQuery", payload))
            elif msg_type == 0x51:  # 'Q' Query
                messages.append(("Query", payload))
            else:
                messages.append((f"Unknown({hex(msg_type)})", payload))

        return messages


    def serve():
        # Create a gRPC server with a thread pool.
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        # Register the service.
        plugin_pb2_grpc.add_PluginServiceServicer_to_server(PostgreSQLPluginService(), server)
        
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

-   [X] Run your plugin

    ```bash
    python plugin.py
    ```

    The plugin now listens on port `50051`

-   [X] Start a PosgtreSQL server with docker

    ```bash
    docker run --name postgres -p 5432:5432 -e POSTGRES_DB=demo \
        -e POSTGRES_USER=demo -e POSTGRES_PASSWORD=demo --rm -it postgres
    ```

-   [X] Start a PosgtreSQL client with docker

    ```bash
    docker run --rm -it postgres psql -U demo \
        -h localhost \   # (1)!
        -p 9098    # (2)!
    ```

    1. The address of the proxy
    2. The port of the proxy since we route our traffic via the proxy

-   [X] Use the plugin with fault

    ```bash
    fault run --grpc-plugin http://localhost:50051 \   # (1)!
        --proxy "9098=psql://192.168.1.45:5432"   # (2)!
    ```

    1. Connect to the plugin
    2. Map a local proxy from port {==9098==} to the address of the database
       server {==192.168.1.45:5432==}. Obviously change the actual IP to the
       one matching your database. 

-   [X] Explore the plugin's behavior

    From the PostgreSQL client, you can now type a SQL query such as:

    ```sql
    select now();
    ```

    The plugin will echo the parsed messages. Something along the lines:

    ```python
    [('Query(0x51)', b'select now();\x00')]
    [('RowDescription', {'field_count': 1, 'fields': [{'name': '', 'table_oid': 24014711, 'column_attr': 0, 'type_oid': 0, 'type_len': 0, 'type_mod': 303104, 'format_code': 2303}]}), ('DataRow', {'field_count': 1, 'fields': [{'length': 29, 'value': b'2025-04-08 20:24:43.111173+00'}]}), ('CommandComplete', b'SELECT 1\x00'), ('ReadyForQuery', b'I')]
    ```

    As a next step, we could use [sqlglot](https://github.com/tobymao/sqlglot)
    to parse the query and, for instance, change it on the fly.

    The goal is to evaluate how the application reacts to variation from the
    database.