# ERC-20 Transfers (EVM)

This example fetches all ERC-20 `Transfer` events from Ethereum, decodes them, joins with block timestamps, and writes to DuckDB.

**Source:** [examples/erc20_custom.py](https://github.com/yulesa/tiders/blob/main/examples/erc20_custom.py)

## Run

```bash
uv run examples/erc20_custom.py --provider hypersync
# or
uv run examples/erc20_custom.py --provider sqd
```

## What It Does

1. **Queries** all logs matching the `Transfer(address,address,uint256)` topic
2. **Decodes** the raw log data into `from`, `to`, and `amount` columns
3. **Joins** transfer data with block timestamps using DataFusion
4. **Hex-encodes** binary fields for readability
5. **Casts** `decimal256` to `decimal128` (DuckDB compatibility)
6. **Writes** to a DuckDB database

## Key Code

### Query — fetch Transfer logs

```python
query = ingest.Query(
    kind=ingest.QueryKind.EVM,
    params=ingest.evm.Query(
        from_block=from_block,
        logs=[
            ingest.evm.LogRequest(
                topic0=[evm_signature_to_topic0("Transfer(address,address,uint256)")],
                include_blocks=True,
            )
        ],
        fields=ingest.evm.Fields(
            block=ingest.evm.BlockFields(number=True, timestamp=True),
            log=ingest.evm.LogFields(
                block_number=True, transaction_hash=True, log_index=True,
                address=True, topic0=True, topic1=True, topic2=True, topic3=True, data=True,
            ),
        ),
    ),
)
```

### Steps — decode, join, encode, cast

```python
steps = [
    cc.Step(
        kind=cc.StepKind.EVM_DECODE_EVENTS,
        config=cc.EvmDecodeEventsConfig(
            event_signature="Transfer(address indexed from, address indexed to, uint256 amount)",
            output_table="transfers",
            allow_decode_fail=True,
        ),
    ),
    cc.Step(
        kind=cc.StepKind.DATAFUSION,
        config=cc.DataFusionStepConfig(runner=join_data),
    ),
    cc.Step(kind=cc.StepKind.HEX_ENCODE, config=cc.HexEncodeConfig()),
    cc.Step(
        kind=cc.StepKind.CAST_BY_TYPE,
        config=cc.CastByTypeConfig(
            from_type=pa.decimal256(76, 0),
            to_type=pa.decimal128(38, 0),
            allow_cast_fail=True,
        ),
    ),
]
```

## Output

```bash
duckdb data/transfers.db
```

```sql
SELECT block_number, transaction_hash, "from", "to", amount
FROM transfers
LIMIT 5;
```
