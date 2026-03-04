# RPC Client Querying

The `Query` type defines what data to fetch from the RPC endpoint.

## Query Structure

**Rust**

```rust
use tiders_rpc_client::{Query, LogRequest, TransactionRequest, TraceRequest};
use tiders_rpc_client::{Fields, BlockFields, TransactionFields, LogFields, TraceFields};

let query = Query {
    from_block: 18_000_000,
    to_block: Some(18_001_000),
    include_all_blocks: false,
    logs: vec![LogRequest { .. }],
    transactions: vec![TransactionRequest { .. }],
    traces: vec![TraceRequest { .. }],
    fields: Fields {
        block: BlockFields { number: true, timestamp: true, ..Default::default() },
        transaction: TransactionFields { hash: true, ..Default::default() },
        log: LogFields { address: true, data: true, ..Default::default() },
        trace: TraceFields::default(),
    },
};
```

**Python**

```python
from tiders_core import ingest

query = ingest.Query(
    kind=ingest.QueryKind.EVM,
    params=ingest.evm.Query(
        from_block=18_000_000,
        to_block=18_001_000,
        include_all_blocks=False,
        logs=[ingest.evm.LogRequest(...)],
        transactions=[ingest.evm.TransactionRequest(...)],
        traces=[ingest.evm.TraceRequest(...)],
        fields=ingest.evm.Fields(
            block=ingest.evm.BlockFields(number=True, timestamp=True),
            transaction=ingest.evm.TransactionFields(hash=True),
            log=ingest.evm.LogFields(address=True, data=True),
            trace=ingest.evm.TraceFields(),
        ),
    ),
)
```

| Option | Type | Default | Description |
|---|---|---|---|
| `from_block` | `u64` / `int` | `0` | First block to fetch (inclusive) |
| `to_block` | `Option<u64>` / `Optional[int]` | `None` | Last block to fetch (inclusive). `None` means stream up to the current head |
| `include_all_blocks` | `bool` | `false` | Fetch block headers even if no log/transaction/trace request is present |
| `logs` | `Vec<LogRequest>` / `list[LogRequest]` | `[]` | Log filter requests |
| `transactions` | `Vec<TransactionRequest>` / `list[TransactionRequest]` | `[]` | Transaction requests |
| `traces` | `Vec<TraceRequest>` / `list[TraceRequest]` | `[]` | Trace requests |
| `fields` | `Fields` | all `false` | Controls which columns appear in the output Arrow batches |

## Log Requests

Filter logs by address and/or topics. Multiple addresses and topics are OR'd together by the provider.

**Rust**

```rust
LogRequest {
    address: vec![Address::from_str("0xdAC17F958D2ee523a2206206994597C13D831ec7")?],
    topic0: vec![topic0_hash],
    include_blocks: true,
    ..Default::default()
}
```

**Python**

```python
ingest.evm.LogRequest(
    address=["0xdAC17F958D2ee523a2206206994597C13D831ec7"],
    topic0=[topic0_hash],
    include_blocks=True,
)
```

| Option | Type | Default | Description |
|---|---|---|---|
| `address` | `Vec<Address>` / `list[str]` | `[]` | Contract addresses to filter |
| `topic0` | `Vec<Topic>` / `list[str]` | `[]` | Event signature hashes |
| `topic1` | `Vec<Topic>` / `list[str]` | `[]` | First indexed parameter |
| `topic2` | `Vec<Topic>` / `list[str]` | `[]` | Second indexed parameter |
| `topic3` | `Vec<Topic>` / `list[str]` | `[]` | Third indexed parameter |
| `include_transactions` | `bool` | `false` | Also fetch transactions for the same block range |
| `include_transaction_traces` | `bool` | `false` | Also fetch traces for the same block range |
| `include_blocks` | `bool` | `false` | Also fetch block headers for the same block range |

Log filters (addresses and topics) cannot be combined with `include_*` flags on the same `LogRequest`. When `include_*` flags activate additional pipelines, those pipelines return unfiltered data for the full block range. To use multi-pipeline coordination remove the log filters and filter post-indexing.

## Transaction Requests

Activates the block pipeline to fetch blocks and transactions via `eth_getBlockByNumber`.

**Rust**

```rust
TransactionRequest {
    include_logs: true,
    include_blocks: true,
    ..Default::default()
}
```

**Python**

```python
ingest.evm.TransactionRequest(
    include_logs=True,
    include_blocks=True,
)
```

