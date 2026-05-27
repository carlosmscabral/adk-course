---
module: Detours
page: gRPC
title: gRPC — HTTP/2 + protobuf + generated stubs
estimated_minutes: 25
prereqs: []
concepts: [gRPC, HTTP-2, protobuf, streaming-rpc, channel, REST-comparison]
icon: 📡
---

[← Triggered from: 18_StreamingLive/06_VideoInput, 19_Internals]  [↑ Map](../MAP.md)

You are here: 🗺 Detours ▸ gRPC

> 🧭 **This is optional.** Take it if "Live uses gRPC under the hood" leaves you wanting more. 25 min. Comes back to module 18.

## What gRPC is, in one sentence

**gRPC is HTTP/2 + Protocol Buffers + a code generator that turns your `.proto` file into typed client and server stubs in your language.**

Three components, each pulling weight:

1. **HTTP/2** — multiplexed, binary, bidi streams on one TCP connection.
2. **Protocol Buffers** — compact, typed, schema-first serialization. See [[ProtocolBuffers]].
3. **Code generation** — `protoc` reads `service Foo { rpc Bar(...) returns (...); }` and emits a typed `FooClient` and `FooServicer` in Python, Go, Java, etc.

The combination gives you: type-checked RPCs, bidi streaming, server push, header compression, all on one TCP connection. The cost is more setup vs REST.

## The four RPC types

```
unary               : Request → Response          (like a regular function call)
server-streaming    : Request → stream Response   (server keeps pushing)
client-streaming    : stream Request → Response   (client keeps pushing)
bidirectional       : stream Request ↔ stream Response   (Live API!)
```

Gemini Live uses **bidirectional** streaming. Both sides send at any rate, in any order. The same TCP connection carries audio frames going up, audio frames coming down, control messages, transcript text — all multiplexed.

## Why one connection matters

HTTP/1.1 needs one TCP connection per outstanding request. If you wanted bidi audio over HTTP/1.1 you'd need two connections (one each way), with separate TCP slow-start, separate TLS handshakes, separate keepalive. That's hundreds of ms of avoidable latency.

HTTP/2 multiplexes **streams** on **one** TCP connection. Each stream has an ID; frames from different streams interleave. The audio-up stream and audio-down stream share the connection, share the TLS context, share the congestion window.

```
  TCP connection ────────────────────────────────────────────────────────
   ├─ stream 1 (call setup):     [header frame]
   ├─ stream 1 (audio up):       [data][data][data]...
   ├─ stream 1 (audio down):     [data][data][data]...
   ├─ stream 1 (transcript up):  [data]...
   └─ stream 1 (transcript down):[data]...
```

(All under one logical RPC = one HTTP/2 stream, with multiple "messages" within it. For multiple concurrent RPCs you'd have multiple HTTP/2 streams.)

## Channels — your connection pool

A gRPC **channel** is a long-lived logical connection to a host. Under the hood it manages 1 or more TCP connections and load-balances across them. **Create a channel once and reuse it** — never one channel per request.

```python
# DON'T
for query in queries:
    channel = grpc.insecure_channel("foo:50051")   # new TCP every time
    stub = MyServiceStub(channel)
    stub.Call(req)

# DO
channel = grpc.insecure_channel("foo:50051")       # once
stub = MyServiceStub(channel)
for query in queries:
    stub.Call(req)
```

This is one of the most common gRPC perf bugs in the wild.

## gRPC vs REST — when each wins

| | REST/JSON | gRPC |
|---|---|---|
| Discoverability | curl, browser, easy | needs stubs |
| Polyglot tooling | universal | protoc-supported langs only |
| Streaming | SSE one-way, awkward bidi | first-class bidi |
| Type safety | optional (OpenAPI) | mandatory (.proto) |
| Payload size | text, larger | binary, smaller |
| Browser-native | yes | no (needs gRPC-Web shim) |
| Latency | one request per call | streams on one connection |

**Pick REST** for: public APIs, browser frontends, simple CRUD.
**Pick gRPC** for: service-to-service, streaming, perf-critical, strong typing.

Live API is the canonical gRPC use case: bidi streaming + strict latency + binary audio data.

## Minimal Python client-streaming example

```protobuf
// chat.proto
syntax = "proto3";
service Chat {
  rpc SendBatch(stream Message) returns (Summary);
}
message Message { string text = 1; }
message Summary { int32 count = 1; }
```

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. chat.proto
```

```python
# client.py
import grpc, chat_pb2, chat_pb2_grpc

def messages():
    for txt in ["hi", "how are you", "bye"]:
        yield chat_pb2.Message(text=txt)

with grpc.insecure_channel("localhost:50051") as channel:
    stub = chat_pb2_grpc.ChatStub(channel)
    summary = stub.SendBatch(messages())
    print(summary.count)        # 3
```

Notice the client passes an **iterator** of `Message` objects. gRPC reads from it as the server reads — that's "client streaming." For bidi, both sides do this.

## Debugging Live gRPC

When something is wrong with a Live session, gRPC's trace logging is invaluable:

```bash
GRPC_TRACE=all GRPC_VERBOSITY=debug python your_live_app.py 2>&1 | less
```

You'll see TLS handshake, HTTP/2 frames, streams opening/closing. Filter to specific subsystems with `GRPC_TRACE=http,connectivity_state` etc.

## 🧪 Mini-exercise (no setup required)

Open a working bidi-demo session, set `GRPC_TRACE=all GRPC_VERBOSITY=info` before launching, and look for log lines like:

```
[transport] frame_type=DATA stream=1 length=3328
[transport] frame_type=DATA stream=1 length=2048
```

Each `DATA` frame is an audio chunk in flight. The stream ID stays the same because it's all one bidi RPC. That's the whole gRPC layer doing its job.

(If you don't have a bidi-demo running yet, skip this — you'll do it after page 08.)

## Back to module 18

- The `runner.run_live(...)` async iterator is **a bidirectional gRPC stream wrapped in Python's async syntax.** The `LiveRequestQueue.send_*` calls put frames onto the upload side of that stream; the `async for event` reads frames from the download side.
- This is also why `session_resumption` matters — a TCP/HTTP-2 connection that drops takes the whole RPC with it. Resumption lets you start a fresh RPC at the same logical position.

[← Back: 18_StreamingLive/06_VideoInput](../18_StreamingLive/06_VideoInput.md) · [Forward: [[ProtocolBuffers]]]  [↑ Map](../MAP.md)
