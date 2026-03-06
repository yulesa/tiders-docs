# Installation

## Python SDK

tiders is published to PyPI as two packages:

- **`tiders`** — the Python pipeline SDK
- **`tiders-core`** — pre-built Rust bindings (installed automatically as a dependency)

### Using pip

```bash
pip install tiders tiders-core
```

### Using uv (recommended)

```bash
uv pip install tiders tiders-core
```

### Optional dependencies

Depending on your output format, you may need additional packages:

| Writer | Extra package |
|---|---|
| DuckDB | `duckdb` |
| ClickHouse | `clickhouse-connect` |
| Iceberg | `pyiceberg` |
| DeltaLake | `deltalake` |

For transformation steps:

| Step engine | Extra package |
|---|---|
| Polars | `polars` |
| DataFusion | `datafusion` |
