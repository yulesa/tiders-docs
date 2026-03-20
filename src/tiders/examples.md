# Examples

Complete working examples that demonstrate different tiders features. Each example is designed to highlight a different aspect of the framework — start with the one closest to your use case.

| Example | Chain | Provider | Decoding | Writer |
|---|---|---|---|---|
| [rETH Transfer (no code)](./examples/reth_transfer.md) | Ethereum (EVM) | Hypersync (Envio) | EVM event decode | Parquet (Pyarrow Dataset) |
| [Jupiter Swaps](./examples/jup_swaps.md) | Solana (SVM) | SQD | SVM instruction decode | DuckDB |
| [Uniswap V3](./examples/uniswap_v3.md) | Ethereum (EVM) | HyperSync / SQD / RPC | EVM event decode (factory + children) | DuckDB / Parquet / Delta Lake / ClickHouse / Iceberg |

## What each example teaches

- **rETH Transfer** — The simplest starting point. Uses a **YAML config with no Python code**, showing how to index a single event from a single contract. Also demonstrates the **SQL step** for joining decoded data with block timestamps.

- **Jupiter Swaps** — Use Tiders' **Python SDK** and switches to **Solana (SVM)**. Shows how to decode **instruction data**, use a **custom Polars step** for joining tables, and run **post-pipeline SQL** in DuckDB to enrich data with external metadata.

- **Uniswap V3** — Demonstrates the **factory + children** two-stage indexing pattern, the most common multi-pipeline pattern in DeFi. Shows how to **chain two pipelines** where the first discovers contracts and the second indexes their events, how to **dynamically generate decode steps** from an ABI, and how to use **table aliases** to give descriptive names to raw ingested tables.

All examples are available in the [examples/](https://github.com/yulesa/tiders/tree/main/examples) directory of the tiders repository.
