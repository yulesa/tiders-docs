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

## CLI flags

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

## Config auto-discovery

If `CONFIG_PATH` is omitted, the CLI searches the current directory in this order:

1. `tiders.yaml`
2. `tiders.yml`
3. Any `.yaml` / `.yml` file that contains both `provider:` and `query:` keys

An error is raised if zero or multiple candidates are found.

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
