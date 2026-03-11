# Development Setup

To develop locally across all repos, clone all three projects side by side:

```bash
git clone https://github.com/yulesa/tiders.git
git clone https://github.com/yulesa/tiders-core.git
git clone https://github.com/yulesa/tiders-rpc-client.git
```

## Building `tiders-core` and `tiders-rpc-client` from source

If you're modifying `tiders-rpc-client` repo locally, you probably want `tiders-core` to build against your local version.

Build `tiders-rpc-client` locally:
```bash
cd tiders-rpc-client/rust
cargo build
```

Use local `tiders-rpc-client`to build `tiders-core`, overriding the crates.io version:

```bash
cd tiders-core
# Build Rust crates with local tiders-rpc-client
cargo build --config 'patch.crates-io.tiders-rpc-client.path="../tiders-rpc-client/rust"'

# Build Python bindings with the same patch
cd python
maturin develop --config 'patch.crates-io.tiders-rpc-client.path="../../tiders-rpc-client/rust"'
# If using uv
maturin develop --uv --config 'patch.crates-io.tiders-rpc-client.path="../../tiders-rpc-client/rust"'
```

If you're modifying `tiders-core` repo locally, you probably want `tiders` to use your local `tiders-core` version.

Build `tiders-core` as described above, or just `cargo build` if you haven't modified tiders-rpc-client.

Use local `tiders-core` in your enviroment, overriding the PyPI version:

```bash
cd tiders
pip install -e ".[all]"
# If using uv
uv pip install -e ".[all]"
```


## Persistent local development

For persistent local development, you can put this in `tiders-core/Cargo.toml`:

```toml
[patch.crates-io]
tiders-rpc-client = { path = "../tiders-rpc-client/rust" }
```

This avoids passing `--config` on every build command.

Configure `tiders` to use your local `tiders-core` Python package:

```toml
[tool.uv.sources]
tiders-core = { path = "../tiders-core/python", editable = true }
```

```bash
cd tiders
uv sync
```

