# Ingest

The `tiders-ingest` crate handles data fetching from blockchain data providers. It provides a unified streaming interface regardless of the backend (HyperSync, SQD, or RPC).

## Python Usage

```python
from tiders_core.ingest import (
    ProviderConfig,
    ProviderKind,
    Query,
    QueryKind,
    start_stream,
)
```

### Provider Configuration

```python
provider = ProviderConfig(
    kind=ProviderKind.HYPERSYNC,   # or SQD, RPC
    url="https://eth.hypersync.xyz",
    stop_on_head=False,            # keep polling for new blocks
    batch_size=100,                # blocks per batch
)
```

### EVM Query

```python
from tiders_core.ingest import evm

query = Query(
    kind=QueryKind.EVM,
    params=evm.Query(
        from_block=18_000_000,
        to_block=18_001_000,
        logs=[evm.LogRequest(...)],
        transactions=[evm.TransactionRequest(...)],
        fields=evm.Fields(...),
    ),
)
```

### SVM Query

```python
from tiders_core.ingest import svm

query = Query(
    kind=QueryKind.SVM,
    params=svm.Query(
        from_block=330_000_000,
        instructions=[svm.InstructionRequest(...)],
        fields=svm.Fields(...),
    ),
)
```

## Rust API

See the [tiders_ingest rustdoc](../api/tiders_ingest/index.html) for the full Rust API.

The main entry point is `start_stream()`, which returns an async stream of `Result<RecordBatch>` items.
