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
  url: "https://mainnet.gateway.tenderly.co" # or change to read from the .env file ${PROVIDER_URL}

contracts:
  - name: erc20
    address: "0xae78736Cd615f374D3085123A210448E74Fc6393" # rETH contract, we need a erc20 reference to download the ABI.
    # An abi: ./erc20.abi.json config will be added after using CLI command `tiders abi` in this folder

query:
  kind: evm
  from_block: 18000000
  to_block: 18000100
  logs:
    - topic0: erc20.Events.Transfer.topic0
  fields:
    log: [address, topic0, topic1, topic2, topic3, data, block_number, transaction_hash, log_index]

steps:
  - kind: evm_decode_events
    config:
      event_signature: erc20.Events.Transfer.signature
      output_table: transfers
      allow_decode_fail: true
      hstack: false
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

## 4. Download ABIs

Tiders CLI provides a command to make it easy to download ABIs defined in the YAML file and save them in the folder.

```bash
tiders abi
```

## 5. Run

```bash
tiders start
```

The CLI auto-discovers `tiders.yaml` in the current directory. However, you can also pass a path explicitly:

```bash
tiders start path/tiders.yaml
```

## 5. Generate a Python script (optional)

Once your YAML pipeline is working, you can generate an equivalent Python script using `tiders codegen`:

```bash
tiders codegen
```

This reads the same YAML file and outputs a standalone Python script that constructs and runs the same pipeline using the tiders Python SDK. By default, the output file is named after the project in snake_case (e.g. `erc20_transfers.py`). You can specify a custom output path with `-o`:

```bash
tiders codegen -o my_pipeline.py
```

This is useful when you want to move beyond YAML and customize the pipeline logic in Python — for example, adding custom transformation steps, conditional logic, or integrating with other libraries.

## Next steps

- [CLI Overview](../tiders/cli_overview.md) — CLI commands, flags, env var substitution, config auto-discovery
- [CLI YAML Reference](../tiders/cli_yaml_reference.md) — full reference for all YAML sections
- [rETH Transfer Example](../tiders/examples/reth_transfer.md) — complete annotated example
