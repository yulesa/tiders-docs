# CLI YAML Reference

A tiders YAML config has six top-level sections:

```yaml
project:       # pipeline metadata (required)
provider:      # data source (required)
contracts:     # ABI + address helpers (optional)
query:         # what data to fetch (required)
steps:         # transformation pipeline (optional)
writer:        # where to write output (required)
table_aliases: # rename default table names (optional)
```

---

## `project`

```yaml
project:
  name: my_pipeline                               # project name
  description: My description.                    # project description
  repository: https://github.com/yulesa/tiders    # optional — informative only
  environment_path: "../../.env"                  # optional — allows to override the .env file path
```

---

## `provider`

```yaml
provider:
  kind: hypersync   # hypersync | sqd | rpc
  url: ${PROVIDER_URL}
  bearer_token: ${TOKEN}   # HyperSync only, optional
```

See [Providers](./providers.md) for full details.

---

## `contracts`

Optional list of contracts. If a ABI path is defined, Tiders reads the events and functions signatures. Addresses, signatures, topic0 and ABI-derived values can be referenced by name anywhere in `provider:` or `query:`.

```yaml
contracts:
  - name: MyToken
    address: "0xabc123..."
    abi: ./MyToken.abi.json
```

**Reference syntax:**

| Reference | Resolves to |
|---|---|
| `MyToken.address` | The contract address string |
| `MyToken.Events.Transfer.topic0` | Keccak-256 hash of the event signature |
| `MyToken.Events.Transfer.signature` | Full event signature string |
| `MyToken.Functions.transfer.selector` | 4-byte function selector |
| `MyToken.Functions.transfer.signature` | Full function signature string |

---

## `query`

The query defines what blockchain data to fetch: the block range, which tables to include, what filters to apply, and which fields to select.

See [Query](./query.md) for full details on EVM and SVM query options, field selection, and request filters.

**EVM**

```yaml
query:
  kind: evm
  from_block: 18000000
  to_block: 18001000          # optional
  include_all_blocks: false   # optional
  fields:
    log: [address, topic0, topic1, topic2, topic3, data, block_number, transaction_hash, log_index]
    block: [number, timestamp]
    transaction: [hash, from, to, value]
    trace: [action_from, action_to, action_value]
  logs:
    - topic0: "Transfer(address,address,uint256)"  # signature or 0x hex
      address: "0xabc..."
      include_blocks: true
  transactions:
    - from: ["0xabc..."]
      include_blocks: true
  traces:
    - action_from: ["0xabc..."]
```

**SVM**

```yaml
query:
  kind: svm
  from_block: 330000000
  to_block: 330001000
  include_all_blocks: true
  fields:
    instruction: [block_slot, program_id, data, accounts]
    transaction: [signature, fee]
    block: [slot, timestamp]
  instructions:
    - program_id: ["JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"]
      include_transactions: true
  transactions:
    - signer: ["0xabc..."]
  logs:
    - kind: [program, system_program]
  balances:
    - account: ["0xabc..."]
  token_balances:
    - mint: ["..."]
  rewards:
    - pubkey: ["..."]
```

---

## `steps`

Steps are transformations applied to each batch of data before writing. They run in order and can decode, cast, encode, join, or apply custom logic.

See [Steps](./steps.md) for full details on each step kind.

### `evm_decode_events`

Decode EVM log events using an ABI signature

```yaml
- kind: evm_decode_events
  config:
    event_signature: "Transfer(address indexed from, address indexed to, uint256 amount)"
    output_table: transfers        # optional — name of the output table for decoded results, default: "decoded_logs"
    input_table: logs              # optional — name of the input table to decode, default: "logs"
    allow_decode_fail: true        # optional — when True rows that fails are nulls values instead of raising an error, default: False
    filter_by_topic0: false        # optional — when True only rows whose ``topic0`` matches the event topic0 are decoded, default: False
    hstack: true                   # optional — when True decoded columns are horizontally stacked with the input columns, default: True
```

### `svm_decode_instructions`

Decode Solana program instructions

