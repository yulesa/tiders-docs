# Cast

The `tiders-cast` crate provides blockchain-aware type casting for Arrow columns. It extends standard Arrow casting with support for types common in blockchain data.

## Python Usage

### Cast by Column Name

```python
import pyarrow as pa
from tiders_core import cast

# Cast specific columns to target types
casted_batch = cast(
    [("block_number", pa.int64()), ("value", pa.decimal128(38, 0))],
    record_batch,
)
```

### Cast by Type

Convert all columns of one Arrow type to another:

```python
from tiders_core import cast_by_type

# Convert all decimal256 columns to decimal128
casted_batch = cast_by_type(
    pa.decimal256(76, 0),
    pa.decimal128(38, 0),
    record_batch,
    allow_cast_fail=True,
)
```

This is useful when a downstream system (like DuckDB) doesn't support certain types.

## Encoding Utilities

The cast module also provides encoding/decoding functions:

```python
from tiders_core import hex_encode, prefix_hex_encode, base58_encode

# Encode binary columns
hex_batch = hex_encode(record_batch)           # "0a1b2c..."
prefixed = prefix_hex_encode(record_batch)     # "0x0a1b2c..."
b58_batch = base58_encode(record_batch)        # Base58 format
```

## Rust API

See the [tiders_cast rustdoc](../api/tiders_cast/index.html) for the full API.
