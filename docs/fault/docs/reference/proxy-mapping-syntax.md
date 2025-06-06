# Proxy Mapping

HTTP is one of the most common protocol used to communicate between services
or from the external world in your system. It stands to reason to widely focus
on that interface to build greater reliability. It is so ubiquitous that <span class="f">fault</span>
supports it by default.

However, we believe there is also great value to explore the impact of network
issues on non-HTTP communication. For instance, how does your application deal
with latency when it access the database, its cache server, etc.

This is what <span class="f">fault</span> supports through TCP proxying.

## What is a fault TCP proxy?

A TCP proxy is a <span class="f">fault</span> proxy that listens on a given port for incoming
connections over the TCP protocol. When such a connection is made, the proxy
also connects to a remote endpoint. During the life of these connections, any
traffic received by the proxy is copied as-is and sent to the remote host.

The proxy applies any configured network faults on the stream.

### Flow

``` mermaid
sequenceDiagram
  autonumber
  Client->>Proxy: Connect
  Proxy->>Remote: Connect
  Note left of Remote: Potentially encrypted over TLS
  loop Stream
      Client->>Remote: Stream data from client to remote via proxy. Apply all network faults
  end
  Client->>Proxy: Disonnect
  Proxy->>Remote: Disconnect
```

### Proxy Mapping

To stitch a client to its remote endpoint, you need a proxy mapping between
a local address for the proxy and a remote host. Once you have configured this
mapping, your client should use the address of the proxy instead of the
actual remote host.


### Encryption

When it comes to encryption, <span class="f">fault</span> supports a simple use case for now. If the
remote endpoint requires encryption over TLS, you can configure the mapping
accordingly and the proxy will establish a secured connection with the remote
host.

However, for now, the flow between the client and the proxy is in clear text.

A future release will let you setup the proxy to expect a secured connection
from the client.

## Grammar

The proxy mapping grammar is a tiny DSL. Below is its EBNF grammar:

```ebnf

config     = left "=" right
left       = port
right      = hostport | proto_url
hostport   = host ":" port
proto_url  = protocol "://" host opt_port
opt_port   = ":" port | /* empty */
protocol   = "http" | "https" | "psql" | "psqls" | "tls"
port       = digit { digit }
host       = char { char }
              (* a host is any nonempty string of characters that is not "=" or ":" *)
digit      = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
char       = any character except "=" and ":"
```

!!! note "The protocol is optional"

    When you map to a remote endpoint, you may be explicit about the L7 protocol
    that will transit. This is entirely optional and, for now, <span class="f">fault</span> does not
    interpret it beyond deciding if the communication between the proxy
    and the remote host should be encrypted.

    In a future version, <span class="f">fault</span> might use this information for more logic.

## Examples

Here are a few examples:

**Send traffic to Google via a local proxy on port 9090**

```bash
--proxy "9090=https://www.google.com"
```

**Send traffic to PostgreSQL via a local proxy on port 35432**

```bash
--proxy "35432=psql://my-db.default.svc:5432"
```
