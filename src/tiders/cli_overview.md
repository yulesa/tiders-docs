# CLI Overview (No-Code Mode)

The tiders CLI lets you run a complete blockchain data pipeline from a single YAML config file — no Python required.

```bash
tiders start config.yaml
```

## How it works

The CLI maps 1:1 to the Python SDK — it parses the YAML into the same Python objects and calls the same `run_pipeline()` function:

1. **Parse** — load the YAML file and substitute `${ENV_VAR}` placeholders
2. **Build** — construct `ProviderConfig`, `Query`, `Step`s, and `Writer` from the config sections
3. **Run** — call `run_pipeline()`, identical to Python-mode execution

## Commands

### `tiders start`

Run a pipeline from a YAML config file.

```
tiders start [CONFIG_PATH] [OPTIONS]

Arguments:
  CONFIG_PATH          Path to the YAML config file (optional, default to use the YAML files in the folder)

Options:
  --from-block INTEGER  Override the starting block number from the config
  --to-block   INTEGER  Override the ending block number from the config
  --env-file   PATH     Path to a .env file (overrides default discovery)
  --help                Show this message and exit
  --version             Show the tiders version and exit
```

### `tiders codegen`

Generate a standalone Python script from a YAML config file. The generated script constructs and runs the same pipeline using the tiders Python SDK — useful as a starting point when you need to customize beyond what YAML supports.

```
tiders codegen [CONFIG_PATH] [OPTIONS]

Arguments:
  CONFIG_PATH          Path to the YAML config file (optional, same discovery rules as start)

Options:
  -o, --output PATH    Output file path (defaults to <ProjectName>.py in the current directory)
  --env-file   PATH    Path to a .env file (overrides default discovery)
  --help               Show this message and exit
```

The output filename is derived from the `project.name` field in the YAML, converted to snake_case (e.g. `ERC20 Transfers` becomes `erc20_transfers.py`).

Environment variables referenced in the YAML (e.g. `${PROVIDER_URL}`) are emitted as `os.environ.get("PROVIDER_URL")` calls in the generated script, so secrets stay out of the code.

### `tiders abi`

Fetch contract ABIs from [Sourcify](https://sourcify.dev/) or [Etherscan](https://etherscan.io/) and save them as JSON files. 

```
tiders abi [OPTIONS]

Options:
  --address TEXT               Contract address (single-address mode)
  --chain-id TEXT              Chain ID or name (default: 1). See supported chains below
  --yaml-path PATH             Path to YAML file with contract declarations
  -o, --output PATH            Output path. Single-address mode: file path. YAML mode: directory
  --source [sourcify|etherscan] ABI source to try first (default: sourcify). Falls back to the other
  --env-file PATH              Path to a .env file (overrides default discovery)
  --help                       Show this message and exit
```

#### Usage modes

**1. Single address** — fetch one ABI by contract address:

```bash
tiders abi --address 0xae78736Cd615f374D3085123A210448E74Fc6393
tiders abi --address 0xae78736Cd615f374D3085123A210448E74Fc6393 --chain-id base
```

**2. From YAML file** — fetch ABIs for all contracts declared in the YAML:

```bash
tiders abi --yaml-path pipeline.yaml #(optional, autodiscobery in current directory)
```

The `--chain-id` option in CLI or in the YAML config accept either a numeric chain ID or a chain name in some chains:

| Name | Chain ID |
|------|----------|
| `ethereum`, `mainnet`, `ethereum-mainnet` | 1 |
| `bnb` | 56 |
| `base` | 8453 |
| `arbitrum` | 42161 |
| `polygon` | 137 |
| `scroll` | 534352 |
| `unichain` | 130 |

Set `ETHERSCAN_API_KEY` in your environment or via .env file. Etherscan is skipped with a warning if not set.


## Environment variables

Secrets and dynamic values are kept out of the YAML using `${VAR}` placeholders:

```yaml
provider:
  kind: hypersync
  url: ${PROVIDER_URL}
  bearer_token: ${HYPERSYNC_BEARER_TOKEN}
```

The CLI automatically loads a `.env` file from the same directory as the config file before substitution. Use `--env-file` to point to a different location:

```bash
tiders start --env-file /path/to/.env config.yaml
```

An error is raised if any `${VAR}` placeholder remains unresolved after substitution.

See the [CLI YAML Reference](./cli_yaml_reference.md) for full details on all sections.
