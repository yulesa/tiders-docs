# Tiders

**Tiders** is an open-source framework for building production-ready blockchain data pipelines.

It lets you extract, decode, transform, and store blockchain data using Python.

## Architecture

Tiders is composed of three repositories:

| Repository | Language | Role |
|---|---|---|
| [tiders](https://github.com/yulesa/tiders) | Python | User-facing SDK for building pipelines |
| [tiders-core](https://github.com/yulesa/tiders-core) | Rust | Core libraries for ingestion, decoding, casting, and schema |
| [tiders-rpc-client](https://github.com/yulesa/tiders-rpc-client) | Rust | RPC client for fetching data from any standard EVM JSON-RPC endpoint |

```text
                         ┌──────────────────────────────┐
                         │      tiders (Python SDK)     │
                         │   pipeline · steps · writers │
                         └──────────────┬───────────────┘
                                        │ calls via PyO3
                         ┌──────────────▼───────────────┐
                         │     tiders-core (Rust)       │
                         │  ingest · decode · cast      │
                         │  evm-schema · svm-schema     │
                         └──────┬───────────────┬───────┘
                                │               │
               ┌────────────────▼──┐   ┌────────▼───────────┐
               │   Data Providers  │   │  tiders-rpc-client │
               │ HyperSync · SQD   │   │  Any EVM JSON-RPC  │
               └───────────────────┘   └────────────────────┘
```

## Key Features

- **Python** — define pipelines as Python code
- **High performance** — all core operations implemented in Rust
- **Multiple data providers** — HyperSync, SQD, and standard RPC endpoints
- **EVM and SVM support** — Ethereum and Solana blockchains
- **Built-in decoding** — ABI event decoding (EVM) and instruction decoding (SVM)
- **Flexible output** — ClickHouse, PostgreSQL, DuckDB, Parquet, Iceberg, DeltaLake, DuckDB, Parquet
- **Streaming architecture** — parallelized ingestion, processing, and writing

## API Reference

Auto-generated Rust API documentation is available at:

- [tiders-core rustdoc](./api/tiders_core/index.html)
- [tiders-rpc-client rustdoc](./api/tiders_rpc_client/index.html)
