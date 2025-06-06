# Built-in Faults

<span class="f">fault</span> comes with a set of builtin faults. This page explores each fault
and how they get applied.

## Latency

**Definition**  
A network fault that delays traffic by a specified amount of time. Latency
commonly contributes to degraded user experience and is often used to simulate
real-world connection slowdowns.

### Key Characteristics

- **Application Side**
  The fault can be applied between different segments of a connection:

    - Client Side: Limits data moving from the client to the proxy.
    - Server Side: Caps data flow from the proxy to the upstream server.

- **Direction**
  The fault can be targeted to affect either the inbound traffic (ingress),
  outbound traffic (egress), or both, allowing you to simulate delays on one or
  both sides of a connection.

- **Timing:**  
    - **Once per connection**  
      Useful for request/response communication (e.g., HTTP). Applies a single
      delay on the first operation (read or write).  
    - **Per-operation**  
      For longer-lived connections (e.g., TCP tunneling, HTTP keep-alives),
      delay can be applied on every read/write operation rather than once.

- **Granularity:**  
    - Can be applied on **client** or **server** side, **ingress** or **egress**
      path.  
    - Expressed in **milliseconds**.

### Distributions

fault implements four different distributions.

#### Uniform Distribution

!!! quote inline end ""

    ```mermaid
    ---
    config:
        xyChart:
            showTitle: false
            width: 300
            height: 100
            xAxis:
                showTitle: false
                showLabel: false
                showAxisLine: false
                showTick: false
            yAxis:
                showTitle: false
                showLabel: false
                showAxisLine: false
                showTick: false

        themeVariables:
            xyChart:
                backgroundColor: "#1e2429"
                xAxisLineColor: "#bec3c6"
                yAxisLineColor: "#bec3c6"
    ---
    xychart-beta
        title "Uniform Distribution (min=5, max=20)"
        x-axis [ "5–8", "8–11", "11–14", "14–17", "17–20" ]
        y-axis "Frequency" 0 --> 300
        bar [ 180, 160, 190, 170, 195 ]
    ```

- **min**  
  The smallest possible delay in milliseconds.
- **max**  
  The largest possible delay in milliseconds.  
> A uniform random draw between `min` and `max` (inclusive).



#### Normal Distribution

!!! quote inline end ""

    ```mermaid
    ---
    config:
        xyChart:
            showTitle: false
            width: 300
            height: 100
            xAxis:
                showTitle: false
                showLabel: false
                showAxisLine: false
                showTick: false
            yAxis:
                showTitle: false
                showLabel: false
                showAxisLine: false
                showTick: false

        themeVariables:
            xyChart:
                backgroundColor: "#1e2429"
                xAxisLineColor: "#bec3c6"
                yAxisLineColor: "#bec3c6"
    ---
    xychart-beta
        title "Normal Distribution (mean=10, stddev=3)"
        x-axis [ "4–6", "6–8", "8–10", "10–12", "12–14" ]
        y-axis "Frequency" 0 --> 400
        bar [ 120, 280, 360, 280, 120 ]
    ```

- **mean**  
  The average delay in milliseconds around which most values cluster.
- **stddev**  
  Standard deviation, describing how spread out the delays are around the mean.  
> Smaller `stddev` values produce tighter clustering around `mean`, while larger
> values spread delays more widely.

#### Pareto Distribution

!!! quote inline end ""

    ```mermaid
    ---
    config:
        xyChart:
            showTitle: false
            width: 300
            height: 100
            xAxis:
                showTitle: false
                showLabel: false
                showAxisLine: false
                showTick: false
            yAxis:
                showTitle: false
                showLabel: false
                showAxisLine: false
                showTick: false

        themeVariables:
            xyChart:
                backgroundColor: "#1e2429"
                xAxisLineColor: "#bec3c6"
                yAxisLineColor: "#bec3c6"
    ---
    xychart-beta
        title "Pareto Distribution (shape=1.5, scale=3)"
        x-axis [ "3–6", "6–9", "9–12", "12–15", "15–18" ]
        y-axis "Frequency" 0 --> 150
        bar [ 80, 100, 120, 50, 20 ]
    ```

- **shape**  
  Governs how “heavy” the tail is. Lower `shape` implies more frequent extreme
  delays; higher `shape` yields fewer large spikes.
- **scale**  
  Minimum threshold (in milliseconds). Delays start at `scale` and can grow
  large based on the heavy tail.

#### Pareto Normal Distribution

!!! quote inline end ""

    ```mermaid
    ---
    config:
        xyChart:
            showTitle: false
            width: 300
            height: 100
            xAxis:
                showTitle: false
                showLabel: false
                showAxisLine: false
                showTick: false
            yAxis:
                showTitle: false
                showLabel: false
                showAxisLine: false
                showTick: false

        themeVariables:
            xyChart:
                backgroundColor: "#1e2429"
                xAxisLineColor: "#bec3c6"
                yAxisLineColor: "#bec3c6"
    ---
    xychart-beta
        title "Pareto-Normal Distribution (mean=10, stddev=3, shape=1.5, scale=3)"
        x-axis [ "4–6", "6–8", "8–10", "10–12", "12–14", "14–16", "16–18", "18–24", "24–40" ]
        y-axis "Frequency" 0 --> 200
        bar [ 20, 60, 130, 180, 160, 120, 80, 50, 30 ]
    ```

- **mean** and **stddev**  
  Define the normal portion of the distribution, where most delays cluster near
  `mean`.  
- **shape** and **scale**  
  Introduce a heavy-tailed component, allowing for occasional large spikes above
  the normal baseline.

