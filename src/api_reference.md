# Rust API Reference

The Rust API documentation is auto-generated from source code using `rustdoc`. It provides detailed documentation for every public type, function, and module.

## Browse the API

- [tiders-core](./api/tiders_core/index.html) — re-exports all core crates
  - [tiders-ingest](./api/tiders_ingest/index.html) — data ingestion and streaming
  - [tiders-evm-decode](./api/tiders_evm_decode/index.html) — EVM ABI decoding
  - [tiders-svm-decode](./api/tiders_svm_decode/index.html) — Solana instruction decoding
  - [tiders-cast](./api/tiders_cast/index.html) — type casting
  - [tiders-evm-schema](./api/tiders_evm_schema/index.html) — EVM Arrow schemas
  - [tiders-svm-schema](./api/tiders_svm_schema/index.html) — SVM Arrow schemas
  - [tiders-query](./api/tiders_query/index.html) — query execution
- [tiders-rpc-client](./api/tiders_rpc_client/index.html) — EVM RPC data fetcher

## Building the API Docs Locally

To generate the rustdoc output locally:

```bash
# tiders-core (all crates)
cd tiders-core
cargo doc --no-deps --workspace

# tiders-rpc-client
cd tiders-rpc-client/rust
cargo doc --no-deps

# Open in browser
open target/doc/tiders_core/index.html
```
