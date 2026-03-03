# RPC Pipeline

This example fetches blocks, transactions, and logs directly from an Ethereum RPC endpoint and writes them to Parquet files.

**Source:** [examples/rpc_pipeline.py](https://github.com/yulesa/tiders/blob/main/examples/rpc_pipeline.py)

## Run

```bash
# Uses default public RPC endpoint
uv run examples/rpc_pipeline.py

# Or specify your own RPC URL
uv run examples/rpc_pipeline.py https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY

# Or set via environment variable
RPC_URL=https://your-rpc-url uv run examples/rpc_pipeline.py
```

## What It Does

1. **Connects** to any standard EVM JSON-RPC endpoint
2. **Fetches** blocks 18,000,000 to 18,000,100 with transactions and logs
3. **Hex-encodes** binary fields
4. **Writes** to Parquet files in `data/`

## Key Code

### RPC Provider Configuration

```python
provider = ingest.ProviderConfig(
    kind=ingest.ProviderKind.RPC,
    url=url,
    stop_on_head=True,
    batch_size=10,
)
```

### Query with Transactions and Related Data

```python
query = ingest.Query(
    kind=ingest.QueryKind.EVM,
    params=ingest.evm.Query(
        from_block=18_000_000,
        to_block=18_000_100,
        transactions=[
            ingest.evm.TransactionRequest(
                include_blocks=True,
                include_logs=True,
            ),
        ],
        fields=ingest.evm.Fields(
            block=ingest.evm.BlockFields(
                number=True, hash=True, timestamp=True, gas_used=True,
            ),
            transaction=ingest.evm.TransactionFields(
                hash=True, from_=True, to=True, value=True, gas_used=True,
            ),
            log=ingest.evm.LogFields(
                block_number=True, address=True, topic0=True, data=True,
            ),
        ),
    ),
)
```

### Parquet Writer

```python
writer = cc.Writer(
    kind=cc.WriterKind.PYARROW_DATASET,
    config=cc.PyArrowDatasetWriterConfig(base_dir="./data"),
)
```

## Output

After running, Parquet files are written to `data/blocks/`, `data/transactions/`, and `data/logs/`.
