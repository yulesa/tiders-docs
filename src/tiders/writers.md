# Writers

Writers define where the processed data is stored. Each writer adapts the Arrow RecordBatch output to a specific storage format.

## Available Writers

| Writer | Format | Best for |
|---|---|---|
| `DUCKDB` | DuckDB database | Local analytics, prototyping |
| `CLICKHOUSE` | ClickHouse | Production analytics at scale |
| `ICEBERG` | Apache Iceberg | Data lake with ACID transactions |
| `DELTA_LAKE` | Delta Lake | Data lake with versioning |
| `PYARROW_DATASET` | Parquet files | Simple file-based storage |

## DuckDB

**Python**

```python
import duckdb

writer = cc.Writer(
    kind=cc.WriterKind.DUCKDB,
    config=cc.DuckdbWriterConfig(
        connection=duckdb.connect("./data/output.db").cursor(),
    ),
)
```

**yaml**

```yaml
writer:
  kind: duckdb
  config:
    path: data/output.duckdb
```

Requires: `pip install "tiders[duckdb]"`

## ClickHouse

**Python**

```python
writer = cc.Writer(
    kind=cc.WriterKind.CLICKHOUSE,
    config=cc.ClickHouseWriterConfig(
        client=clickhouse_client,
        engine="MergeTree()",
        order_by={"transfers": ["block_number", "log_index"]},
        create_tables=True,
    ),
)
```

**yaml**

```yaml
writer:
  kind: clickhouse
  config:
    host: localhost
    port: 8123
    username: default
    password: ${CH_PASSWORD}
    database: default
    engine: MergeTree()
    order_by:
      transfers: [block_number, log_index]
    create_tables: true
```

Requires: `pip install "tiders[clickhouse]"`

## Iceberg

**Python**

```python
writer = cc.Writer(
    kind=cc.WriterKind.ICEBERG,
    config=cc.IcebergWriterConfig(
        namespace="my_namespace",
        catalog=iceberg_catalog,
        write_location="s3://my-bucket/iceberg/",
    ),
)
```

**yaml**

```yaml
writer:
  kind: iceberg
  config:
    namespace: my_namespace
    catalog_uri: sqlite:///catalog.db
    warehouse: s3://my-bucket/iceberg/
    catalog_type: sql          # default: sql
    write_location: s3://my-bucket/iceberg/  # default: warehouse
```

Requires: `pip install "tiders[iceberg]"`

## Delta Lake

**Python**

```python
writer = cc.Writer(
    kind=cc.WriterKind.DELTA_LAKE,
    config=cc.DeltaLakeWriterConfig(
        data_uri="s3://my-bucket/delta/",
        storage_options={"AWS_REGION": "us-east-1"},
    ),
)
```

**yaml**

```yaml
writer:
  kind: delta_lake
  config:
    data_uri: s3://my-bucket/delta/
    partition_by: [block_number]    # optional
    storage_options:                # optional
      AWS_REGION: us-east-1
      AWS_ACCESS_KEY_ID: ${AWS_KEY}
    anchor_table: transfers         # optional
```

Requires: `pip install "tiders[delta_lake]"`

## PyArrow Dataset (Parquet)

**Python**

```python
writer = cc.Writer(
    kind=cc.WriterKind.PYARROW_DATASET,
    config=cc.PyArrowDatasetWriterConfig(
        base_dir="./data/output",
    ),
)
```

**yaml**

```yaml
writer:
  kind: pyarrow_dataset
  config:
    base_dir: data/output
    partitioning: [block_number]    # optional
    partitioning_flavor: hive       # optional
    max_rows_per_file: 1000000      # optional
    anchor_table: transfers         # optional
```

## Schema Auto-Inference

All writers support automatic table creation. tiders infers the output schema from the Arrow data and creates tables accordingly. No manual schema definition is needed.
