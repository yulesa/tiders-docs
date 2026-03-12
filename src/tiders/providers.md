# Providers

Providers are the data sources that tiders fetches blockchain data from. Each provider connects to a different backend service.

## Available Providers

| Provider | EVM (Ethereum) | SVM (Solana) | Description |
|---|---|---|---|
| [HyperSync](https://docs.envio.dev/docs/HyperSync/overview) | Yes | No | High-performance indexed data |
| [SQD](https://docs.sqd.ai/) | Yes | Yes | Decentralized data network |
| RPC | Yes | No | Any standard EVM JSON-RPC endpoint |

## Configuration

All providers use `ProviderConfig` from `tiders_core.ingest`:

```python
from tiders_core.ingest import ProviderConfig, ProviderKind
```

### Common Parameters

These parameters are available for all providers:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `kind` | `ProviderKind` | — | Provider backend (`hypersync`, `sqd`, `rpc`) |
| `url` | `str` | None | Provider endpoint URL. If None, uses the provider's default |
| `bearer_token` | `str` | None | Authentication token for protected APIs |
| `stop_on_head` | `bool` | `false` | If true, stop when reaching the chain head; if false, keep polling indefinitely |
| `head_poll_interval_millis` | `int` | None | How frequently (ms) to poll for new blocks when streaming live data |
| `buffer_size` | `int` | None | Number of responses to buffer before sending to the consumer |
| `max_num_retries` | `int` | None | Maximum number of retries for failed requests |
| `retry_backoff_ms` | `int` | None | Delay increase between retries in milliseconds |
| `retry_base_ms` | `int` | None | Base retry delay in milliseconds |
| `retry_ceiling_ms` | `int` | None | Maximum retry delay in milliseconds |
| `req_timeout_millis` | `int` | None | Request timeout in milliseconds |

### RPC-only Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `batch_size` | `int` | None | Number of blocks fetched per batch |
| `compute_units_per_second` | `int` | None | Rate limit in compute units per second |
| `reorg_safe_distance` | `int` | None | Number of blocks behind head considered safe from chain reorganizations |
| `trace_method` | `str` | None | Trace API method: `"trace_block"` or `"debug_trace_block_by_number"` |

---

### HyperSync

**Python**

```python
provider = ProviderConfig(
    kind=ProviderKind.HYPERSYNC,
    url="https://eth.hypersync.xyz",
    bearer_token = HYPERSYNC_TOKEN
)
```

**yaml**

```yaml
provider:
  kind: hypersync
  url: ${PROVIDER_URL}
  bearer_token: ${HYPERSYNC_BEARER_TOKEN}   # optional
```

### SQD

**Python**

```python
provider = ProviderConfig(
    kind=ProviderKind.SQD,
    url="https://portal.sqd.dev/datasets/ethereum-mainnet",
)
```

**yaml**

```yaml
provider:
  kind: sqd
  url: ${PROVIDER_URL}
```

### RPC

Use any standard EVM JSON-RPC endpoint (Alchemy, Infura, QuickNode, local node, etc.):

**Python**

```python
provider = ProviderConfig(
    kind=ProviderKind.RPC,
    url="https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY",
)
```

**yaml**

```yaml
provider:
  kind: rpc
  url: ${PROVIDER_URL}
  stop_on_head: true                     # optional, default: false
  trace_method: trace_block              # optional — trace_block or debug_trace_block_by_number
```

The RPC provider uses [tiders-rpc-client](../tiders-rpc-client/overview.md) under the hood, which supports adaptive concurrency, retry logic, and streaming.

## Choosing a Provider

- **HyperSync** — fast EVM historical data, allow request filtering; requires API key
- **SQD** — fast, supports both EVM and SVM, allow request filtering; decentralized
- **RPC** — works with traditional RPC, don't allow request filtering; useful when other providers don't support your chain