| Option | Type | Default | Description |
|---|---|---|---|
| `include_logs` | `bool` | `false` | Also fetch logs for the same block range |
| `include_traces` | `bool` | `false` | Also fetch traces for the same block range |
| `include_blocks` | `bool` | `false` | Also fetch block headers (always fetched by this pipeline, included for API compatibility) |

`TransactionRequest` also exposes filter fields (`from_`, `to`, `sighash`, `status`, `type_`, `contract_deployment_address`, `hash`), but these are **not supported** by the RPC client. `eth_getBlockByNumber` returns all transactions in a block with no server-side filtering. Setting any of these fields will produce an error. This functionality is only supported on other tiders clients (SQD, HyperSync). Ingest all transactions and filter post-indexing in your tiders (Python) pipeline or database instead.

## Trace Requests

Activates the trace pipeline to fetch internal call traces.

**Rust**

```rust
use tiders_rpc_client::TraceMethod;

TraceRequest {
    trace_method: TraceMethod::TraceBlock,  // or DebugTraceBlockByNumber
    include_blocks: true,
    ..Default::default()
}
```

**Python**

```python
ingest.evm.TraceRequest(
    include_blocks=True,
)
```

| Option | Type | Default | Description |
|---|---|---|---|
| `trace_method` | `TraceMethod` | `TraceBlock` | `TraceBlock` (Parity-style) or `DebugTraceBlockByNumber` (Geth-style) |
| `include_transactions` | `bool` | `false` | Also fetch transactions for the same block range |
| `include_transaction_logs` | `bool` | `false` | Also fetch logs for the same block range |
| `include_blocks` | `bool` | `false` | Also fetch block headers for the same block range |

`TraceRequest` also exposes filter fields (`from_`, `to`, `address`, `call_type`, `reward_type`, `type_`, `sighash`, `author`), but these are **not supported** by the RPC client. `trace_block` and `debug_traceBlockByNumber` return all traces in a block with no server-side filtering. Setting any of these fields will produce an error. This functionality is only supported on other tiders clients (SQD, HyperSync). Ingest all traces and filter post-indexing in your tiders (Python) pipeline or database instead.

## Field Selection

Select only the fields you need to minimize data transfer. When all flags are `false` (the default), the full schema is returned.

**Rust**

```rust
Fields {
    block: BlockFields { number: true, hash: true, timestamp: true, ..Default::default() },
    transaction: TransactionFields { hash: true, from: true, to: true, value: true, ..Default::default() },
    log: LogFields { address: true, data: true, topic0: true, ..Default::default() },
    trace: TraceFields::default(),
}
```

**Python**

```python
ingest.evm.Fields(
    block=ingest.evm.BlockFields(number=True, hash=True, timestamp=True),
    transaction=ingest.evm.TransactionFields(hash=True, from_=True, to=True, value=True),
    log=ingest.evm.LogFields(address=True, data=True, topic0=True),
    trace=ingest.evm.TraceFields(),
)
```

### Block Fields

| Field | Description |
|---|---|
| `number` | Block number |
| `hash` | Block hash |
| `parent_hash` | Parent block hash |
| `nonce` | Block nonce |
| `sha3_uncles` | SHA3 of uncle blocks |
| `logs_bloom` | Bloom filter for logs |
| `transactions_root` | Merkle root of transactions |
| `state_root` | Merkle root of state |
| `receipts_root` | Merkle root of receipts |
| `miner` | Block miner address |
| `difficulty` | Block difficulty |
| `total_difficulty` | Total chain difficulty |
| `extra_data` | Extra data field |
| `size` | Block size in bytes |
| `gas_limit` | Block gas limit |
| `gas_used` | Total gas used in block |
| `timestamp` | Block timestamp |
| `uncles` | Uncle block hashes |
| `base_fee_per_gas` | EIP-1559 base fee |
| `blob_gas_used` | EIP-4844 blob gas used |
| `excess_blob_gas` | EIP-4844 excess blob gas |
| `parent_beacon_block_root` | Parent beacon block root |
| `withdrawals_root` | Merkle root of withdrawals |
| `withdrawals` | Validator withdrawals |
| `l1_block_number` | L1 block number (L2 chains) |
| `send_count` | Send count (Arbitrum) |
| `send_root` | Send root (Arbitrum) |
| `mix_hash` | Mix hash |

### Transaction Fields

