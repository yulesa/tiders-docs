# RPC Client Configuration

The `ClientConfig` struct controls how the RPC client connects to the provider and manages request behavior.

## Basic Configuration

```rust
use tiders_rpc_client::ClientConfig;

let config = ClientConfig::new("https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY");
```

## Configuration Options

| Option | Default | Description |
|---|---|---|
| `url` | (required) | The JSON-RPC endpoint URL |
| `bearer_token` | None | Optional bearer token for authentication |
| `batch_size` | Provider-dependent | Number of blocks to fetch per batch |
| `max_concurrent_requests` | Auto | Maximum parallel RPC calls (adaptive by default) |
| `retry_count` | 3 | Number of retries on failure |
| `retry_backoff_ms` | 1000 | Initial backoff delay between retries |

## Provider Compatibility

The RPC client works with any standard EVM JSON-RPC provider:

| Provider | Notes |
|---|---|
| Alchemy | Full support including traces |
| Infura | Full support (traces may require paid plan) |
| QuickNode | Full support |
| Local nodes (Geth, Erigon, Reth) | Full support; Erigon/Reth recommended for traces |
| Public endpoints | Works but may have rate limits |

## Adaptive Concurrency

The client automatically adjusts concurrency based on provider response times and error rates:

- Starts with conservative concurrency
- Increases parallelism when responses are fast
- Backs off when rate limits or errors are detected
- Different concurrency controls for blocks, logs, and traces

## Rust API Reference

See the [ClientConfig rustdoc](../api/tiders_rpc_client/struct.ClientConfig.html) for all fields and methods.
