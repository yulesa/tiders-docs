# Development Setup

To develop locally across all repos, clone all three projects side by side:

```bash
git clone https://github.com/yulesa/tiders.git
git clone https://github.com/yulesa/tiders-core.git
git clone https://github.com/yulesa/tiders-rpc-client.git
```

## Building `tiders-core` and `tiders-rpc-client` from source

If you're modifying this repo locally, you probably want `tiders-core` to build against your local version.

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
maturin develop --release --config 'patch.crates-io.tiders-rpc-client.path="../../tiders-rpc-client/rust"'
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