| Field | Description |
|---|---|
| `block_hash` | Block hash |
| `block_number` | Block number |
| `from` / `from_` | Sender address |
| `gas` | Gas provided |
| `gas_price` | Gas price |
| `hash` | Transaction hash |
| `input` | Input data (calldata) |
| `nonce` | Sender nonce |
| `to` | Recipient address |
| `transaction_index` | Index in block |
| `value` | Value transferred (wei) |
| `v` | Signature v |
| `r` | Signature r |
| `s` | Signature s |
| `max_priority_fee_per_gas` | EIP-1559 max priority fee |
| `max_fee_per_gas` | EIP-1559 max fee |
| `chain_id` | Chain ID |
| `cumulative_gas_used` | Cumulative gas used (receipt) |
| `effective_gas_price` | Effective gas price (receipt) |
| `gas_used` | Gas used by transaction (receipt) |
| `contract_address` | Created contract address (receipt) |
| `logs_bloom` | Bloom filter for logs (receipt) |
| `type_` | Transaction type |
| `root` | State root (pre-Byzantium receipt) |
| `status` | Success/failure (receipt) |
| `sighash` | Function selector (first 4 bytes of input) |
| `y_parity` | EIP-2930 y parity |
| `access_list` | EIP-2930 access list |
| `l1_fee` | L1 fee (Optimism) |
| `l1_gas_price` | L1 gas price (Optimism) |
| `l1_fee_scalar` | L1 fee scalar (Optimism) |
| `gas_used_for_l1` | Gas used for L1 (Arbitrum) |
| `max_fee_per_blob_gas` | EIP-4844 max blob fee |
| `blob_versioned_hashes` | EIP-4844 blob hashes |
| `deposit_nonce` | Deposit nonce (Optimism) |
| `blob_gas_price` | EIP-4844 blob gas price |
| `deposit_receipt_version` | Deposit receipt version (Optimism) |
| `blob_gas_used` | EIP-4844 blob gas used |
| `l1_base_fee_scalar` | L1 base fee scalar (Optimism Ecotone) |
| `l1_blob_base_fee` | L1 blob base fee (Optimism Ecotone) |
| `l1_blob_base_fee_scalar` | L1 blob base fee scalar (Optimism Ecotone) |
| `l1_block_number` | L1 block number (Optimism) |
| `mint` | Minted value (Optimism) |
| `source_hash` | Source hash (Optimism) |

Fields marked with **(receipt)** require `eth_getBlockReceipts` — the block pipeline fetches receipts automatically when any of these fields are selected.

### Log Fields

| Field | Description |
|---|---|
| `removed` | Whether log was removed due to reorg |
| `log_index` | Log index in block |
| `transaction_index` | Transaction index in block |
| `transaction_hash` | Transaction hash |
| `block_hash` | Block hash |
| `block_number` | Block number |
| `address` | Contract address that emitted the event |
| `data` | Non-indexed event data |
| `topic0` | Event signature hash |
| `topic1` | First indexed parameter |
| `topic2` | Second indexed parameter |
| `topic3` | Third indexed parameter |

### Trace Fields

| Field | Description |
|---|---|
| `from` / `from_` | Sender address |
| `to` | Recipient address |
| `call_type` | Call type (call, delegatecall, staticcall) |
| `gas` | Gas provided |
| `input` | Input data |
| `init` | Contract creation code |
| `value` | Value transferred |
| `author` | Block reward recipient |
| `reward_type` | Reward type (block, uncle) |
| `block_hash` | Block hash |
| `block_number` | Block number |
| `address` | Created contract address |
| `code` | Created contract code |
| `gas_used` | Gas used |
| `output` | Output data |
| `subtraces` | Number of subtraces |
| `trace_address` | Trace position in call tree |
| `transaction_hash` | Transaction hash |
| `transaction_position` | Transaction index in block |
| `type_` | Trace type (call, create, suicide, reward) |
| `error` | Error message if reverted |
| `sighash` | Function selector |
| `action_address` | Self-destruct address |
| `balance` | Self-destruct balance |
| `refund_address` | Self-destruct refund address |

## Response Format

The stream yields `ArrowResponse` items containing Arrow RecordBatches:

**Rust**

```rust
let mut stream = client.stream(query);

while let Some(response) = stream.next().await {
    let response = response?;
    // response.blocks — Arrow RecordBatch
    // response.transactions — Arrow RecordBatch
    // response.logs — Arrow RecordBatch
    // response.traces — Arrow RecordBatch
}
```

## Rust API Reference

See the [Query rustdoc](../api/tiders_rpc_client/struct.Query.html) for all fields.
