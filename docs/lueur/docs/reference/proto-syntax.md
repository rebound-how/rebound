# Proxy Protocols

HTTP is one of the most common protocol used to communicate between services
or from the external world in your system. It stands to reason to widely focus
on that interface to build greater reliability.

We believe there is value to also explore the impact of network issues on
non-HTTP communication. For instance, how does your application deal with
latency when it access the database, its cache server, etc.

This is what lueur supports through TCP proxying.

## What is a TCP proxy?

A TCP proxy is a lueur proxy that listens on a given port for incoming
connections over the TCP protocol. When suhc a connection is made, the proxy
also connects to a remote endpoint. During the life of these connections, any
traffic received by the proxy is copied as-is and sent to the remote host.

The proxy applies any configured network faults on the stream.

### 

## Grammar

The proxy protocol grammar is a tiny DSL. Below is its EBNF grammar:

```ebnf

config     = left "=" right
left       = port
right      = hostport | proto_url
hostport   = host ":" port
proto_url  = protocol "://" host opt_port
opt_port   = ":" port | /* empty */
protocol   = "http" | "https" | "psql"
port       = digit { digit }
host       = char { char }
              (* a host is any nonempty string of characters that is not "=" or ":" *)
digit      = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
char       = any character except "=" and ":"
```

## Examples

Here are a few examples:

**Send traffic to Google**

```bash
--proxy-proto "9090=https://www.google.com"
```

**Send traffic to PostgreSQL**

```bash
--proxy-proto "9090=psql://my-db.default.svc:5432"
```
