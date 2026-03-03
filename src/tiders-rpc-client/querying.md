# RPC Client Querying

The `Query` type defines what data to fetch from the RPC endpoint.

## Query Structure

```rust
use tiders_rpc_client::{Query, LogRequest, TransactionRequest, TraceRequest};
use tiders_rpc_client::{BlockFields, TransactionFields, LogFields, TraceFields};

let query = Query {
    from_block: 18_000_000,
    to_block: Some(18_001_000),
    logs: vec![LogRequest { ... }],
    transactions: vec![TransactionRequest { ... }],
    traces: vec![TraceRequest { ... }],
    fields: Fields {
        block: BlockFields { number: true, timestamp: true, ..Default::default() },
        transaction: TransactionFields { hash: true, ..Default::default() },
        log: LogFields { address: true, data: true, ..Default::default() },
        trace: TraceFields::default(),
    },
};
```

## Log Requests

Filter logs by address and/or topics:

```rust
LogRequest {
    address: vec![Address::from_str("0xdAC17F958D2ee523a2206206994597C13D831ec7")?],
    topic0: vec![topic0_hash],
    include_blocks: true,
}
```

## Transaction Requests

```rust
TransactionRequest {
    include_blocks: true,
    include_logs: true,
}
```

## Trace Requests

```rust
use tiders_rpc_client::TraceMethod;

TraceRequest {
    method: TraceMethod::TraceBlock,  // or DebugTraceBlockByNumber
    include_blocks: true,
}
```

## Field Selection

Select only the fields you need to minimize data transfer:

```rust
BlockFields {
    number: true,
    hash: true,
    timestamp: true,
    ..Default::default()  // all other fields false
}
```

## Response Format

The stream yields `ArrowResponse` items containing optional Arrow RecordBatches:

```rust
let mut stream = client.stream(query);

while let Some(response) = stream.next().await {
    let response = response?;
    if let Some(blocks) = response.blocks { /* Arrow RecordBatch */ }
    if let Some(transactions) = response.transactions { /* Arrow RecordBatch */ }
    if let Some(logs) = response.logs { /* Arrow RecordBatch */ }
    if let Some(traces) = response.traces { /* Arrow RecordBatch */ }
}
```

## Rust API Reference

See the [Query rustdoc](../api/tiders_rpc_client/struct.Query.html) for all fields.
