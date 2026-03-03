# Python SDK Overview

The `tiders-etl` Python package is the primary user-facing interface for building blockchain data pipelines.

## Installation

```bash
pip install tiders-etl tiders-core
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

```python
import asyncio
from tiders_etl import config as cc, run_pipeline
from tiders_core import ingest

pipeline = cc.Pipeline(
    provider=ingest.ProviderConfig(kind=ingest.ProviderKind.HYPERSYNC, url="https://eth.hypersync.xyz"),
    query=query,       # see Query docs
    writer=writer,     # see Writers docs
    steps=[...],       # see Steps docs
)

asyncio.run(run_pipeline(pipeline=pipeline))
```

## Module Structure

```text
tiders_etl
├── config          # Pipeline, Step, Writer configuration classes
├── pipeline        # run_pipeline() entry point
├── writers/        # Output adapters (DuckDB, ClickHouse, Iceberg, etc.)
└── utils           # Utility functions
```

## Performance Model

tiders parallelizes three phases automatically:

1. **Ingestion** — fetching data from the provider (async, concurrent)
2. **Processing** — running transformation steps on each batch
3. **Writing** — inserting into the output store

The next batch is being fetched while the current batch is being processed and the previous batch is being written.
