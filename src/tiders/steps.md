# Transformation Steps

Transformation steps are built-in processing operations that are applied sequentially during pipeline execution. They run in order and can decode, cast, encode, join, or apply custom logic.

Here's an overview of how transformation steps work:

1. Select Step: Each transformation step defines a series of operations. This can range from data validation, decoding, encoding, and joining data, to custom transformations.
2. Step Configuration: Each step has a configuration object that defines input parameters and/or modifies behavior. For example, `EvmDecodeEventsConfig` requires an `event_signature` and has configs for horizontally stacking raw and decoded columns, not stopping on failed rows, and naming the output table.
3. Process Flow: Steps are executed in the order they are provided. After each step, the data is updated, and the transformed data is passed to the next step in the pipeline.

## Built-in Steps

| Step | yaml | Description |
|---|---|---|
| `EVM_DECODE_EVENTS` | `evm_decode_events` | Decode EVM log events using an ABI signature |
| `SVM_DECODE_INSTRUCTIONS` | `svm_decode_instructions` | Decode Solana program instructions |
| `SVM_DECODE_LOGS` | `svm_decode_logs` | Decode Solana program logs |
| `CAST` | `cast` | Cast specific columns to new types |
| `CAST_BY_TYPE` | `cast_by_type` | Cast all columns of one Arrow type to another |
| `HEX_ENCODE` | `hex_encode` | Hex-encode all binary columns |
| `BASE58_ENCODE` | `base58_encode` | Base58-encode all binary columns |
| `U256_TO_BINARY` | `u256_to_binary` | Convert U256 decimal columns to binary |
| `JOIN_BLOCK_DATA` | `join_block_data` | Join block fields into other tables |
| `JOIN_EVM_TRANSACTION_DATA` | `join_evm_transaction_data` | Join EVM transaction fields into other tables |
| `JOIN_SVM_TRANSACTION_DATA` | `join_svm_transaction_data` | Join SVM transaction fields into other tables |
| `SET_CHAIN_ID` | `set_chain_id` | Add a constant `chain_id` column to all tables |
| `POLARS` | — | Custom transformation using Polars DataFrames |
| `PANDAS` | — | Custom transformation using Pandas DataFrames |
| `DATAFUSION` | — | Custom transformation using DataFusion |
| — | `python_file` | Load a custom Polars or DataFusion function from a .py file (yaml only) |
| — | `sql` | Run DataFusion SQL queries (yaml only) |

---

## EVM Decode Events

Decodes raw log `data` and `topic` fields into typed columns using an ABI event signature.

**Python**

```python
cc.Step(
    kind=cc.StepKind.EVM_DECODE_EVENTS,
    config=cc.EvmDecodeEventsConfig(
        event_signature="Transfer(address indexed from, address indexed to, uint256 amount)",
        output_table="token_transfers",   # optional — name of the output table for decoded results, default: "decoded_logs"
        input_table="logs",               # optional — name of the input table to decode, default: "logs"
        allow_decode_fail=True,           # optional — when True rows that fails are nulls values instead of raising an error, default: False
        filter_by_topic0=False,           # optional — when True only rows whose ``topic0`` matches the event topic0 are decoded, default: False
        hstack=True,                      # optional — when True decoded columns are horizontally stacked with the input columns, default: True input columns
    ),
)
```

**yaml**

```yaml
- kind: evm_decode_events
  config:
    event_signature: "Transfer(address indexed from, address indexed to, uint256 amount)"
    output_table: transfers       # optional, default: decoded_logs
    input_table: logs             # optional, default: logs
    allow_decode_fail: false      # optional, default: false
    filter_by_topic0: false       # optional, default: false
    hstack: true                  # optional, default: true
```

---

## SVM Decode Instructions

Decodes raw Solana instruction data into structured columns using an Anchor/Borsh instruction signature.

**Python**

