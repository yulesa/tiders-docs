# Schemas

The `tiders-evm-schema` and `tiders-svm-schema` crates define the canonical Arrow schemas for blockchain data tables.

## EVM Schemas

Tables produced by EVM data sources:

| Table | Key Columns |
|---|---|
| `blocks` | `number`, `hash`, `parent_hash`, `timestamp`, `miner`, `gas_limit`, `gas_used`, `base_fee_per_gas`, `size`, `withdrawals` |
| `transactions` | `hash`, `from`, `to`, `value`, `gas_used`, `effective_gas_price`, `cumulative_gas_used`, `contract_address` |
| `logs` | `block_number`, `transaction_hash`, `log_index`, `address`, `topic0`..`topic3`, `data` |
| `traces` | `block_number`, `transaction_hash`, `trace_address`, `type`, `from`, `to`, `value`, `input`, `output` |

All binary fields (hashes, addresses) are stored as Arrow `Binary` type by default. Use the `HEX_ENCODE` step to convert them to readable strings.

## SVM Schemas

Tables produced by SVM (Solana) data sources:

| Table | Key Columns |
|---|---|
| `blocks` | `slot`, `hash`, `timestamp`, `parent_slot` |
| `transactions` | `block_slot`, `transaction_index`, `signature` |
| `instructions` | `block_slot`, `transaction_index`, `instruction_address`, `program_id`, `data`, `a0`..`a9` |

## Field Selection

You don't fetch all columns by default. Use the `Fields` types in your query to select only the columns you need:

```python
fields = ingest.evm.Fields(
    block=ingest.evm.BlockFields(number=True, timestamp=True),
    log=ingest.evm.LogFields(block_number=True, address=True, data=True),
)
```

This reduces network transfer, memory usage, and processing time.

## Rust API

- [tiders_evm_schema rustdoc](../api/tiders_evm_schema/index.html)
- [tiders_svm_schema rustdoc](../api/tiders_svm_schema/index.html)
