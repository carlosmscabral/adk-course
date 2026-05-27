---
module: Detours
page: ProtocolBuffers
title: Protocol Buffers — the schema and the wire format
estimated_minutes: 20
prereqs: []
concepts: [protobuf, schema, varint, tag, code-generation, schema-evolution]
icon: 📦
---

[← Triggered from: 18_StreamingLive (Live transport), 19_Internals]  [↑ Map](../MAP.md)

You are here: 🗺 Detours ▸ Protocol Buffers

> 🧭 **This is optional.** Take it if `.proto` files and `google.genai.types` feel mysterious. 20 min. Comes back to module 18.

## What protobuf is

**Protocol Buffers (protobuf, pb)** is Google's schema-first binary serialization format. You define your data types in a `.proto` file, run `protoc` to generate language-specific classes, and use those classes to serialize / parse compact binary messages.

It's what `gRPC` carries (see [[gRPC]]) and what `google.genai` SDK types are built on under the hood. Every `types.Content`, `types.Part`, `types.Blob` in your ADK code is a protobuf message with a wire format.

## A `.proto` file

```protobuf
// todo.proto
syntax = "proto3";

message Todo {
  int32  id        = 1;     // tag 1
  string title     = 2;     // tag 2
  bool   completed = 3;     // tag 3
  repeated string tags = 4; // tag 4 — list of strings
}
```

Three things matter:

- The **field type** (`int32`, `string`, `bool`, `repeated string`).
- The **field name** — only used by humans and generated code.
- The **field tag** (1, 2, 3, 4) — only used on the wire. **These are the contract.** Never reuse a tag; never change a tag's type.

## Code generation

```bash
$ protoc --python_out=. todo.proto
# emits todo_pb2.py
```

```python
>>> import todo_pb2
>>> t = todo_pb2.Todo(id=1, title="laundry", completed=False, tags=["home", "chore"])
>>> data = t.SerializeToString()
>>> len(data)
22
>>> data
b'\x08\x01\x12\x07laundry"\x04home"\x05chore'
```

22 bytes for a 4-field message. JSON for the same data is ~70 bytes. That's the compactness win.

```python
>>> t2 = todo_pb2.Todo()
>>> t2.ParseFromString(data)
>>> t2.title
'laundry'
```

## The wire format (just enough to read it)

Each field is **tag, wire-type, value**. Tag and wire-type are packed into a single varint. Wire-types:

| Wire type | What |
|-----------|------|
| 0 | varint (int32, bool, enum) |
| 1 | 64-bit (double, fixed64) |
| 2 | length-delimited (string, bytes, embedded message, repeated) |
| 5 | 32-bit (float, fixed32) |

Look at the bytes above:

- `\x08` = `(tag=1, wire=0)` = field 1 (id), varint. Next byte `\x01` = 1.
- `\x12` = `(tag=2, wire=2)` = field 2 (title), length-delimited. Next byte `\x07` = length 7. Next 7 bytes = `"laundry"`.
- Field 3 (completed) is `False` = default; **omitted from the wire**. proto3 doesn't send defaults.
- `"\x04home"` = tag 4, length 4, "home". Then `"\x05chore"`.

This is why protobuf is small: defaults are free, integers are varint-compressed (`1` is one byte; `127` is one byte; `128` is two bytes).

## Varints

A **varint** encodes an integer using as few bytes as needed. Each byte has 7 bits of value and 1 continuation bit. So small integers (the common case) take 1 byte; huge ones take up to 10.

```
1   = 0000 0001                      (1 byte)
300 = 1010 1100 0000 0010            (2 bytes; little-endian groups of 7)
```

Field tags are also varints. Tags 1-15 fit in a single byte (you get 4 bits of tag + 3 bits of wire-type + 1 continuation bit). Tags 16+ take 2 bytes. **So put hot fields in tags 1-15.** This is a Google internal style rule.

## Schema evolution — the two iron rules

protobuf is designed to evolve over years across many clients. Two rules:

1. **Never change a field's type or its tag.** If `id` was `int32` tag 1, it stays `int32` tag 1 forever.
2. **Never reuse a tag.** When you delete a field, **reserve** its tag:

```protobuf
message Todo {
  reserved 3;            // was `completed`
  reserved "completed";  // also reserve the name
  int32 id = 1;
  string title = 2;
  repeated string tags = 4;
  int32 priority = 5;    // new
}
```

Add new fields with new tags; mark old fields `reserved`. New code reads old messages (unknown fields are skipped); old code reads new messages (new fields it doesn't know are ignored). **Wire compatibility is forever** if you follow the rules.

## Why Vertex AI uses protobuf

- **Compact:** every saved millisecond on every audio frame matters at Live scale.
- **Typed:** prevents whole classes of bugs (field-name typos, type mismatches).
- **Language-neutral:** same `.proto` file generates Python, Go, Java, TS, Swift. The Python SDK, the Java SDK, and the Flutter SDK all speak the same wire format because they're all generated from the same schema.
- **Evolvable:** Google can add new fields to Gemini API messages without breaking any deployed client.

When you write `types.Content(parts=[types.Part(text="hi")])` in Python, you're constructing a generated protobuf class. When you call `runner.run_async()` it serializes that to wire bytes, ships over gRPC, the server parses it back into its own generated class.

## 🧪 Mini-exercise

Define a tiny Todo message and round-trip it.

```bash
mkdir pbdemo && cd pbdemo
cat > todo.proto <<'EOF'
syntax = "proto3";
message Todo {
  int32  id = 1;
  string title = 2;
  bool   completed = 3;
  repeated string tags = 4;
}
EOF
pip install protobuf grpcio-tools
python -m grpc_tools.protoc -I. --python_out=. todo.proto
```

```python
import todo_pb2
t = todo_pb2.Todo(id=42, title="buy milk", tags=["home"])
print(len(t.SerializeToString()))   # tiny number

raw = t.SerializeToString()
t2 = todo_pb2.Todo()
t2.ParseFromString(raw)
assert t2.title == "buy milk"
```

Now try printing the raw bytes and pick out the tags/lengths by hand. The exercise sticks better when you've decoded 15 bytes manually.

## Back to module 18

- The events streaming out of `runner.run_live(...)` are deserialized protobuf messages from the Live API. The Python `Event` you handle is the typed shape of that wire data.
- `event.content.parts[0].inline_data.data` for audio is a `bytes` field that came over as a length-delimited protobuf field — same wire shape as the `"laundry"` example above, just bigger.
- When you see `event.model_dump_json(...)` in `bidi-demo`, that's the Python SDK converting the protobuf object to JSON for the WebSocket — leaving the protobuf-on-gRPC world for the JSON-on-WebSocket world at the boundary.

[← Back: 18_StreamingLive](../18_StreamingLive/00_Overview.md) · [Back: [[gRPC]]]  [↑ Map](../MAP.md)
