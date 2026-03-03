# Installation

## Python SDK

tiders is published to PyPI as two packages:

- **`tiders-etl`** — the Python pipeline SDK
- **`tiders-core`** — pre-built Rust bindings (installed automatically as a dependency)

### Using pip

```bash
pip install tiders-etl tiders-core
```

### Using uv (recommended)

```bash
uv pip install tiders-etl tiders-core
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

## Development Setup

To develop tiders locally, you need all three repos:

```bash
git clone https://github.com/yulesa/tiders.git
git clone https://github.com/yulesa/tiders-core.git
git clone https://github.com/yulesa/tiders-rpc-client.git
```

### Building tiders-core from source

```bash
cd tiders-core
# Install maturin for building the Python extension
pip install maturin
# Build the Python package
cd python
maturin develop --release
```

### Setting up tiders for development

```bash
cd tiders
uv sync
```

The `pyproject.toml` is configured to use the local `tiders-core` build:

```toml
[tool.uv.sources]
tiders-core = { path = "../tiders-core/python", editable = true }
```
