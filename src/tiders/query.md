# Query

The query defines what blockchain data to fetch: the block range, which tables to include, what filters to apply, and which fields to select.

## Structure

```python
from tiders_core.ingest import Query, QueryKind
```

A query has:
- **`kind`** — `QueryKind.EVM` or `QueryKind.SVM`
- **`params`** — chain-specific query parameters

## EVM Queries

```python
from tiders_core.ingest import evm

query = Query(
    kind=QueryKind.EVM,
    params=evm.Query(
        from_block=18_000_000,          # required
        to_block=18_001_000,            # optional (defaults to chain head)
        logs=[...],                     # optional log filters
        transactions=[...],            # optional transaction filters
        fields=evm.Fields(...),        # required field selection
    ),
)
```

### Log Requests

Filter logs by contract address and/or topic:

```python
evm.LogRequest(
    address=["0xdAC17F958D2ee523a2206206994597C13D831ec7"],  # optional
    topic0=[evm_signature_to_topic0("Transfer(address,address,uint256)")],
    include_blocks=True,   # also fetch related blocks
)
```

### Transaction Requests

```python
evm.TransactionRequest(
    include_blocks=True,   # also fetch related blocks
    include_logs=True,     # also fetch related logs
)
```

### Field Selection

Select only the columns you need:

```python
evm.Fields(
    block=evm.BlockFields(number=True, timestamp=True, hash=True),
    transaction=evm.TransactionFields(hash=True, from_=True, to=True, value=True),
    log=evm.LogFields(block_number=True, address=True, topic0=True, data=True),
)
```

## SVM Queries

```python
from tiders_core.ingest import svm

query = Query(
    kind=QueryKind.SVM,
    params=svm.Query(
        from_block=330_000_000,
        to_block=330_001_000,
        include_all_blocks=True,
        instructions=[
            svm.InstructionRequest(
                program_id=["JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"],
                discriminator=["0xe445a52e51cb9a1d40c6cde8260871e2"],
                include_transactions=True,
            )
        ],
        fields=svm.Fields(
            instruction=svm.InstructionFields(
                block_slot=True, program_id=True, data=True,
            ),
            block=svm.BlockFields(hash=True, timestamp=True),
            transaction=svm.TransactionFields(signature=True),
        ),
    ),
)
```
