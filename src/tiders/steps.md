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

**Python**

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

**yaml**

```yaml
- kind: evm_decode_events
  config:
    event_signature: "Transfer(address indexed from, address indexed to, uint256 amount)"
    output_table: transfers       # default: decoded_logs
    input_table: logs             # default: logs
    allow_decode_fail: true       # default: false
    filter_by_topic0: false       # default: false
    hstack: true                  # default: true
```

## Hex Encode

Converts all binary columns to hex-encoded strings for readability:

**Python**

```python
cc.Step(
    kind=cc.StepKind.HEX_ENCODE,
    config=cc.HexEncodeConfig(),
)
```

**yaml**

```yaml
- kind: hex_encode
  config:
    tables: [transfers]   # optional — apply to specific tables only
    prefixed: true        # default: true — add 0x prefix
```

## Cast By Type

Cast all columns of a given Arrow type to another type:

**Python**

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

**yaml**

```yaml
- kind: cast_by_type
  config:
    from_type: "decimal256(76,0)"
    to_type: "decimal128(38,0)"
    allow_cast_fail: true
```

Supported type strings: `int8`–`int64`, `uint8`–`uint64`, `float16`–`float64`, `string`, `binary`, `bool`, `date32`, `date64`, `null`, `decimal128(p,s)`, `decimal256(p,s)`.

## SQL (yaml only)

Run DataFusion SQL queries against the in-memory tables. Results from `CREATE TABLE name AS ...` are stored under `name`; plain `SELECT` results are stored as `sql_result`.

**yaml**

```yaml
- kind: sql
  config:
    queries:
      - >
        CREATE TABLE enriched AS
        SELECT t.*, b.timestamp
        FROM transfers t
        JOIN blocks b ON b.number = t.block_number
```

## Custom Steps with Polars

**Python**

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

**yaml**

```yaml
- kind: python_file
  config:
    file: ./steps/my_step.py
    function: my_transform
    step_type: polars
```

## Custom Steps with DataFusion

**Python**

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

**yaml**

```yaml
- kind: python_file
  config:
    file: ./steps/my_step.py
    function: my_sql_transform
    step_type: datafusion
```