```python
from tiders_core.svm_decode import InstructionSignature

cc.Step(
    kind=cc.StepKind.SVM_DECODE_INSTRUCTIONS,
    config=cc.SvmDecodeInstructionsConfig(
        instruction_signature=InstructionSignature(...),
        output_table="decoded_instructions",  # optional — name of the input table to decode, default: "decoded_instructions"
        input_table="instructions",           # optional — name of the input table to decode, default: "instructions"
        allow_decode_fail=False,              # optional — when True, rows that fails are nulls values instead of raising an error, default: False
        filter_by_discriminator=False,        # optional — when True, only rows whose data starting bytes matches the event topic0 are decoded, default: False
        hstack=True,                          # optional — when True, decoded columns are horizontally stacked with the input columns, default: True
    ),
)
```

**yaml**

```yaml
- kind: svm_decode_instructions
  config:
    instruction_signature: {...}               # required
    output_table: decoded_instructions         # optional, default: "decoded_instructions"
    input_table: instructions                  # optional, default: "instructions"
    allow_decode_fail: false                   # optional, default: false
    filter_by_discriminator: false             # optional, default: false
    hstack: true                               # optional, default: true
```

### Instruction Signature

Signatures objects serve as decoding blueprints: they describe the expected structure of an instruction — including the name, type, and length of each parameter — allowing the pipeline to parse and interpret the raw byte data reliably.

Users can construct these signatures by gathering information from a variety of sources:

- Published IDLs (when available)
- Program source code (typically in Rust)
- Manual inspection of raw instructions on a Solana explorer

Here's an example of an instruction signature for decoding Jupiter swap instructions. We'll break down each part below:

```python
instruction_signature = InstructionSignature(
    discriminator="0xe445a52e51cb9a1d40c6cde8260871e2",
    params=[
        ParamInput(
            name="Amm",
            param_type=FixedArray(DynType.U8, 32),
        ),
        ParamInput(
            name="InputMint",
            param_type=FixedArray(DynType.U8, 32),
        ),
        ParamInput(
            name="InputAmount",
            param_type=DynType.U64,
        ),
        ParamInput(
            name="OutputMint",
            param_type=FixedArray(DynType.U8, 32),
        ),
        ParamInput(
            name="OutputAmount",
            param_type=DynType.U64,
        ),
    ],
    accounts_names=[],
)
```

**Discriminators**

A discriminator is a fixed sequence of bytes at the beginning of serialized data that identifies which instruction, struct, or event the data represents. During decoding, the discriminator matches raw data to the correct signature definition.

Discriminators are one of the most challenging parts to reverse-engineer because Solana has no standard for defining them. Here are some common patterns observed in real-world programs:

- Sequential values: Some programs use simple, ordered values (e.g., 0x00, 0x01, 0x02, ...) as discriminators.
- Anchor conventions: Anchor programs typically use the first 8 bytes of the SHA-256 hash of a struct name as the discriminator, ensuring uniqueness.
- Nested Anchor logs: Some Anchor-based programs use a two-level discriminator — the first 8 bytes identify a CPI log instruction, and the next 8 bytes identify a specific data structure inside the log (for a total of 16 bytes).
- Completely custom formats: Some programs define arbitrarily structured discriminators that don't follow any public pattern.

If you can reliably identify a particular instruction from observed transactions, you may be able to deduce its discriminator by finding repeated byte sequences at the start of the instruction data.

**Params**

The `params` field in the signature defines the expected values within the instruction data — in the exact order they appear. Each param can include a name, a type, and in the case of composite types, a list of fields or variants. These parameters are ordered and interpreted sequentially during decoding.

Supported types include:

- Primitives: Uint, Int, and Bool
- Complex types:
    - FixedArray: A fixed-length array of another type (e.g., Public keys, for example, are 32 bytes (or u8) [u8; 32].)
    - Array: A dynamic-length array. Data are prefixed with a length indicator to determine how many elements to decode.
    - Struct: A composite of keys - value types (like a dictionary)
    - Enum: A type representing one of several variants. Variant may optionally carry its own nested value.
    - Option: A nullable value that either holds a nested type or is empty.

