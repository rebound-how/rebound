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
