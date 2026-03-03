# Jupiter Swaps (SVM)

This example fetches Jupiter swap instructions from Solana, decodes them, and writes to DuckDB with enriched token metadata.

**Source:** [examples/jup_swap.py](https://github.com/yulesa/tiders/blob/main/examples/jup_swap.py)

## Run

```bash
uv run examples/jup_swap.py --from_block 330447751 --to_block 330447751
```

## What It Does

1. **Queries** Solana instructions from the Jupiter program (`JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4`)
2. **Decodes** instruction data into typed swap fields (AMM, input/output mints, amounts)
3. **Joins** with block and transaction data using Polars
4. **Base58-encodes** binary fields
5. **Enriches** with token and AMM metadata using DuckDB post-processing
6. **Writes** to DuckDB

## Key Code

### Instruction Signature Definition

```python
from tiders_core.svm_decode import InstructionSignature, ParamInput, DynType, FixedArray

instruction_signature = InstructionSignature(
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
```

### Custom Polars Step

```python
def process_data(data: dict[str, pl.DataFrame], ctx) -> dict[str, pl.DataFrame]:
    table = data["jup_swaps_decoded_instructions"]
    table = table.join(data["blocks"], left_on="block_slot", right_on="slot")
    table = table.join(data["transactions"], on=["block_slot", "transaction_index"])
    return {"jup_swaps_decoded_instructions": table}
```

## Output

```sql
SELECT * FROM jup_swaps LIMIT 3;
```
