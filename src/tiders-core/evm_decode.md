# EVM Decode

The `tiders-evm-decode` crate decodes EVM smart contract data (events and function calls) from raw bytes into typed Arrow columns.

## Python Usage

### Decode Events

```python
from tiders_core import evm_decode_events, evm_signature_to_topic0

# Compute topic0 for filtering
topic0 = evm_signature_to_topic0("Transfer(address,address,uint256)")

# Decode log records into typed columns
decoded = evm_decode_events(
    record_batch,
    "Transfer(address indexed from, address indexed to, uint256 amount)",
)
```

### Decode Function Calls

```python
from tiders_core import evm_decode_call_inputs, evm_decode_call_outputs

inputs = evm_decode_call_inputs(record_batch, "transfer(address to, uint256 amount)")
outputs = evm_decode_call_outputs(record_batch, "balanceOf(address) returns (uint256)")
```

### Get Arrow Schema

```python
from tiders_core import evm_event_signature_to_arrow_schema

schema = evm_event_signature_to_arrow_schema(
    "Transfer(address indexed from, address indexed to, uint256 amount)"
)
```

## How It Works

1. Parses the Solidity ABI signature string
2. Uses [alloy](https://docs.rs/alloy/) `DynSolEvent`/`DynSolCall` for ABI decoding
3. Maps Solidity types to Arrow types (addresses, uint256, bytes, nested structs, arrays)
4. Returns an Arrow RecordBatch with decoded columns

## Rust API

See the [tiders_evm_decode rustdoc](../api/tiders_evm_decode/index.html) for the full API.
