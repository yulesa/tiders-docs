# Core Libraries Overview

`tiders-core` is a Rust workspace that provides the high-performance engine behind tiders. It handles data ingestion, ABI decoding, type casting, encoding, and schema definitions.

The Python SDK calls into these libraries via [PyO3](https://pyo3.rs/) bindings.

## Crates

| Crate | Purpose |
|---|---|
| `tiders-ingest` | Data provider orchestration and streaming |
| `tiders-evm-decode` | EVM event and function ABI decoding |
| `tiders-svm-decode` | Solana instruction and log decoding |
| `tiders-cast` | Arrow column type casting (blockchain-aware) |
| `tiders-evm-schema` | Arrow schema definitions for EVM data |
| `tiders-svm-schema` | Arrow schema definitions for SVM data |
| `tiders-query` | Query execution and filtering |
| `tiders-core` | Re-export crate aggregating all of the above |
| `tiders-core-python` | PyO3 Python bindings |

## Dependency Graph

```text
tiders-core (re-exports)
├── tiders-ingest
│   ├── tiders-evm-schema
│   ├── tiders-svm-schema
│   └── tiders-rpc-client (optional, for RPC provider)
├── tiders-evm-decode
├── tiders-svm-decode
├── tiders-cast
└── tiders-query
```

## Rust API Reference

Auto-generated API documentation for all crates:
- [tiders-core rustdoc](../api/tiders_core/index.html)

## Python API

The `tiders_core` Python module exposes these functions directly:

| Function | Description |
|---|---|
| `cast()`, `cast_schema()` | Cast columns using a name-to-type mapping |
| `cast_by_type()`, `cast_schema_by_type()` | Cast all columns of one type to another |
| `hex_encode()`, `prefix_hex_encode()` | Hex-encode binary data |
| `base58_encode()`, `base58_encode_bytes()` | Base58-encode binary data |
| `evm_decode_events()` | Decode EVM log events |
| `evm_decode_call_inputs()`, `evm_decode_call_outputs()` | Decode EVM function calls |
| `evm_signature_to_topic0()` | Compute topic0 hash from event signature |
| `svm_decode_instructions()`, `svm_decode_logs()` | Decode Solana data |
| `ingest.start_stream()` | Start a streaming data ingestion pipeline |
