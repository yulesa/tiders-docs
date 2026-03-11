# Installation

## CLI (No-Code Mode)

To use `tiders start` with a YAML config, install the `cli`:

```bash
pip install "tiders"
```

This adds everything needed to run pipelines from a YAML file.

Combine with writer extras as needed:

```bash
pip install "tiders[duckdb]"
pip install "tiders[delta_lake]"
pip install "tiders[clickhouse]"
pip install "tiders[iceberg]"
```

Or install everything at once:

```bash
pip install "tiders[all]"
```

## Python SDK

To create pipelines scripts in python, install Tiders as libraries. Tiders is published to PyPI as two packages:

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

Depending on your selected writer or transformation engine, you may need additional packages:

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
| Pandas | `pandas` |
| DataFusion | `datafusion` |

```bash
uv pip install tiders[duckdb, polars] tiders-core
```
