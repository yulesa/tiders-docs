# RPC Client Overview

`tiders-rpc-client` is a Rust library for fetching EVM blockchain data from any standard JSON-RPC endpoint and converting it to Apache Arrow format.

Unlike specialized providers (HyperSync, SQD), the RPC client works with **any** Ethereum-compatible JSON-RPC endpoint — Alchemy, Infura, QuickNode, local nodes, or any other provider.

## Data Types

The client can fetch four types of blockchain data:

| Data Type | RPC Methods |
|---|---|
| Blocks | `eth_getBlockByNumber` |
| Transactions | via block data or `eth_getBlockReceipts` |
| Logs | `eth_getLogs` |
| Traces | `trace_block` or `debug_traceBlockByNumber` |

## Key Features

- **Streaming** — data is returned as a stream of Arrow RecordBatches
- **Adaptive concurrency** — automatically adjusts parallelism based on provider response times
- **Retry logic** — built-in error recovery with exponential backoff
- **Block range fallback** — splits large `eth_getLogs` ranges when providers reject them
- **Field selection** — fetch only the columns you need

## Usage via tiders (Python)

The simplest way to use the RPC client is through the tiders Python SDK:

```python
from tiders_core.ingest import ProviderConfig, ProviderKind

provider = ProviderConfig(
    kind=ProviderKind.RPC,
    url="https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY",
    stop_on_head=True,
    batch_size=10,
)
```

See the [RPC pipeline example](../tiders/examples/rpc_pipeline.md) for a complete working example.

## Usage as a Rust Library

```rust
use tiders_rpc_client::{Client, ClientConfig, Query};

let config = ClientConfig::new("https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY");
let client = Client::new(config);
let mut stream = client.stream(query);

while let Some(response) = stream.next().await {
    let response = response?;
    // response.blocks, response.transactions, response.logs, response.traces
}
```

## Rust API Reference

See the [tiders_rpc_client rustdoc](../api/tiders_rpc_client/index.html) for the full API.
