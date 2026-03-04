# RPC Client Configuration

The `ClientConfig` struct controls how the RPC client connects to the provider and manages request behavior. In Python, configuration is done through `ProviderConfig` with `ProviderKind.RPC`.

## Basic Configuration

### Rust

```rust
use tiders_rpc_client::ClientConfig;

let config = ClientConfig::new("https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY");
```

### Python

```python
from tiders_core.ingest import ProviderConfig, ProviderKind

provider = ProviderConfig(
    kind=ProviderKind.RPC,
    url="https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY",
)
```

## Configuration Options

| Option | Type | Default | Description |
|---|---|---|---|
| `url` | `String` | (required) | The JSON-RPC endpoint URL |
| `bearer_token` | `Option<String>` | `None` | Optional bearer token for authentication |
| `max_num_retries` | `u32` | `5000` | Maximum number of retries for a single RPC call |
| `retry_backoff_ms` | `u64` | `1000` | Fixed per-retry delay in milliseconds (used by alloy's `RetryBackoffLayer`) |
| `retry_base_ms` | `u64` | `300` | Base delay for exponential backoff (used by per-block retry loops) |
| `retry_ceiling_ms` | `u64` | `10000` | Maximum delay for exponential backoff (used by per-block retry loops) |
| `req_timeout_millis` | `u64` | `30000` | Per-request HTTP timeout in milliseconds |
| `compute_units_per_second` | `Option<u64>` | `None` | Compute-unit rate limit for alloy's `RetryBackoffLayer` |
| `batch_size` | `Option<usize>` | `None` | Initial number of blocks per batch in simple pipeline mode; Response size (in blocks) in multi-pipeline mode (impact memory usage).  |
| `trace_method` | `Option<TraceMethod>` | `None` | Override the trace method (`trace_block` or `debug_trace_block_by_number`) |
| `stop_on_head` | `bool` | `false` | Stop the stream after reaching the chain head instead of entering live-polling mode |
| `head_poll_interval_millis` | `u64` | `1000` | How often to poll for new blocks during live mode, in milliseconds |
| `buffer_size` | `usize` | `10` | Bounded channel capacity for the `ArrowResponse` stream |
| `reorg_safe_distance` | `u64` | `0` | Number of blocks behind the head to stay, to avoid reorged data |

## Provider Compatibility

The RPC client works with any standard EVM JSON-RPC provider:

| Provider | Notes |
|---|---|
| Alchemy | Full support including traces |
| Infura | Full support (traces may require paid plan) |
| QuickNode | Full support |
| Local nodes (Geth, Erigon, Reth) | Full support; Erigon/Reth recommended for traces |
| Public endpoints | Works but may have rate limits |

## Rust API Reference

See the [ClientConfig rustdoc](../api/tiders_rpc_client/struct.ClientConfig.html) for all fields and methods.
