# Uniswap V3 (Factory + Children Pattern)

This example demonstrates the factory + children indexing pattern — one of the most common patterns in crypto data engineering. A Factory contract deploys child contracts (pools) on-chain. To index them you first index the factory to discover the children and then index their events. This pattern applies to Uniswap (V2/V3), Aave, Compound, Curve, and many other DeFi protocols.

**Source:** [examples/uniswap_v3/](https://github.com/yulesa/tiders/tree/main/examples/uniswap_v3)

## Run

```bash
cd examples/uniswap_v3
cp .env.example .env
uv run uniswap_v3.py --provider <hypersync|sqd|rpc> --from_block 12369621 --to_block 12370621
#  [--rpc_url URL]    \  # only needed with --provider rpc
#  [--database BACKEND]  # default: pyarrow. Options: pyarrow, duckdb, delta_lake, clickhouse, iceberg
```

## Pipeline Overview

This example runs two pipelines sequentially:

**Stage 1 — Discover pools from the Factory:**

1. **Queries** `PoolCreated` logs from the [Uniswap V3 Factory](https://etherscan.io/address/0x1f98431c8ad98523631ae4a59f267346ea31f984) contract
2. **Decodes** raw log data into typed columns (`token0`, `token1`, `fee`, `tickSpacing`, `pool`)

**Stage 2 — Index events from discovered pools:**

1. **Reads** pool addresses from the Stage 1 output (plain Python, not a Tiders feature)
2. **Queries** ALL logs emitted by those pool addresses (no topic filter — fetches every event type)
3. **Decodes** each known pool event (Swap, Mint, Burn, Flash, etc.) into its own output table
6. **Writes** all decoded event tables to the chosen backend

## ABI Setup

`evm_abi_events()` parses an ABI JSON file and returns event descriptors. We build a dict keyed by event name for easy access to events params.

The same pattern is used for pool events. Both ABI JSON files are included in the example directory.

```python
factory_events = {
    ev.name: {
        "topic0": ev.topic0,
        "signature": ev.signature,
        "name_snake_case": ev.name_snake_case,
        "selector_signature": ev.selector_signature,
    }
    for ev in evm_abi_events(_FACTORY_ABI_JSON)
}
```

## Stage 1 — Pool Discovery Pipeline

### Query

Fetches logs from the Factory contract address, filtered by the `PoolCreated` topic0 hash. The `fields` parameter selects which log columns to include.

```python
query = ingest.Query(
    kind=ingest.QueryKind.EVM,
    params=ingest.evm.Query(
        from_block=from_block,
        to_block=to_block,
        logs=[
            ingest.evm.LogRequest(
                address=[UNISWAP_V3_FACTORY],
                topic0=[factory_events["PoolCreated"]["topic0"]],
            )
        ],
        fields=ingest.evm.Fields(
            log=ingest.evm.LogFields(
                block_number=True, block_hash=True,
                transaction_hash=True, log_index=True,
                address=True, topic0=True, topic1=True,
                topic2=True, topic3=True, data=True,
            ),
        ),
    ),
)
```

### Steps

1. **`EVM_DECODE_EVENTS`** — Decodes the raw `PoolCreated` log into typed columns: `token0`, `token1`, `fee`, `tickSpacing`, and `pool`. The decoded output goes into a new `uniswap_v3_pool_created` table.
2. **`HEX_ENCODE`** — Converts all binary columns to `0x…` hex strings.

```python
steps = [
    cc.Step(
        kind=cc.StepKind.EVM_DECODE_EVENTS,
        config=cc.EvmDecodeEventsConfig(
            event_signature=factory_events["PoolCreated"]["signature"],
            input_table=POOL_CREATED_LOGS_TABLE,
            output_table=POOL_CREATED_TABLE,
            allow_decode_fail=False,
        ),
    ),
    cc.Step(
        kind=cc.StepKind.HEX_ENCODE,
        config=cc.HexEncodeConfig(),
    ),
]
```
Tiders ingests raw EVM logs into a default `logs` table. `table_aliases` renames it so the decode step can reference it by a descriptive name


## Bridging Stages

After Stage 1 writes the decoded pool data, we read back the pool addresses using plain Python. Tiders doesn't prescribe how you connect pipeline stages — use whatever method fits your storage backend:

```python
pool_addresses = await load_pool_addresses(database)
```

## Stage 2 — Pool Events Pipeline

### Query

Re-queries the same block range, but now filtered to the discovered pool addresses. No topic filter — we want ALL events from these pools:

```python
query = ingest.Query(
    kind=ingest.QueryKind.EVM,
    params=ingest.evm.Query(
        from_block=from_block,
        to_block=to_block,
        logs=[
            ingest.evm.LogRequest(
                address=pool_addresses,
            )
        ],
        ...
    ),
)
```

### Steps

A decode step is created dynamically for each event in the pool contracts. Each event gets decoded from the shared raw logs table into its own output table (e.g., `uniswap_v3_pool_swap`, `uniswap_v3_pool_mint`).

```python
for _, event in pool_events.items():
    output_table = f"uniswap_v3_pool_{event['name_snake_case']}"
    steps.append(
        cc.Step(
            kind=cc.StepKind.EVM_DECODE_EVENTS,
            config=cc.EvmDecodeEventsConfig(
                event_signature=event["signature"],
                input_table=POOL_EVENTS_TABLE,
                output_table=output_table,
                allow_decode_fail=True,
                filter_by_topic0=True,
            ),
        ),
    )
```

- **`filter_by_topic0=True`** — only attempts to decode logs whose topic0 matches this event's signature, since the raw table contains mixed event types.
- **`allow_decode_fail=True`** — skips logs that don't match the expected format without raising errors.

After decoding, a **`CAST_BY_TYPE`** step downcasts `decimal256` to `decimal128`, and **`HEX_ENCODE`** converts binary fields to hex strings.

## Key Concepts

**Factory + children pattern** — The most common multi-stage indexing pattern in DeFi. Stage 1 reads the factory to discover child contracts; Stage 2 indexes the children. This same approach works for any protocol with factory-deployed contracts (Uniswap V2 pairs, Aave markets, Compound cTokens, etc.).

**Table aliases** — Tiders names raw ingested tables generically (`logs`, `blocks`, etc.). Use `table_aliases` to give them descriptive names per pipeline, which is especially important when running multiple pipelines that write to the same database.

**Dynamic decode steps** — Instead of hardcoding a decode step for each event, this example loops over all events in the pool ABI and creates a step for each. This keeps the pipeline maintainable as ABIs evolve.

**Cast step** — EVM `int256`/`uint256` values are decoded as `decimal256(76,0)`. The `cast_by_type` step downcasts to `decimal128(38,0)` for databases that don't support 256-bit decimals. This step is dispensable in PyArrow datasets (Parquet).
