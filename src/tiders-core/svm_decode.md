# SVM Decode

The `tiders-svm-decode` crate decodes Solana program instructions and logs from raw bytes into typed Arrow columns.

## Python Usage

### Decode Instructions

```python
from tiders_core.svm_decode import InstructionSignature, ParamInput, DynType, FixedArray

# Define the instruction layout
signature = InstructionSignature(
    discriminator="0xe445a52e51cb9a1d40c6cde8260871e2",
    params=[
        ParamInput(name="Amm", param_type=FixedArray(DynType.U8, 32)),
        ParamInput(name="InputMint", param_type=FixedArray(DynType.U8, 32)),
        ParamInput(name="InputAmount", param_type=DynType.U64),
        ParamInput(name="OutputMint", param_type=FixedArray(DynType.U8, 32)),
        ParamInput(name="OutputAmount", param_type=DynType.U64),
    ],
    accounts_names=[],
)

from tiders_core import svm_decode_instructions

decoded = svm_decode_instructions(record_batch, signature)
```

### Available Types

- `DynType.U8`, `U16`, `U32`, `U64`, `U128`
- `DynType.I8`, `I16`, `I32`, `I64`, `I128`
- `DynType.BOOL`, `DynType.STRING`
- `FixedArray(inner_type, length)` — fixed-size arrays
- `DynArray(inner_type)` — variable-length arrays

### Get Arrow Schema

```python
from tiders_core import instruction_signature_to_arrow_schema

schema = instruction_signature_to_arrow_schema(signature)
```

## Rust API

See the [tiders_svm_decode rustdoc](../api/tiders_svm_decode/index.html) for the full API.
