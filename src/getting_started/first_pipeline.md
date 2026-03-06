# Your First Pipeline

This tutorial builds a pipeline that fetches ERC-20 transfer events from Ethereum and writes them to DuckDB.

## Pipeline Anatomy

Every tiders pipeline has four parts:

1. **Provider** — where to fetch data from
2. **Query** — what data to fetch
3. **Steps** — transformations to apply
4. **Writer** — where to write the output

## Step 1: Define the Provider

```python
from tiders_core import ingest

provider = ingest.ProviderConfig(
    kind=ingest.ProviderKind.HYPERSYNC,
    url="https://eth.hypersync.xyz",
)
```

Available providers: `HYPERSYNC`, `SQD`, `RPC`.

## Step 2: Define the Query

```python
from tiders_core import evm_signature_to_topic0

query = ingest.Query(
    kind=ingest.QueryKind.EVM,
    params=ingest.evm.Query(
        from_block=18_000_000,
        logs=[
            ingest.evm.LogRequest(
                topic0=[
                    evm_signature_to_topic0("Transfer(address,address,uint256)")
                ],
                include_blocks=True,
            )
        ],
        fields=ingest.evm.Fields(
            block=ingest.evm.BlockFields(number=True, timestamp=True),
            log=ingest.evm.LogFields(
                block_number=True,
                transaction_hash=True,
                log_index=True,
                address=True,
                topic0=True,
                topic1=True,
                topic2=True,
                topic3=True,
                data=True,
            ),
        ),
    ),
)
```

## Step 3: Add Transformation Steps

```python
from tiders import config as cc

steps = [
    # Decode the raw log data into typed columns
    cc.Step(
        kind=cc.StepKind.EVM_DECODE_EVENTS,
        config=cc.EvmDecodeEventsConfig(
            event_signature="Transfer(address indexed from, address indexed to, uint256 amount)",
            output_table="transfers",
            allow_decode_fail=True,
        ),
    ),
    # Hex-encode binary fields for readable output
    cc.Step(
        kind=cc.StepKind.HEX_ENCODE,
        config=cc.HexEncodeConfig(),
    ),
]
```

## Step 4: Configure the Writer

```python
import duckdb

connection = duckdb.connect(database="./data/transfers.db")

writer = cc.Writer(
    kind=cc.WriterKind.DUCKDB,
    config=cc.DuckdbWriterConfig(
        connection=connection.cursor(),
    ),
)
```

## Step 5: Run the Pipeline

```python
import asyncio
from tiders import run_pipeline

pipeline = cc.Pipeline(
    provider=provider,
    query=query,
    writer=writer,
    steps=steps,
)

asyncio.run(run_pipeline(pipeline=pipeline))
```

## Verify the Output

```bash
duckdb data/transfers.db
```

```sql
SELECT * FROM transfers LIMIT 5;
```

## Next Steps

- Learn about all available [providers](../tiders/providers.md)
- See the full list of [transformation steps](../tiders/steps.md)
- Explore more [examples](../tiders/examples.md)
