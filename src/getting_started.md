# Getting Started

This section walks you through installing tiders and running your first blockchain data pipeline.

## Prerequisites

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Quick Start

```bash
# Install
pip install tiders-etl tiders-core
# Or with uv:
uv pip install tiders-etl tiders-core
```

Then run one of the included examples:

```bash
# Fetch ERC-20 transfers into DuckDB
uv run examples/erc20_custom.py --provider hypersync

# Fetch blocks from an RPC endpoint into Parquet
uv run examples/rpc_pipeline.py
```

Read on for detailed [installation](./getting_started/installation.md) instructions and a step-by-step [first pipeline](./getting_started/first_pipeline.md) tutorial.