```yaml
- kind: svm_decode_instructions
  config:
    instruction_signature:
      discriminator: "0xe517cb977ae3ad2a"  # The instruction discriminator bytes used to identify the instruction type.
      params:                              # The list of typed parameters to decode from the instruction data (after the discriminator).
        - name: amount
          type: u64
        - name: data
          type: { type: array, element: u8 }
      accounts_names: [tokenAccountIn, tokenAccountOut] #  Names assigned to positional accounts in the instruction.
    allow_decode_fail: false              # optional — when True, rows that fails are nulls values instead of raising an error, default: False
    filter_by_discriminator: false        # optional — when True, only rows whose data starting bytes matches the event topic0 are decoded, default: False
    input_table: instructions             # optional — name of the input table to decode, default: "instructions"
    output_table: decoded_instructions    # optional — name of the input table to decode, default: "decoded_instructions"
    hstack: true                          # optional — when True, decoded columns are horizontally stacked with the input columns, default: True
```

### `svm_decode_logs`

Decode Solana program logs

```yaml
- kind: svm_decode_logs
  config:
    log_signature:              # The list of typed parameters to decode from the log data.
      params:
        - name: amount_in
          type: u64
        - name: amount_out
          type: u64
    allow_decode_fail: false    # optional — when True rows that fails are nulls values instead of raising an error, default: False
    input_table: logs           # optional — name of the input table to decode, default: "logs"
    output_table: decoded_logs  # optional — name of the input table to decode, default: "decoded_logs"
    hstack: true                # optional — when True decoded columns are horizontally stacked with the input columns, default: True
```

### `cast_by_type`

```yaml
- kind: cast_by_type
  config:
    from_type: "decimal256(76,0)" # The source pyarrow.DataType to match.
    to_type: "decimal128(38,0)"   # The target pyarrow.DataType to cast
    allow_cast_fail: true         # optional — when True, values that cannot be cast are set to null instead of raising an error, default: False
```

Supported type strings: `int8`–`int64`, `uint8`–`uint64`, `float16`–`float64`, `string`, `utf8`, `large_string`, `binary`, `large_binary`, `bool`, `date32`, `date64`, `null`, `decimal128(p,s)`, `decimal256(p,s)`.

### `cast`

Cast all columns of one type to another

```yaml
- kind: cast
  config:
    table_name: transfers         # The name of the table whose columns should be cast.
    mappings:                     # A mapping of column name to target pyarrow.DataType
      amount: "decimal128(38,0)"
      block_number: "int64"
    allow_cast_fail: false        # optional — When True, values that cannot be cast are set to null instead of raising an error, default: False
```

Supported type strings: `int8`–`int64`, `uint8`–`uint64`, `float16`–`float64`, `string`, `utf8`, `large_string`, `binary`, `large_binary`, `bool`, `date32`, `date64`, `null`, `decimal128(p,s)`, `decimal256(p,s)`.

### `hex_encode`

Hex-encode all binary columns

```yaml
- kind: hex_encode
  config:
    tables: [transfers]   # optional — list of table names to process. When ``None``, all tables in the data dictionary are processed, default: None
    prefixed: true        # optional — When True, output strings are "0x"-prefixed, default: True
```

### `base58_encode`

Base58-encode all binary columns

```yaml
- kind: base58_encode
  config:
    tables: [instructions]   # optional — list of table names to process. When ``None``, all tables in the data dictionary are processed, default: None
```

### `set_chain_id`

Add a chain_id column

```yaml
- kind: set_chain_id
  config:
    chain_id: 1  # The chain identifier to set (e.g. 1 for Ethereum mainnet).
```

### `sql`

Run one or more DataFusion SQL queries. `CREATE TABLE name AS SELECT ...` stores results under `name`; plain `SELECT` stores as `sql_result`.

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

### `python_file`

Load a custom step function from an external Python file. Paths are relative to the YAML config directory.

```yaml
- kind: python_file
  name: my_custom_step
  config:
    file: ./steps/my_step.py
    function: transform          # callable name in the file
    step_type: datafusion        # datafusion (default), polars, or pandas
    context:                     # optional — passed as ctx to the function
      threshold: 100
```

