# Transformation Steps

Steps are transformations applied to each batch of data before writing. They run in order and can decode, cast, encode, join, or apply custom logic.

## Built-in Steps

| Step | Description |
|---|---|
| `EVM_DECODE_EVENTS` | Decode EVM log events using an ABI signature |
| `SVM_DECODE_INSTRUCTIONS` | Decode Solana program instructions |
| `SVM_DECODE_LOGS` | Decode Solana program logs |
| `CAST` | Cast columns to specific types using a mapping |
| `CAST_BY_TYPE` | Cast all columns of one type to another |
| `HEX_ENCODE` | Hex-encode all binary columns |
| `BASE58_ENCODE` | Base58-encode all binary columns |
| `U256_TO_BINARY` | Convert U256 decimal columns to binary |
| `JOIN_BLOCK_DATA` | Join block fields into other tables |
| `JOIN_EVM_TRANSACTION_DATA` | Join EVM transaction fields |
| `JOIN_SVM_TRANSACTION_DATA` | Join SVM transaction fields |
| `SET_CHAIN_ID` | Add a chain_id column |
| `POLARS` | Custom transformation using Polars |
| `DATAFUSION` | Custom transformation using DataFusion |

## EVM Decode Events

Decodes raw log `data` and `topic` fields into typed columns using an ABI event signature:

```python
cc.Step(
    kind=cc.StepKind.EVM_DECODE_EVENTS,
    config=cc.EvmDecodeEventsConfig(
        event_signature="Transfer(address indexed from, address indexed to, uint256 amount)",
        output_table="transfers",
        allow_decode_fail=True,  # write null on decode failure instead of erroring
    ),
)
```

## Hex Encode

Converts all binary columns to hex-encoded strings for readability:

```python
cc.Step(
    kind=cc.StepKind.HEX_ENCODE,
    config=cc.HexEncodeConfig(),
)
```

## Cast By Type

Cast all columns of a given Arrow type to another type:

```python
import pyarrow as pa

cc.Step(
    kind=cc.StepKind.CAST_BY_TYPE,
    config=cc.CastByTypeConfig(
        from_type=pa.decimal256(76, 0),
        to_type=pa.decimal128(38, 0),
        allow_cast_fail=True,
    ),
)
```

## Custom Steps with Polars

```python
import polars as pl

def my_transform(data: dict[str, pl.DataFrame], ctx) -> dict[str, pl.DataFrame]:
    table = data["my_table"]
    table = table.filter(pl.col("value") > 0)
    return {"my_table": table}

cc.Step(
    kind=cc.StepKind.POLARS,
    config=cc.PolarsStepConfig(runner=my_transform),
)
```

## Custom Steps with DataFusion

```python
import datafusion

def my_sql_transform(session_ctx, data, ctx):
    result = session_ctx.sql("SELECT * FROM my_table WHERE value > 0")
    return {"my_table": result}

cc.Step(
    kind=cc.StepKind.DATAFUSION,
    config=cc.DataFusionStepConfig(runner=my_sql_transform),
)
```