## Jitter

**Definition**  
Jitter is a network fault that introduces random, unpredictable delays into
packet transmission. Unlike fixed latency, jitter fluctuates on a per-operation
basis, emulating the natural variance seen in real-world network conditions.
This can help reveal how well an application copes with irregular timing and
bursty network behavior.

### Key Characteristics

- **Per-Operation Application**
  Jitter is applied to individual operations (reads and/or writes) rather than
  as a one‑time delay for an entire connection. This accurately models scenarios
  where network delay fluctuates with each packet.

- **Application Side**
  The fault can be applied between different segments of a connection:

    - Client Side: Limits data moving from the client to the proxy.
    - Server Side: Caps data flow from the proxy to the upstream server.

- **Direction**
  The fault can be targeted to affect either the inbound traffic (ingress),
  outbound traffic (egress), or both, allowing you to simulate delays on one or
  both sides of a connection.

- **Amplitude**
  This parameter defines the maximum delay, expressed in milliseconds, that can
  be randomly applied to an operation. It sets the upper bound on how severe
  each individual delay can be.

- **Frequency**
  Frequency indicates how often the jitter fault is applied, measured in Hertz
  (the number of times per second). Higher frequencies simulate more frequent
  variability in delay.

## Bandwidth

**Definition**

Bandwidth is a network fault that simulates a limited throughput by capping
the rate at which data can be transmitted. In effect, it imposes a throttle on
the flow of information, causing delays when the amount of data exceeds the
defined maximum transfer rate.

### Key Characteristics

- **Application Side**
  The fault can be applied between different segments of a connection:

    - Client Side: Limits data moving from the client to the proxy.
    - Server Side: Caps data flow from the proxy to the upstream server.

- **Direction**
  The fault can be targeted to affect either the inbound traffic (ingress),
  outbound traffic (egress), or both, allowing you to simulate delays on one or
  both sides of a connection.

- **Rate Limit and Unit**
  The core of the bandwidth fault is its transfer rate—defined as a positive
  integer value paired with a unit. The unit (Bps, KBps, MBps, or GBps)
  specifies the scale of the limitation. In practice, this value represents the
  maximum number of bytes (or kilobytes, megabytes, etc.) that can be
  transmitted per second. When data exceeds the allowed rate, additional bytes
  are delayed, effectively throttling the connection.

## Blackhole

**Definition**
The Blackhole network fault causes packets to vanish—effectively discarding or
"dropping" the traffic. When this fault is enabled, data sent over the affected
network path is simply lost, simulating scenarios such as misconfigured routing,
severe network congestion, or complete link failure. This helps test how well an
application or service manages lost packets and timeouts.

### Key Characteristics

- **Application Side**
  The fault can be applied between different segments of a connection:

    - Client Side: Limits data moving from the client to the proxy.
    - Server Side: Caps data flow from the proxy to the upstream server.

- **Direction**
  The fault can be targeted to affect either the inbound traffic (ingress),
  outbound traffic (egress), or both, allowing you to simulate delays on one or
  both sides of a connection.

- **Fault Behavior**
  When active, the Blackhole simply discards the affected packets. There is no
  acknowledgment or error sent back to the sender. This mimics real-world
  conditions where faulty network paths silently drop traffic, often leading to
  connection timeouts and degraded performance.


## Packet Loss

**Definition**
Packet Loss is a network fault that randomly drops a certain percentage of
packets. In this mode, some packets are lost in transit instead of being
delivered to their destination. This fault simulates real-world conditions such
as unreliable networks, congestion, or hardware issues that cause intermittent
communication failures.

### Key Characteristics

- **Application Side**
  The fault can be applied between different segments of a connection:

    - Client Side: Limits data moving from the client to the proxy.
    - Server Side: Caps data flow from the proxy to the upstream server.

- **Direction**
  The fault can be targeted to affect either the inbound traffic (ingress),
  outbound traffic (egress), or both, allowing you to simulate delays on one or
  both sides of a connection.

- **Fault Behavior**
  The packet loss fault randomly discards packets. Unlike blackholing, which
  silently discards all packets on a given path, packet loss is typically
  configured to drop only a fraction of packets. This can create intermittent
  failures that test the application's ability to handle retransmissions,
  timeouts, or other compensatory mechanisms.

## HTTP Error

**Definition**
The HTTP Response fault intercepts HTTP requests and returns a predefined HTTP
error response immediately, without forwarding the request to the upstream
server. This fault simulates scenarios where a service deliberately returns an
error (e.g., due to misconfiguration or overload), enabling you to test how the
client and application behave when receiving error responses.


### Key Characteristics

- **Fault Enablement**
  When enabled, the proxy responds with an HTTP error response instead of
  passing the request through. This behavior bypasses any normal processing by
  the backend service.

- **Status Code and Body**

    - **HTTP Response Status**
      You can specify which HTTP status code to return (defaulting to 500).

    - **Optional Response Body**
      An optional HTTP body can be provided so that clients receive not only a
      status code but also explanatory content.
      These settings allow the simulation of different error scenarios (e.g.,
      404 for "Not Found", 503 for "Service Unavailable").

- **Trigger Probability**
  The fault is applied probabilistically based on a trigger probability between
  0.0 and 1.0 (default 1.0). A value less than 1.0 means that only a fraction of
  the requests will trigger the error response, enabling the simulation of
  intermittent errors rather than constant failure.

- **Impact on Communication**
  This fault terminates the normal request–response cycle by immediately
  returning the error response. It is useful in tests where you need to verify
  that error handling or failover mechanisms in your client application are
  functioning correctly.