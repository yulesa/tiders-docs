# Tiders Overview (Python SDK)

The `tiders` Python package is the primary user-facing interface for building blockchain data pipelines.

## Two ways to use tiders

| Mode | How | When to use |
|---|---|---|
| **Python SDK** | Write a Python script, import `tiders` | Full control, custom logic, complex pipelines |
| **CLI (No-Code)** | Write a YAML config, run `tiders start` | Quick setup, no Python required, standard pipelines |

Both modes share the same pipeline engine. The CLI parses a YAML config into the same Python objects and calls the same `run_pipeline()` function.

## Installation

```bash
pip install tiders tiders-core
```

For the CLI (no-code mode):

```bash
pip install "tiders[cli]"
```

## Core Concepts

A pipeline is built from four components:

| Component | Description |
|---|---|
| `ProviderConfig` | Data source (HyperSync, SQD, or RPC) |
| `Query` | What data to fetch (block range, filters, field selection) |
| `Step` | Transformations to apply (decode, cast, encode, custom) |
| `Writer` | Output destination (DuckDB, ClickHouse, Iceberg, DeltaLake, Parquet) |

## Basic Usage

**Python**

```python
import asyncio
from tiders import config as cc, run_pipeline
from tiders_core import ingest

pipeline = cc.Pipeline(
    provider=ingest.ProviderConfig(kind=ingest.ProviderKind.HYPERSYNC, url="https://eth.hypersync.xyz"),
    query=query,       # see Query docs
    writer=writer,     # see Writers docs
    steps=[...],       # see Steps docs
)

asyncio.run(run_pipeline(pipeline=pipeline))
```

**yaml**

```yaml
provider:
  kind: hypersync
  url: ${PROVIDER_URL}

query:
  kind: evm
  from_block: 18000000

steps: [...]

writer:
  kind: duckdb
  config:
    path: data/output.duckdb
```

```bash
tiders start config.yaml
```

## Module Structure

```text
tiders
├── config          # Pipeline, Step, Writer configuration classes
├── pipeline        # run_pipeline() entry point
├── cli/            # CLI entry point and YAML parser
├── writers/        # Output adapters (DuckDB, ClickHouse, Iceberg, etc.)
└── utils           # Utility functions
```

## Performance Model

tiders parallelizes three phases automatically:

1. **Ingestion** — fetching data from the provider (async, concurrent)
2. **Processing** — running transformation steps on each batch
3. **Writing** — inserting into the output store

The next batch is being fetched while the current batch is being processed and the previous batch is being written.
