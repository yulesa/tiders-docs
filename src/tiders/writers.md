# Writers

Writers define where the processed data is stored after each pipeline batch. Each writer adapts the Arrow RecordBatch output to a specific storage format.

## Available Writers

| Writer | Format | Best for |
|---|---|---|
| `DUCKDB` | DuckDB database | Local analytics, prototyping |
| `CLICKHOUSE` | ClickHouse | Production analytics at scale |
| `ICEBERG` | Apache Iceberg | Data lake with ACID transactions |
| `DELTA_LAKE` | Delta Lake | Data lake with versioning |
| `PYARROW_DATASET` | Parquet files | Simple file-based storage |
| `POSTGRESQL` | PostgreSQL | Relational storage, existing PostgreSQL instances |
| `CSV` | CSV files | Simple text export, interoperability |

Each table in the pipeline data is written as a separate table or directory named after its key (e.g. `"transfers"` → `transfers` table or `transfers/` directory).

All writers support automatic table creation. tiders infers the output schema from the Arrow data and creates tables accordingly. No manual schema definition is needed.


---

## DuckDB

Inserts Arrow tables into a DuckDB database. Tables are auto-created on the first push using the Arrow schema. `Decimal256` columns are automatically downcast to `Decimal128(38, scale)` since DuckDB does not support 256-bit decimals — use a [`cast_by_type`](steps.md#cast-by-type) step beforehand if you need control over overflow behavior.

Requires: `pip install "tiders[duckdb]"`

**Python**

```python
import duckdb
import tiders as cc

writer = cc.Writer(
    kind=cc.WriterKind.DUCKDB,
    config=cc.DuckdbWriterConfig(
        connection=duckdb.connect("./data/output.duckdb"),   # required
    ),
)
```

**yaml**

```yaml
writer:
  kind: duckdb
  config:
    path: data/output.duckdb   # required
```

---

## ClickHouse

Inserts Arrow tables into ClickHouse using the `clickhouse-connect` async client. Tables are auto-created on the first insert using the inferred Arrow schema. All tables except the `anchor_table` are inserted in parallel.

Requires: `pip install "tiders[clickhouse]"`

**Python**

```python
import clickhouse_connect
import tiders as cc
from tiders.config import ClickHouseSkipIndex

clickhouse_client = await clickhouse_connect.get_async_client(
    host="localhost",
    port=8123,
    username="default",
    password="",
    database="default",
    secure=False,
)

writer = cc.Writer(
    kind=cc.WriterKind.CLICKHOUSE,
    config=cc.ClickHouseWriterConfig(
        client=clickhouse_client,   # required, An async ClickHouse client (``clickhouse_connect``)
        engine="MergeTree()",       # optional, ClickHouse table engine clause. default: MergeTree()
        order_by={"transfers": ["block_number", "log_index"]},   # optional, per-table ordering key columns.
        codec={"transfers": {"data": "ZSTD(3)"}},   # optional, per-table, per-column compression codecs.
        skip_index={"transfers": [ClickHouseSkipIndex(name="idx_value", val="value", type_="minmax", granularity=1)]},   # optional, per-table list of data-skipping indexes added after table creation.
        create_tables=True,         # optional, when True, tables are auto-created on the first insert using the Arrow schema, default: True.
        anchor_table="transfers",   # optional, if set, this table is inserted last to provide ordering guarantees for downstream consumers, default: None.
    ),
)
```

**yaml**

```yaml
writer:
  kind: clickhouse
  config:                         # include params to create the ClickHouseClient.
    host: localhost               # required
    port: 8123                    # optional, default: 8123
    username: default             # optional, default: default
    password: ${CH_PASSWORD}      # optional, default: ""
    database: default             # optional, default: default
    secure: false                 # optional, default: false
    engine: MergeTree()           # optional, default: MergeTree()
    order_by:                     # optional — per-table list of ORDER BY columns
      transfers: [block_number, log_index]
    codec:                        # optional — per-table, per-column compression codec
      transfers:
        data: ZSTD(3)
    create_tables: true           # optional, default: true
    anchor_table: transfers       # optional — written last after all other tables
```

**`skip_index`** (Python only): `ClickHouseSkipIndex` takes `name`, `val` (index expression), `type_` (e.g. `"minmax"`, `"bloom_filter"`), and `granularity`. Indexes are added after table creation via `ALTER TABLE ... ADD INDEX`.

---

## Iceberg

Writes Arrow tables into an Apache Iceberg catalog. Each table is created in the specified namespace if it does not already exist.

Requires: `pip install "tiders[iceberg]"`

**Python**

```python
from pyiceberg.catalog import load_catalog
import tiders as cc

catalog = load_catalog(
    "my_catalog",
    type="sql",
    uri="sqlite:///catalog.db",
    warehouse="s3://my-bucket/iceberg/",
)

writer = cc.Writer(
    kind=cc.WriterKind.ICEBERG,
    config=cc.IcebergWriterConfig(
        namespace="my_namespace",           # required — Iceberg namespace (database) to write tables into
        catalog=catalog,                    # required — a pyiceberg Catalog instance
        write_location="s3://my-bucket/iceberg/",   # required — storage URI where Iceberg data files are written
    ),
)
```

**yaml**

```yaml
writer:
  kind: iceberg
  config:
    namespace: my_namespace                          # required
    catalog_uri: sqlite:///catalog.db                # required
    warehouse: s3://my-bucket/iceberg/               # required
    catalog_type: sql                                # optional, default: sql
    write_location: s3://my-bucket/iceberg/          # optional, default: warehouse
```

---

## Delta Lake

Appends Arrow tables to Delta tables using `deltalake.write_deltalake` with schema merging enabled. Each table is stored at `<data_uri>/<table_name>/`. All tables except the `anchor_table` are written in parallel.

Requires: `pip install "tiders[delta_lake]"`

**Python**

```python
import tiders as cc

writer = cc.Writer(
    kind=cc.WriterKind.DELTA_LAKE,
    config=cc.DeltaLakeWriterConfig(
        data_uri="s3://my-bucket/delta/",               # required — base URI; each table is written to <data_uri>/<table_name>/
        partition_by={"transfers": ["block_number"]},   # optional — per-table list of partition columns
        storage_options={"AWS_REGION": "us-east-1"},    # optional — cloud storage credentials passed to deltalake
        anchor_table="transfers",                       # optional — written last after all other tables
    ),
)
```

**yaml**

```yaml
writer:
  kind: delta_lake
  config:
    data_uri: s3://my-bucket/delta/    # required
    partition_by:                       # optional — per-table list of partition columns
      transfers: [block_number]
    storage_options:                    # optional — cloud storage credentials
      AWS_REGION: us-east-1
      AWS_ACCESS_KEY_ID: ${AWS_KEY}
    anchor_table: transfers             # optional — written last after all other tables
```

---

## PyArrow Dataset (Parquet)

Writes Arrow tables as Parquet files using `pyarrow.dataset.write_dataset`. Each table is stored under `<base_dir>/<table_name>/`. A monotonic counter is appended to the file name to avoid collisions across successive pushes. All tables except the `anchor_table` are written in parallel.

**Python**

```python
import tiders as cc

writer = cc.Writer(
    kind=cc.WriterKind.PYARROW_DATASET,
    config=cc.PyArrowDatasetWriterConfig(
        base_dir="./data/output",                       # required — root directory; each table is written to <base_dir>/<table_name>/
        partitioning={"transfers": ["block_number"]},   # optional — per-table list of partition columns or pyarrow.dataset.Partitioning
        partitioning_flavor={"transfers": "hive"},      # optional — per-table partitioning flavor
        basename_template="part-{i}.parquet",           # optional — output file name template, default: "part-{i}.parquet"
        max_rows_per_file=1_000_000,                    # optional — max rows per output file, default: 0 (unlimited)
        min_rows_per_group=0,                           # optional — min rows per Parquet row group, default: 0
        max_rows_per_group=1024 * 1024,                 # optional — max rows per Parquet row group, default: 1048576
        max_partitions=1024,                            # optional — max number of partitions, default: 1024
        max_open_files=1024,                            # optional — max files open simultaneously, default: 1024
        use_threads=True,                               # optional — use threads for writing, default: True
        create_dir=True,                                # optional — create output directory if missing, default: True
        anchor_table="transfers",                       # optional — written last after all other tables
    ),
)
```

**yaml**

```yaml
writer:
  kind: pyarrow_dataset
  config:
    base_dir: data/output                # required
    partitioning:                        # optional — per-table list of partition columns
      transfers: [block_number]
    partitioning_flavor:                 # optional — per-table flavor (e.g. "hive")
      transfers: hive
    basename_template: part-{i}.parquet  # optional — output file name template
    max_rows_per_file: 1000000           # optional, default: 0 (unlimited)
    min_rows_per_group: 0                # optional, default: 0
    max_rows_per_group: 1048576          # optional, default: 1048576
    max_partitions: 1024                 # optional, default: 1024
    max_open_files: 1024                 # optional, default: 1024
    use_threads: true                    # optional, default: true
    create_dir: true                     # optional, default: true
    anchor_table: transfers              # optional — written last after all other tables
```

---

## CSV

Writes Arrow tables as CSV files using `pyarrow.csv.write_csv`. Each table is written to `<base_dir>/<table_name>.csv`. On successive pushes the file is appended to. All tables except the `anchor_table` are written in parallel.

**Python**

```python
import tiders as cc

writer = cc.Writer(
    kind=cc.WriterKind.CSV,
    config=cc.CsvWriterConfig(
        base_dir="./data/output",       # required — root directory; each table is written to <base_dir>/<table_name>.csv
        delimiter=",",                  # optional — field delimiter character, default: ","
        include_header=True,            # optional — write a header row, default: True
        create_dir=True,                # optional — create output directory if missing, default: True
        anchor_table="transfers",       # optional — written last after all other tables
    ),
)
```

**yaml**

```yaml
writer:
  kind: csv
  config:
    base_dir: data/output        # required
    delimiter: ","               # optional, default: ","
    include_header: true         # optional, default: true
    create_dir: true             # optional, default: true
    anchor_table: transfers      # optional — written last after all other tables
```

---

## PostgreSQL

Inserts Arrow tables into PostgreSQL using the COPY protocol via `psycopg` v3. Tables are auto-created on the first push using `CREATE TABLE IF NOT EXISTS` derived from the Arrow schema. All tables except the `anchor_table` are inserted in parallel.

Requires: `pip install "tiders[postgresql]"`

### Unsupported raw blockchain fields

The PostgreSQL writer does **not** support `List`, `Struct`, or `Map` Arrow columns. Writing raw EVM or SVM data directly will fail unless you use a step to flatten or drop the affected columns first.

**EVM fields that require preprocessing:**

| Table | Field | Arrow type |
|---|---|---|
| `blocks` | `uncles` | `List(Binary)` |
| `blocks` | `withdrawals` | `List(Struct(index, validator_index, address, amount))` |
| `transactions` | `access_list` | `List(Struct(address, storage_keys))` |
| `transactions` | `blob_versioned_hashes` | `List(Binary)` |
| `traces` | `trace_address` | `List(UInt64)` |

**SVM fields that require preprocessing:**

| Table | Field | Arrow type |
|---|---|---|
| `transactions` | `account_keys` | `List(Binary)` |
| `transactions` | `signatures` | `List(Binary)` |
| `transactions` | `loaded_readonly_addresses` | `List(Binary)` |
| `transactions` | `loaded_writable_addresses` | `List(Binary)` |
| `transactions` | `address_table_lookups` | `List(Struct(account_key, writable_indexes, readonly_indexes))` |
| `logs` | `instruction_address` | `List(UInt32)` |
| `instructions` | `instruction_address` | `List(UInt32)` |
| `instructions` | `rest_of_accounts` | `List(Binary)` |

**Python**

```python
import psycopg
import asyncio
import tiders as cc

connection = asyncio.get_event_loop().run_until_complete(
    psycopg.AsyncConnection.connect(
        "host=localhost port=5432 dbname=mydb user=postgresql password=secret",
        autocommit=False,
    )
)

writer = cc.Writer(
    kind=cc.WriterKind.POSTGRESQL,
    config=cc.PostgresqlWriterConfig(
        connection=connection,         # required — open psycopg.AsyncConnection
        schema="public",               # optional — PostgreSQL schema (namespace), default: "public"
        create_tables=True,            # optional — auto-create tables on first push, default: True
        anchor_table="transfers",      # optional — written last after all other tables, default: None
    ),
)
```

**yaml**

```yaml
writer:
  kind: postgresql
  config:
    host: localhost               # required
    dbname: mydb                  # required
    port: 5432                    # optional, default: 5432
    user: postgresql              # optional, default: postgresql
    password: ${PG_PASSWORD}      # optional
    schema: public                # optional, default: public
    create_tables: true           # optional, default: true
    anchor_table: transfers       # optional — written last after all other tables
```

---
