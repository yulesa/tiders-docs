# rETH Transfers (No-Code)

This example indexes `Transfer` events from the [Rocket Pool rETH](https://etherscan.io/token/0xae78736cd615f374d3085123a210448e74fc6393) token contract using a YAML config — no Python required.

**Source:** [examples/reth_transfer_nocode/](https://github.com/yulesa/tiders/tree/main/examples/reth_transfer_nocode)

## Run

```bash
cd examples/reth_transfer_nocode
cp .env.example .env
# Fill PROVIDER_URL and HYPERSYNC_BEARER_TOKEN in .env
tiders start
```

## What it does

1. **Queries** logs matching the `Transfer` event from the rETH contract via HyperSync
2. **Decodes** the raw log data into typed `from`, `to`, and `amount` columns
3. **Casts** `decimal256` to `decimal128` for compatibility
4. **Hex-encodes** binary fields for readability
5. **Joins** transfer data with block timestamps via SQL
6. **Writes** to a Delta Lake table

## Full config

```yaml
project:
  name: rETH_transfer
  description: Index rETH Transfer events from the Rocket Pool rETH token contract.
  repository: https://github.com/yulesa/tiders/example/reth_transfer_nocode

provider:
  kind: hypersync
  url: ${PROVIDER_URL}
  bearer_token: ${HYPERSYNC_BEARER_TOKEN}

contracts:
  - name: RocketTokenRETH
    address: 0xae78736Cd615f374D3085123A210448E74Fc6393
    abi: ./RocketTokenRETH.abi.json

query:
  kind: evm
  from_block: 13325304
  to_block: 13325404
  logs:
    - topic0: "Transfer(address,address,uint256)"
      include_blocks: true
  fields:
    log: [address, topic0, topic1, topic2, topic3, data, block_number, transaction_hash, log_index]
    block: [number, timestamp]

steps:
  - kind: evm_decode_events
    config:
      event_signature: "Transfer(address indexed from, address indexed to, uint256 amount)"
      output_table: transfers
      allow_decode_fail: true

  - kind: cast_by_type
    name: i256_to_i128
    config:
      from_type: "decimal256(76,0)"
      to_type: "decimal128(38,0)"
      allow_cast_fail: true

  - kind: hex_encode

  - kind: sql
    config:
      queries:
        - >
          SELECT transfers.*, blocks.timestamp AS block_timestamp
          FROM transfers
          INNER JOIN blocks ON blocks.number = transfers.block_number

writer:
  kind: delta_lake
  config:
    data_uri: data/pyarrow
```

## Key concepts

**Contract references** — the `contracts:` section loads `RocketTokenRETH.abi.json` and makes the contract available by name. `topic0: "Transfer(address,address,uint256)"` is a human-readable event signature; the CLI converts it to a Keccak-256 hash automatically.

**Decode step** — `evm_decode_events` reads the raw `topic1`, `topic2`, and `data` columns and produces typed `from`, `to`, and `amount` columns in a new `transfers` table.

**Cast step** — EVM `uint256` values are decoded as `decimal256(76,0)`. The `cast_by_type` step downcasts them to `decimal128(38,0)` for Delta Lake compatibility.

**SQL step** — the `sql` step runs DataFusion SQL against the in-memory tables. Both `transfers` and `blocks` are available because `include_blocks: true` was set on the log request.

**Environment variables** — credentials stay in `.env` and are referenced as `${PROVIDER_URL}` in the YAML. The CLI loads `.env` automatically from the config directory.
