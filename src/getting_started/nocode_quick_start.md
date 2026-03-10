# No-Code Quick Start

Run a blockchain data pipeline without writing Python — just a YAML config file.

## 1. Install

```bash
pip install "tiders[duckdb]"
```

## 2. Create a config file

Create `tiders.yaml`:

```yaml
project:
  name: erc20_transfers
  description: Fetch ERC-20 Transfer events and write to DuckDB.

provider:
  kind: rpc
  url: ${PROVIDER_URL}

query:
  kind: evm
  from_block: 18000000
  to_block: 18000100
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
      output_table: transfers_raw
      allow_decode_fail: true
  - kind: hex_encode

writer:
  kind: duckdb
  config:
    path: data/transfers.duckdb
```

## 3. Environment Variables

Use `${VAR_NAME}` placeholders anywhere in the YAML to keep secrets and environment-specific values out of your config file. This works for any string field — provider URLs, credentials, file paths, etc.

```yaml
provider:
  kind: rpc
  url: ${PROVIDER_URL}
  bearer_token: ${PROVIDER_BEARER_TOKEN}
```

At startup, the CLI automatically loads a `.env` file from the same directory as the config file, then substitutes all `${VAR_NAME}` placeholders with their values. If a variable is referenced in the YAML but not defined, the CLI raises an error.

Create a `.env` file alongside your config:

```bash
PROVIDER_URL=https://mainnet.gateway.tenderly.co
PROVIDER_BEARER_TOKEN=12345678
```

You can also point to a different `.env` file using the `--env-file` flag:

```bash
tiders start --env-file /path/to/.env tiders.yaml
```

## 4. Run

```bash
tiders start
```

The CLI auto-discovers `tiders.yaml` in the current directory. However, you can also pass a path explicitly:

```bash
tiders start path/tiders.yaml
```

## Next steps

- [CLI Overview](../tiders/cli_overview.md) — CLI flags, env var substitution, config auto-discovery
- [CLI YAML Reference](../tiders/cli_yaml_reference.md) — full reference for all YAML sections
- [rETH Transfer Example](../tiders/examples/reth_transfer.md) — complete annotated example