All complex types can be nested arbitrarily — for example, an array of structs, an option of an enum, or a struct containing other structs.

**Accounts Names**

In Solana, each instruction includes a list of accounts it interacts with, passed as a separate data structure from the instruction data itself. The accounts_names field allows you to assign meaningful names to these account indices, making decoded output easier to read and analyze.

While the decoder doesn't interpret account data contents, having named accounts helps clarify the role each address plays in the instruction (e.g., "user", "token_account", "vault", etc.).

---

## SVM Decode Logs

Decodes raw Solana program log entries into structured columns using a log signature definition. Logs signatures works the same way as [instructions signatures](steps.md#instruction-signature).

**Python**

```python
from tiders_core.svm_decode import LogSignature

cc.Step(
    kind=cc.StepKind.SVM_DECODE_LOGS,
    config=cc.SvmDecodeLogsConfig(
        log_signature=LogSignature(...),
        output_table="decoded_logs",   # optional — when True rows that fails are nulls values instead of raising an error, default: False
        input_table="logs",            # optional — name of the input table to decode, default: "logs"
        allow_decode_fail=False,       # optional — when True rows that fails are nulls values instead of raising an error, default: False
        hstack=True,                   # optional — when True decoded columns are horizontally stacked with the input columns, default: True
    ),
)
```

**yaml**

```yaml
- kind: svm_decode_logs
  config:
    log_signature: {...}               # required
    output_table: decoded_logs         # optional, optional, default: "decoded_logs"
    input_table: logs                  # optional, optional, default: "logs"
    allow_decode_fail: false           # optional, optional, default: false
    hstack: true                       # optional, optional, default: true
```

---

## Cast

Casts specific columns in a table to new Arrow data types.

**Python**

```python
import pyarrow as pa

cc.Step(
    kind=cc.StepKind.CAST,
    config=cc.CastConfig(
        table_name="transfers",  # required — the name of the table whose columns should be cast.
        mappings={               # required — a mapping of column name to target pyarrow.DataType
            "value": pa.decimal128(38, 0),
            "block_number": pa.int64(),
        },
        allow_cast_fail=False,   # optional — When True, values that cannot be cast are set to null instead of raising an error, default: False
    ),
)
```

**yaml**

```yaml
- kind: cast
  config:
    table_name: transfers          # required
    mappings:                      # required — column name to Arrow type
      value: "decimal128(38,0)"
      block_number: int64
    allow_cast_fail: false         # optional, default: false
```

Supported type strings: `int8`–`int64`, `uint8`–`uint64`, `float16`–`float64`, `string`, `binary`, `bool`, `date32`, `date64`, `null`, `decimal128(p,s)`, `decimal256(p,s)`.

---

## Cast By Type

Casts all columns of a given Arrow type to a different type, across every table.

**Python**

```python
import pyarrow as pa

cc.Step(
    kind=cc.StepKind.CAST_BY_TYPE,
    config=cc.CastByTypeConfig(
        from_type=pa.decimal256(76, 0),
        to_type=pa.decimal128(38, 0),
        allow_cast_fail=False,   # default: false
    ),
)
```

**yaml**

```yaml
- kind: cast_by_type
  config:
    from_type: "decimal256(76,0)"   # required — the source pyarrow.DataType to match.
    to_type: "decimal128(38,0)"     # required — the target pyarrow.DataType to cast
    allow_cast_fail: false          # optional, default: false
```

Supported type strings: `int8`–`int64`, `uint8`–`uint64`, `float16`–`float64`, `string`, `binary`, `bool`, `date32`, `date64`, `null`, `decimal128(p,s)`, `decimal256(p,s)`.

---

## Hex Encode

Converts all binary columns to hex-encoded strings for readability.

**Python**

```python
cc.Step(
    kind=cc.StepKind.HEX_ENCODE,
    config=cc.HexEncodeConfig(
        tables=["transfers"],   # default: None — apply to all tables
        prefixed=True,          # default: true — add 0x prefix
    ),
)
```

**yaml**

```yaml
- kind: hex_encode
  config:
    tables: [transfers]   # optional — list of table names to process. When ``None``, all tables in the data dictionary are processed, default: None
    prefixed: true        # optional — When True, output strings are "0x"-prefixed, default: True

```

---

## Base58 Encode

Converts all binary columns to Base58-encoded strings, used for Solana public keys and signatures.

**Python**

```python
cc.Step(
    kind=cc.StepKind.BASE58_ENCODE,
    config=cc.Base58EncodeConfig(
        tables=["instructions"],   # optional — list of table names to process. When ``None``, all tables in the data dictionary are processed, default: None
    ),
)
```

**yaml**

```yaml
- kind: base58_encode
  config:
    tables: [instructions]   # optional — apply to specific tables only; default: all tables
```

---
<!-- 
## U256 To Binary

Converts `Decimal256` columns (including those nested in structs and lists) to a fixed-size binary representation.

**Python**

```python
cc.Step(
    kind=cc.StepKind.U256_TO_BINARY,
    config=cc.U256ToBinaryConfig(
        tables=["transfers"],   # optional — list of table names to process. When ``None``, all tables in the data dictionary are processed, default: None
    ),
)
```

**yaml**

```yaml
- kind: u256_to_binary
  config:
    tables: [transfers]   # optional — apply to specific tables only; default: all tables
```

---
-->

## Join Block Data

Joins block fields into other tables using a left outer join. Column collisions are prefixed with `<block_table_name>_`.

**Python**

```python
cc.Step(
    kind=cc.StepKind.JOIN_BLOCK_DATA,
    config=cc.JoinBlockDataConfig(
        tables=["logs"],                # optional — list of tables to join into; default: all tables except the block table
        block_table_name="blocks",      # optional — name of the blocks table, default: "blocks"
        join_left_on=["block_number"],  # optional — join key on the left (child) table, default: ["block_number"]
        join_blocks_on=["number"],      # optional — join key on the blocks table, default: ["number"]
    ),
)
```

**yaml**

```yaml
- kind: join_block_data
  config:
    tables: [logs]               # optional — tables to join into; default: all tables except the block table
    block_table_name: blocks     # optional, default: "blocks"
    join_left_on: [block_number] # optional, default: ["block_number"]
    join_blocks_on: [number]     # optional, default: ["number"]
```

---

## Join EVM Transaction Data

Joins EVM transaction fields into other tables using a left outer join. Column collisions are prefixed with `<tx_table_name>_`.
**Python**

```python
cc.Step(
    kind=cc.StepKind.JOIN_EVM_TRANSACTION_DATA,
    config=cc.JoinEvmTransactionDataConfig(
        tables=["logs"],                   # optional — list of tables to join into; default: all tables except the transactions table
        tx_table_name="transactions",      # optional — name of the transactions table, default: "transactions"
        join_left_on=["block_number", "transaction_index"],        # optional — join key on the left table, default: ["block_number", "transaction_index"]
        join_transactions_on=["block_number", "transaction_index"],# optional — join key on the transactions table, default: ["block_number", "transaction_index"]
    ),
)
```

**yaml**

```yaml
- kind: join_evm_transaction_data
  config:
    tables: [logs]                                           # optional — tables to join into; default: all except the transactions table
    tx_table_name: transactions                              # optional, default: "transactions"
    join_left_on: [block_number, transaction_index]          # optional, default: ["block_number", "transaction_index"]
    join_transactions_on: [block_number, transaction_index]  # optional, default: ["block_number", "transaction_index"]
```

---

## Join SVM Transaction Data

Joins SVM transaction fields into other tables using a left outer join. Column collisions are prefixed with `<tx_table_name>_`.

**Python**

```python
cc.Step(
    kind=cc.StepKind.JOIN_SVM_TRANSACTION_DATA,
    config=cc.JoinSvmTransactionDataConfig(
        tables=["instructions"],           # optional — list of tables to join into; default: all tables except the transactions table
        tx_table_name="transactions",      # optional — name of the transactions table, default: "transactions"
        join_left_on=["block_slot", "transaction_index"],        # optional — join key on the left table, default: ["block_slot", "transaction_index"]
        join_transactions_on=["block_slot", "transaction_index"],# optional — join key on the transactions table, default: ["block_slot", "transaction_index"]
    ),
)
```

**yaml**

```yaml
- kind: join_svm_transaction_data
  config:
    tables: [instructions]                                  # optional — tables to join into; default: all except the transactions table
    tx_table_name: transactions                             # optional, default: "transactions"
    join_left_on: [block_slot, transaction_index]           # optional, default: ["block_slot", "transaction_index"]
    join_transactions_on: [block_slot, transaction_index]   # optional, default: ["block_slot", "transaction_index"]
```

---

## Set Chain ID

Adds (or replaces) a constant `chain_id` column on every table.

**Python**

```python
cc.Step(
    kind=cc.StepKind.SET_CHAIN_ID,
    config=cc.SetChainIdConfig(
        chain_id=1,   # The chain identifier to set (e.g. 1 for Ethereum mainnet).
    ),
)
```

**yaml**

```yaml
- kind: set_chain_id
  config:
    chain_id: 1   # required
```

---

## Custom Steps with Polars (Python only)

The Polars step lets you plug any Python function directly into the pipeline. When the step runs, tiders converts every in-memory PyArrow table into a `polars.DataFrame`, calls your function with all of them at once, and then converts the results back to PyArrow tables so the rest of the pipeline can continue.

Your function receives two arguments:

- `data` — a `dict[str, pl.DataFrame]` mapping table names (e.g. `"transfers"`, `"blocks"`) to their current Polars DataFrames.
- `context` — any value (a dict, scalar, list, etc.) passed via `context` in the config , it exports this varible from the pipeline to the callable python function. Useful for parameterizing the function without hard-coding values. It is `None` when not set.

The function must return a `dict[str, pl.DataFrame]` mapping table name to tables. You can return the same tables with modifications, drop tables, or add new ones — whatever is in the returned dict becomes the new state of the pipeline's data for subsequent steps.

Requires `pip install tiders[polars]`.

```python
import polars as pl
import tiders as cc

def my_transform(data: dict[str, pl.DataFrame], context) -> dict[str, pl.DataFrame]:
    threshold = context["threshold"] if context else 0
    transfers = data["transfers"]
    # filter low-value transfers and add a normalized column
    data["transfers"] = (
        transfers
        .filter(pl.col("value") > threshold)
        .with_columns((pl.col("value") / 1e18).alias("value_eth"))
    )
    data.pop("raw_logs")
    return data # returned data dict will include the original inputs tables, except "raw_logs" (popped) and the add (or updated) table "transfer"

cc.Step(
    kind=cc.StepKind.POLARS,
    config=cc.PolarsStepConfig(
        runner=my_transform,
        context={"threshold": 1_000_000},   # optional — variable passed as context to the function, in this case a dict.
    ),
)
```

---

## Custom Steps with Pandas (Python only)

The Pandas step lets you plug any Python function directly into the pipeline. When the step runs, tiders converts every in-memory PyArrow table into a `pandas.DataFrame`, calls your function with all of them at once, and then converts the results back to PyArrow tables so the rest of the pipeline can continue.

Your function receives two arguments:

- `data` — a `dict[str, pd.DataFrame]` mapping table names (e.g. `"transfers"`, `"blocks"`) to their current Pandas DataFrames.
- `context` — any value (a dict, scalar, list, etc.) passed via `context` in the config, it exports this variable from the pipeline to the callable python function. Useful for parameterizing the function without hard-coding values. It is `None` when not set.

The function must return a `dict[str, pd.DataFrame]` mapping table name to tables. You can return the same tables with modifications, drop tables, or add new ones — whatever is in the returned dict becomes the new state of the pipeline's data for subsequent steps.

Requires `pip install tiders[pandas]`.

```python
import pandas as pd
import tiders as cc

def my_transform(data: dict[str, pd.DataFrame], context) -> dict[str, pd.DataFrame]:
    threshold = context["threshold"] if context else 0
    transfers = data["transfers"]
    # filter low-value transfers and add a normalized column
    transfers = transfers[transfers["value"] > threshold].copy()
    transfers["value_eth"] = transfers["value"] / 1e18
    data["transfers"] = transfers
    data.pop("raw_logs")
    return data  # returned data dict will include the original inputs tables, except "raw_logs" (popped) and the added (or updated) table "transfers"

cc.Step(
    kind=cc.StepKind.PANDAS,
    config=cc.PandasStepConfig(
        runner=my_transform,
        context={"threshold": 1_000_000},   # optional — variable passed as context to the function, in this case a dict.
    ),
)
```

---

## Custom Steps with DataFusion (Python only)

The DataFusion step uses [Apache DataFusion](https://datafusion.apache.org/) as the execution engine, which lets you write SQL queries against the pipeline tables within your custom function.

When the step runs, tiders creates a fresh `datafusion.SessionContext`, registers every in-memory PyArrow table as a DataFusion DataFrame inside it, and calls your function. Your function can run SQL queries through `session_ctx.sql(...)`, transform DataFrames using DataFusion's DataFrame API, or combine both. The returned DataFrames are converted back to PyArrow tables for the next step.

Your function receives three arguments:

- `session_ctx` — the `datafusion.SessionContext` with all current tables already registered by name, so you can query them directly with SQL.
- `data` — a `dict[str, datafusion.DataFrame]` mapping table names to their DataFusion DataFrames. It's a convenience shortcut for the DataFrame API — equivalent to calling `session_ctx.table(name)` for each table and useful to construct the returning data.
- `context` — any value (a dict, scalar, list, etc.) passed via `context` in the config , it exports this varible from the pipeline to the callable python function. Useful for parameterizing the function without hard-coding values. It is `None` when not set.

The function must return a `dict[str, datafusion.DataFrame]` mapping table name to tables. User is responsible to manage the returning dict. You can return the same tables with modifications, drop tables, or add new ones — whatever is in the returned dict becomes the new state of the pipeline's data for subsequent steps.

Requires `pip install tiders[datafusion]`.

```python
import datafusion
import tiders as cc

def my_sql_transform(session_ctx, data, context):
    min_block = context["min_block"] if context else 0
    data["transfers"] = session_ctx.sql(f"""
        SELECT t.*, b.timestamp
        FROM transfers t
        JOIN blocks b ON b.number = t.block_number
        WHERE t.block_number >= {min_block}
    """)
    data.pop("raw_logs")
    return data # returned data dict will include the original inputs tables, except "raw_logs" (popped) and the added (or updated) table "transfer"

cc.Step(
    kind=cc.StepKind.DATAFUSION,
    config=cc.DataFusionStepConfig(
        runner=my_sql_transform,
        context={"min_block": 18_500_000},   # optional — variable passed as context to the function, in this case a dict.
    ),
)
```

---

## Python File (yaml only)

The `python_file` kind is the yaml equivalent of the Polars and DataFusion custom steps. It imports a `.py` file as a module, looks up the named function, and runs it as either a Polars or DataFusion step depending on `step_type`.

The file path is resolved relative to the yaml config file's directory. The function must be defined at the module level (not nested inside another function or class).

**Polars**

Set `step_type: polars`. The function must use the `(data, context)` signature described in [Custom Steps with Polars](#custom-steps-with-polars).

`./steps/my_step.py`:

```python
import polars as pl

def my_transform(data: dict[str, pl.DataFrame], context) -> dict[str, pl.DataFrame]:
    threshold = context["threshold"] if context else 0
    transfers = data["transfers"]
    transfers = (
        transfers
        .filter(pl.col("value") > threshold)
        .with_columns((pl.col("value") / 1e18).alias("value_eth"))
    )
    data["transfers"] = transfers
    return data
```

```yaml
- kind: python_file
  config:
    file: ./steps/my_step.py    # required — path to the .py file, relative to the yaml config
    function: my_transform      # required — module-level function name to call
    step_type: polars           # required — "polars", "pandas", or "datafusion" (default: datafusion)
    context:                    # optional — any yaml value, passed as context to the function
      threshold: 1000000
```

**Pandas**

Set `step_type: pandas`. The function must use the `(data, context)` signature described in [Custom Steps with Pandas](#custom-steps-with-pandas).

`./steps/my_step.py`:

```python
import pandas as pd

def my_transform(data: dict[str, pd.DataFrame], context) -> dict[str, pd.DataFrame]:
    threshold = context["threshold"] if context else 0
    transfers = data["transfers"]
    transfers = transfers[transfers["value"] > threshold].copy()
    transfers["value_eth"] = transfers["value"] / 1e18
    data["transfers"] = transfers
    return data
```

```yaml
- kind: python_file
  config:
    file: ./steps/my_step.py    # required — path to the .py file, relative to the yaml config
    function: my_transform      # required — module-level function name to call
    step_type: pandas           # required — "polars", "pandas", or "datafusion" (default: datafusion)
    context:                    # optional — any yaml value, passed as context to the function
      threshold: 1000000
```

**DataFusion**

Set `step_type: datafusion` (or omit it, since datafusion is the default). The function must use the `(session_ctx, data, context)` signature described in [Custom Steps with DataFusion](#custom-steps-with-datafusion).

`./steps/my_step.py`:

```python
def my_sql_transform(session_ctx, data, context):
    min_block = context["min_block"] if context else 0
    data["transfers"] = session_ctx.sql(f"""
        SELECT t.*, b.timestamp
        FROM transfers t
        JOIN blocks b ON b.number = t.block_number
        WHERE t.block_number >= {min_block}
    """)
    return data
```

```yaml
- kind: python_file
  config:
    file: ./steps/my_step.py      # required — path to the .py file, relative to the yaml config
    function: my_sql_transform    # required — module-level function name to call
    step_type: datafusion         # optional — default when step_type is omitted
    context:                      # optional — any yaml value, passed as context to the function
      min_block: 18500000
```

---

## SQL (yaml only)

The `sql` kind is a yaml-only convenience step that lets you write DataFusion SQL directly in your config file without needing a separate Python file. Under the hood it builds a DataFusion runner and executes each query sequentially against the current in-memory tables.

All in-memory tables are available by name in every query. Queries run in order, and the output of one query is available to the next. Each query's result is stored back into the pipeline data:

- `CREATE TABLE name AS SELECT ...` — stores the result under `name`, making it available for subsequent steps and for the writer. `CREATE OR REPLACE TABLE` and `CREATE TABLE IF NOT EXISTS` are also supported.
- `CREATE VIEW name AS SELECT ...` — same as above; the view is registered in the session and stored under `name`.
- Plain `SELECT ...` — stores the result under the key `sql_result`, overwriting the previous value if multiple plain selects are used.

Existing tables not referenced in any query are preserved unchanged.

**yaml**

```yaml
- kind: sql
  config:
    queries:                        # required — one or more SQL strings, run in order
      - >
        CREATE TABLE transfers AS
        SELECT *
        FROM logs
        WHERE topic0 = '0xddf252ad...'
      - >
        CREATE OR REPLACE TABLE enriched AS
        SELECT t.*, b.timestamp
        FROM transfers t
        JOIN blocks b ON b.number = t.block_number
```