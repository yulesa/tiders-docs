# Architeture

This section walks you through how is tiders architecture.

## Dependency Graph

```
tiders-evm-schema        (no deps)
tiders-svm-schema         (no deps)
tiders-cast               (no deps)
tiders-query              (no deps)
tiders-evm-decode         (no deps)
tiders-svm-decode         (no deps)
    │
    ├──► tiders-rpc-client
    │        └── tiders-evm-schema
    │
    ├──► tiders-ingest
    │        ├── tiders-evm-schema
    │        ├── tiders-svm-schema
    │        ├── tiders-cast
    │        ├── tiders-query
    │        └── tiders-rpc-client
    │
    ├──► tiders-core
    │        ├── tiders-evm-schema
    │        ├── tiders-svm-schema
    │        ├── tiders-cast
    │        ├── tiders-query
    │        ├── tiders-evm-decode
    │        ├── tiders-svm-decode
    │        └── tiders-ingest
    │
    └──► tiders-core-python
             └── tiders-core (aliased as "baselib")
```