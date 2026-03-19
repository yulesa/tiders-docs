# Your First Pipeline

This tutorial builds a pipeline that fetches ERC-20 transfer events from Ethereum and writes them to DuckDB.

## Pipeline Anatomy

Every tiders pipeline has five parts:

1. **Contracts** — optional, helper for contract information 
2. **Provider** — where to fetch data from
3. **Query** — what data to fetch
4. **Steps** — transformations to apply
5. **Writer** — where to write the output

## Step 1: Define the Contracts

Contracts is an optional module that makes it easier to get contract information, such as Events, Functions and their params.

Use evm_abi_events and evm_abi_functions from tiders_core. These functions take a JSON ABI string and return a list[EvmAbiEvent] / list[EvmAbiFunction] with the fields described above.

```python
from pathlib import Path
from tiders_core import evm_abi_events, evm_abi_functions

erc20_address = '0xae78736Cd615f374D3085123A210448E74Fc6393'  # rETH token contract

erc20_abi_path = Path('/home/yulesa/repos/tiders/examples/first_pipeline/erc20.abi.json')
erc20_abi_json = erc20_abi_path.read_text()

# Build a dict of events keyed by name, e.g. erc20_events["Transfer"]["topic0"]
erc20_events = {
    ev.name: {
        'topic0': ev.topic0,
        'signature': ev.signature,
        'name_snake_case': ev.name_snake_case,
        'selector_signature': ev.selector_signature,
    }
    for ev in evm_abi_events(erc20_abi_json)}

# Build a dict of functions keyed by name, e.g. erc20_functions["approve"]["selector"]
erc20_functions = {
    fn.name: {
        'selector': fn.selector,
        'signature': fn.signature,
        'name_snake_case': fn.name_snake_case,
        'selector_signature': fn.selector_signature,
    }
    for fn in evm_abi_functions(erc20_abi_json)}
```

## Step 2: Define the Provider

```python
from tiders_core.ingest import ProviderConfig, ProviderKind

provider = ProviderConfig(
    kind=ProviderKind.RPC,
    url='https://mainnet.gateway.tenderly.co',
)
```

Available providers: `HYPERSYNC`, `SQD`, `RPC`.

## Step 3: Define the Query

The query defines what data to fetch: block range, filters, and fields.

```python
from tiders_core.ingest import Query, QueryKind
from tiders_core.ingest import evm

query = Query(
    kind=QueryKind.EVM,
    params=evm.Query(
        from_block=18000000,
        to_block=18000100,
        logs=[evm.LogRequest(topic0=[erc20_events["Transfer"]["topic0"]])],
        fields=evm.Fields(
            log=evm.LogFields(
                log_index=True,
                transaction_hash=True,
                block_number=True,
                address=True,
                data=True,
                topic0=True,
                topic1=True,
                topic2=True,
                topic3=True,
            ),
        ),
    ),
)
```

## Step 4: Add Transformation Steps

Steps are transformations applied to the raw data before writing. They run in order, each step's output feeding into the next.

STEP 1 - EVM_DECODE_EVENTS: 

Decodes the raw log data (topic1..3 + data) into named columns using the event signature.
  - allow_decode_fail: if True, rows that fail to decode are kept (with nulls)
  - hstack: if False, outputs only decoded columns; if True, append them to the original raw log columns

STEP 2 - HEX_ENCODE: 

Converts binary columns (addresses, hashes) to hex strings, making them human-readable and compatible with databases like DuckDB.

```python
from tiders.config import EvmDecodeEventsConfig, HexEncodeConfig, Step, StepKind

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

## Step 5: Configure the Writer

The writer defines where transformed data is stored. DuckDB creates a local database file. Other options include ClickHouse, Delta Lake, Iceberg, PostgreSQL, PyArrow Dataset (Parquet), and CSV.

```python
from tiders.config import DuckdbWriterConfig, Writer, WriterKind

writer = Writer(
    kind=WriterKind.DUCKDB,
    config=DuckdbWriterConfig(path='data/transfers.duckdb'),
)
```

## Step 6: Run the Pipeline

The Pipeline ties all parts together. run_pipeline() executes the full ingestion: fetch -> transform -> write.

```python
import asyncio
from tiders import run_pipeline
from tiders.config import Pipeline

pipeline = cc.Pipeline(
    provider=provider,
    query=query,
    writer=writer,
    steps=steps,
)

asyncio.run(run_pipeline(pipeline=pipeline))
```

## Verify the Output

Verify the output by querying the DuckDB file using duckdb-cli:

```bash
duckdb data/transfers.db
```

```sql
SHOW TABLES;
SELECT * FROM transfers LIMIT 5;
```

## Next Steps

- Learn about all available [providers](../tiders/providers.md)
- See the full list of [transformation steps](../tiders/steps.md)
- Explore more [examples](../tiders/examples.md)
