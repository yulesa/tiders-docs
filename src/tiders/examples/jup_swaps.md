# Jupiter Swaps (SVM)

This example builds a Solana indexer that fetches Jupiter DEX swap instructions, decodes them into typed fields, joins with block and transaction data using Polars, and writes enriched swap analytics to DuckDB.

**Source:** [examples/jup_swap/jup_swap.py](https://github.com/yulesa/tiders/blob/main/examples/jup_swap/jup_swap.py)

## Run

```bash
uv run jup_swap.py --from_block 330447751 --to_block 330448751
```

## Pipeline Overview

1. **Queries** Solana instructions filtered by Jupiter program ID (`JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4`) and swap event discriminator (`0xe445a52e51cb9a1d40c6cde8260871e2`), along with related blocks and transactions
2. **Decodes** instruction data into typed swap fields (AMM, input/output mints, amounts) using `InstructionSignature`
3. **Joins** block and transaction data into the decoded instructions table via a custom Polars step
4. **Base58-encodes** binary fields (public keys, hashes) into human-readable strings
5. **Writes** to DuckDB
6. **Enriches** with token metadata and AMM names via DuckDB post-processing SQL

## Provider

Connects to the SQD portal network for Solana mainnet data:

```python
provider = ProviderConfig(
    kind=ProviderKind.SQD,
    url="https://portal.sqd.dev/datasets/solana-mainnet",
)
```

## Query

The query fetches instructions, blocks, and transactions for a given block range. Field selection controls which columns are returned per table, minimizing bandwidth. The `InstructionRequest` filters rows to only Jupiter swap events by `program_id=["JUP…4"]` and `discriminator=["0xe4…e2"]`. Setting `include_transactions=True` pulls in the transaction table for matching instructions, and `include_all_blocks=True` returns all blocks in the range regardless of matches.

```python
query = IngestQuery(
    kind=QueryKind.SVM,
    params=Query(
        from_block=from_block,
        to_block=actual_to_block,
        include_all_blocks=True,
        fields=Fields(
            instruction=InstructionFields(
                block_slot=True,
                block_hash=True,
                transaction_index=True,
                instruction_address=True,
                program_id=True,
                a0=True, a1=True, a2=True, a3=True, a4=True,
                a5=True, a6=True, a7=True, a8=True, a9=True,
                data=True,
                error=True,
            ),
            block=BlockFields(
                slot=True,
                hash=True,
                timestamp=True,
            ),
            transaction=TransactionFields(
                block_slot=True,
                block_hash=True,
                transaction_index=True,
                signature=True,
            ),
        ),
        instructions=[
            InstructionRequest(
                program_id=["JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"],
                discriminator=["0xe445a52e51cb9a1d40c6cde8260871e2"],
                include_transactions=True,
            )
        ],
    ),
)
```

## Instruction Signature

Defines the layout of the Jupiter Aggregator v6 `SwapEvent` instruction data. The discriminator identifies the instruction type, and `params` describes the binary layout: three 32-byte public keys (AMM, InputMint, OutputMint) and two u64 amounts. Signatures can be sourced from IDLs, SolScan, or contract source code.

For more information read the [instructions signatures](../steps.md#instruction-signature) documentation.

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

## Transformation Steps

Steps are executed sequentially. Each step receives the transformed output of the previous one.

1. **`SVM_DECODE_INSTRUCTIONS`** — Decodes raw instruction `data` using the signature above. `hstack=True` appends decoded columns alongside the original fields. `allow_decode_fail=True` keeps rows that fail to decode. The output is written to a new table `jup_swaps_decoded_instructions`.
2. **`POLARS` (custom step)** — Runs a user-defined function that joins block timestamps and transaction signatures into the decoded instructions table using Polars DataFrames.
3. **`BASE58_ENCODE`** — Converts all binary columns (public keys, hashes) to base58 strings.

*obs: Tiders has available `JOIN_BLOCK_DATA` and `JOIN_SVM_TRANSACTION_DATA` steps to make joins effortlessly. We are using custom polars funtions to set an example.*

```python
steps = [
    cc.Step(
        kind=cc.StepKind.SVM_DECODE_INSTRUCTIONS,
        config=cc.SvmDecodeInstructionsConfig(
            instruction_signature=instruction_signature,
            hstack=True,
            allow_decode_fail=True,
            output_table="jup_swaps_decoded_instructions",
        ),
    ),
    cc.Step(
        kind=cc.StepKind.POLARS,
        config=cc.PolarsStepConfig(runner=process_data),
    ),
    cc.Step(
        kind=cc.StepKind.BASE58_ENCODE,
        config=cc.Base58EncodeConfig(),
    ),
]
```

### Custom Polars Step

The `process_data` function joins block and transaction tables into the decoded instructions table. The blocks join brings in `timestamp`; the transactions join brings in `signature`.

```python
def process_data(
    data: dict[str, pl.DataFrame], ctx: Optional[Any]
) -> dict[str, pl.DataFrame]:
    table = data["jup_swaps_decoded_instructions"]
    table = table.join(data["blocks"], left_on="block_slot", right_on="slot")
    table = table.join(data["transactions"], on=["block_slot", "transaction_index"])
    return {"jup_swaps_decoded_instructions": table}
```

## Writer

Writes the pipeline output to a local DuckDB database:

```python
connection = duckdb.connect("data/solana_swaps.db")

writer = cc.Writer(
    kind=cc.WriterKind.DUCKDB,
    config=cc.DuckdbWriterConfig(
        connection=connection.cursor(),
    ),
)
```

## Running the Pipeline

```python
pipeline = cc.Pipeline(
    provider=provider,
    query=query,
    writer=writer,
    steps=steps,
)
await run_pipeline(pipeline_name="jup_swaps", pipeline=pipeline)
```

## Post-Pipeline Analytics

After the pipeline writes `jup_swaps_decoded_instructions` to DuckDB, a SQL post-processing step enriches the data with token metadata and AMM names from CSV lookup tables, producing a `jup_swaps` table similar to a `dex.trades` analytics table:

```sql
CREATE OR REPLACE TABLE solana_amm AS
    SELECT * FROM read_csv('./solana_amm.csv');
CREATE OR REPLACE TABLE solana_tokens AS
    SELECT * FROM read_csv('./solana_tokens.csv');
CREATE OR REPLACE TABLE jup_swaps AS
    SELECT
        di.amm AS amm,
        sa.amm_name AS amm_name,
        case when di.inputmint > di.outputmint
            then it.token_symbol || '-' || ot.token_symbol
            else ot.token_symbol || '-' || it.token_symbol
            end as token_pair,
        it.token_symbol as input_token,
        di.inputmint AS input_token_address,
        di.inputamount AS input_amount_raw,
        it.token_decimals AS input_token_decimals,
        di.inputamount / 10^it.token_decimals AS input_amount,
        ot.token_symbol as output_token,
        di.outputmint AS output_token_address,
        di.outputamount AS output_amount_raw,
        ot.token_decimals AS output_token_decimals,
        di.outputamount / 10^ot.token_decimals AS output_amount,
        di.block_slot AS block_slot,
        di.transaction_index AS transaction_index,
        di.instruction_address AS instruction_address,
        di.timestamp AS block_timestamp
    FROM jup_swaps_decoded_instructions di
    LEFT JOIN solana_amm sa ON di.amm = sa.amm_address
    LEFT JOIN solana_tokens it ON di.inputmint = it.token_address
    LEFT JOIN solana_tokens ot ON di.outputmint = ot.token_address;
```

## Output

```sql
SELECT * FROM jup_swaps_decoded_instructions LIMIT 3;
SELECT * FROM jup_swaps LIMIT 3;
```
