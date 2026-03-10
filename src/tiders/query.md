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

**Python**

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

**yaml**

```yaml
query:
  kind: evm
  from_block: 18000000
  to_block: 18001000        # optional
  logs: [...]
  transactions: [...]
  fields: {...}
```

### Log Requests

Filter logs by contract address and/or topic:

**Python**

```python
evm.LogRequest(
    address=["0xdAC17F958D2ee523a2206206994597C13D831ec7"],  # optional
    topic0=[evm_signature_to_topic0("Transfer(address,address,uint256)")],
    include_blocks=True,   # also fetch related blocks
)
```

**yaml**

```yaml
query:
  kind: evm
  logs:
    - address: "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # optional
      topic0: "Transfer(address,address,uint256)"             # signature or 0x hex hash
      include_blocks: true
```

### Transaction Requests

**Python**

```python
evm.TransactionRequest(
    include_blocks=True,   # also fetch related blocks
    include_logs=True,     # also fetch related logs
)
```

**yaml**

```yaml
query:
  kind: evm
  transactions:
    - include_blocks: true
      include_logs: true
```

### Field Selection

Select only the columns you need:

**Python**

```python
evm.Fields(
    block=evm.BlockFields(number=True, timestamp=True, hash=True),
    transaction=evm.TransactionFields(hash=True, from_=True, to=True, value=True),
    log=evm.LogFields(block_number=True, address=True, topic0=True, data=True),
)
```

**yaml**

```yaml
query:
  kind: evm
  fields:
    block: [number, timestamp, hash]
    transaction: [hash, from, to, value]
    log: [block_number, address, topic0, data]
```

Fields can also be specified as a `{name: true/false}` mapping:

```yaml
fields:
  log:
    address: true
    data: true
    block_number: true
```

## SVM Queries

**Python**

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

**yaml**

```yaml
query:
  kind: svm
  from_block: 330000000
  to_block: 330001000
  include_all_blocks: true
  instructions:
    - program_id: ["JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"]
      discriminator: ["0xe445a52e51cb9a1d40c6cde8260871e2"]
      include_transactions: true
  fields:
    instruction: [block_slot, program_id, data]
    block: [hash, timestamp]
    transaction: [signature]
```
