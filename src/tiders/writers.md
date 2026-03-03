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

```python
import duckdb

writer = cc.Writer(
    kind=cc.WriterKind.DUCKDB,
    config=cc.DuckdbWriterConfig(
        connection=duckdb.connect("./data/output.db").cursor(),
    ),
)
```

## ClickHouse

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

## Iceberg

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

## Delta Lake

```python
writer = cc.Writer(
    kind=cc.WriterKind.DELTA_LAKE,
    config=cc.DeltaLakeWriterConfig(
        data_uri="s3://my-bucket/delta/",
        storage_options={"AWS_REGION": "us-east-1"},
    ),
)
```

## PyArrow Dataset (Parquet)

```python
writer = cc.Writer(
    kind=cc.WriterKind.PYARROW_DATASET,
    config=cc.PyArrowDatasetWriterConfig(
        base_dir="./data/output",
    ),
)
```

## Schema Auto-Inference

All writers support automatic table creation. tiders infers the output schema from the Arrow data and creates tables accordingly. No manual schema definition is needed.
