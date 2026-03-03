# Providers

Providers are the data sources that tiders fetches blockchain data from. Each provider connects to a different backend service.

## Available Providers

| Provider | EVM (Ethereum) | SVM (Solana) | Description |
|---|---|---|---|
| [HyperSync](https://docs.envio.dev/docs/HyperSync/overview) | Yes | No | High-performance indexed data |
| [SQD](https://docs.sqd.ai/) | Yes | Yes | Decentralized data network |
| RPC | Yes | No | Any standard JSON-RPC endpoint |

## Configuration

All providers use `ProviderConfig` from `tiders_core.ingest`:

```python
from tiders_core.ingest import ProviderConfig, ProviderKind
```

### HyperSync

```python
provider = ProviderConfig(
    kind=ProviderKind.HYPERSYNC,
    url="https://eth.hypersync.xyz",
)
```

### SQD

```python
# EVM
provider = ProviderConfig(
    kind=ProviderKind.SQD,
    url="https://portal.sqd.dev/datasets/ethereum-mainnet",
)

# SVM (Solana)
provider = ProviderConfig(
    kind=ProviderKind.SQD,
    url="https://portal.sqd.dev/datasets/solana-mainnet",
)
```

### RPC

Use any standard EVM JSON-RPC endpoint (Alchemy, Infura, QuickNode, local node, etc.):

```python
provider = ProviderConfig(
    kind=ProviderKind.RPC,
    url="https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY",
    stop_on_head=True,   # stop when reaching chain head
    batch_size=10,        # number of blocks per batch
)
```

The RPC provider uses [tiders-rpc-client](../tiders-rpc-client/overview.md) under the hood, which supports adaptive concurrency, retry logic, and streaming.

## Choosing a Provider

- **HyperSync** — fastest for EVM historical data; requires no API key
- **SQD** — supports both EVM and SVM; decentralized
- **RPC** — works with any endpoint; useful when other providers don't support your chain