---

## `writer`

See [Writers](./writers.md) for full details.

### DuckDB

```yaml
writer:
  kind: duckdb
  config:
    path: data/output.duckdb   # path to create or connect to a duckdb database
```

### ClickHouse

```yaml
writer:
  kind: clickhouse
  config:
    host: localhost            # ClickHouse server hostname
    port: 8123                 # ClickHouse HTTP port
    username: default          # ClickHouse username
    password: ${CH_PASSWORD}   # ClickHouse password
    database: default          # ClickHouse database name
    secure: false              # optional — use TLS, default: false
    codec: LZ4                 # optional — default compression codec for all columns
    order_by:                  # optional — per-table ORDER BY columns
      transfers: [block_number, log_index]
    engine: MergeTree()        # optional — ClickHouse table engine, default: MergeTree()
    anchor_table: transfers    # optional — table written last, for ordering guarantees
    create_tables: true        # optional — auto-create tables on first insert, default: true
```

### Delta Lake

```yaml
writer:
  kind: delta_lake
  config:
    data_uri: s3://my-bucket/delta/   # base URI where Delta tables are stored
    partition_by: [block_number]      # optional — columns used for partitioning
    storage_options:                  # optional — cloud storage credentials/options
      AWS_REGION: us-east-1
      AWS_ACCESS_KEY_ID: ${AWS_KEY}
    anchor_table: transfers           # optional — table written last, for ordering guarantees
```

### Iceberg

```yaml
writer:
  kind: iceberg
  config:
    namespace: my_namespace                  # Iceberg namespace (database) to write tables into
    catalog_uri: sqlite:///catalog.db        # URI for the Iceberg catalog (e.g. sqlite or jdbc)
    warehouse: s3://my-bucket/iceberg/       # warehouse root URI for the catalog
    catalog_type: sql                        # catalog type (e.g. sql, rest, hive)
    write_location: s3://my-bucket/iceberg/  # storage URI where Iceberg data files are written
```

### PyArrow Dataset (Parquet)

```yaml
writer:
  kind: pyarrow_dataset
  config:
    base_dir: data/output          # root directory for all output datasets
    anchor_table: transfers        # optional — table written last, for ordering guarantees
    partitioning: [block_number]   # optional — columns or Partitioning object per table
    partitioning_flavor: hive      # optional — partitioning flavor (e.g. hive)
    max_rows_per_file: 1000000     # optional — max rows per output file, default: 0 (unlimited)
    create_dir: true               # optional — create output directory if missing, default: true
```

### PostgreSQL

```yaml
writer:
  kind: postgresql
  config:
    host: localhost               # required — PostgreSQL server hostname
    dbname: mydb                  # required — database name
    port: 5432                    # optional, default: 5432
    user: postgresql              # optional, default: postgresql
    password: ${PG_PASSWORD}      # optional
    schema: public                # optional — PostgreSQL schema (namespace), default: public
    create_tables: true           # optional — auto-create tables on first push, default: true
    anchor_table: transfers       # optional — table written last, for ordering guarantees
```

---

## `table_aliases`

Rename the default ingestion table names.

### EVM

```yaml
table_aliases:
  blocks: my_blocks     # optional — name for the blocks response, default: "blocks"
  transactions: my_txs  # optional — name for the transactions response, default: "transactions"
  logs: my_logs         # optional — name for the logs response, default: "logs"
  traces: my_traces     # optional — name for the traces response, default: "traces"
```

### SVM

```yaml
table_aliases:
  instructions: my_instructions       # optional — name for the instructions response, default: "instructions"
  transactions: my_txs                # optional — name for the transactions response, default: "transactions"
  logs: my_logs                       # optional — name for the logs response, default: "logs"
  balances: my_balances               # optional — name for the balances response, default: "balances"
  token_balances: my_token_balances   # optional — name for the token_balances response, default: "token_balances"
  rewards: my_rewards                 # optional — name for the rewards response, default: "rewards"
  blocks: my_blocks                   # optional — name for the blocks response, default: "blocks"
```
