# Pipelines

The RPC client organizes data fetching into three independent **pipelines**, each targeting a specific JSON-RPC method. When a query needs more than one pipeline, they are coordinated through a multi-pipeline stream.

## Historical and Live Phases

Each pipeline operates in two phases:

1. **Historical** — fetches all data from `from_block` to the chain head (or `to_block` if specified), using concurrent tasks for throughput
2. **Live** — after catching up, polls for new blocks at the interval set by `head_poll_interval_millis` and fetches data sequentially

If `stop_on_head` is set to `true`, the stream ends after the historical phase without entering live mode.

## Block Pipeline

Fetches blocks and transactions using `eth_getBlockByNumber`.

- Sends batch RPC calls for a range of block numbers
- Transactions are extracted from the block response — no separate RPC call is needed
- Concurrency is managed by the block [adaptive concurrency](./adaptive_concurrency.md) controller

`eth_getBlockByNumber` returns all transactions in a block with no server-side filtering. Setting filter fields (e.g. `from_`, `to`, `sighash`, `status`) on a `TransactionRequest` will produce an error. This functionality is only supported on other Tiders' clients (sqd, hypersync). Ingest all transactions and filter post-indexing in your Tiders (python) pipeline or database instead.

### Transaction Receipts

When the query requests transaction receipts fields (e.g. `status`, `gas_used`, `effective_gas_price`), the block pipeline automatically fetches transaction receipts via `eth_getBlockReceipts` and merges them into the transaction data. This runs as a sub-step inside the block pipeline, not as a separate pipeline.

Each block's receipts are fetched individually in parallel, bounded by the single-block [adaptive concurrency](./adaptive_concurrency.md) controller.

## Log Pipeline

Fetches event logs using `eth_getLogs`.

- Constructs filters from the query's log requests (addresses and topics)
- Concurrency is managed by the log [adaptive concurrency](./adaptive_concurrency.md) controller
- Automatically splits large address lists into groups of 1000 per request
- When a provider rejects a block range as too large, the pipeline automatically limits the block range and retries

Log filters (addresses and topics) cannot be combined with `include_*` flags on the same `LogRequest`. When `include_*` flags activate additional pipelines, those pipelines return unfiltered data for the full block range — combining that with filtered logs would produce an inconsistent response. To use cross-pipeline coordination, remove the log filters and filter post-indexing.

## Trace Pipeline

Fetches internal call traces using `trace_block` or `debug_traceBlockByNumber`.

- The trace method is auto-detected from the provider or can be overridden via `trace_method` in the configuration
- Each block is traced individually in parallel, bounded by the single-block [adaptive concurrency](./adaptive_concurrency.md) controller
- Each block is retried independently up to `max_num_retries` times

`trace_block` and `debug_traceBlockByNumber` return all traces in a block with no server-side filtering. Setting filter fields (e.g. `from_`, `to`, `call_type`, `sighash`) on a `TraceRequest` will produce an error. This functionality is only supported on other Tiders' clients (sqd, hypersync). Ingest all transactions and filter post-indexing in your Tiders (python) pipeline or database instead.

> **Note:** Tracing requires a provider that supports block-level trace methods.

## Multi-Pipeline Stream

When a query requires data from more than one pipeline, the client automatically switches to a **coordinated multi-pipeline stream** instead of running individual pipeline streams.

The coordinator:

1. Divides the block range into fixed-size batches (sized by `batch_size`). Unlike single-pipeline mode, the batch size does not adapt — it stays fixed throughout the run, so each response covers the same number of blocks.
2. Runs all needed pipelines for each batch over the **same block range**. Pipelines run sequentially within a batch to avoid interference between their [adaptive concurrency](./adaptive_concurrency.md) controllers. Concurrency parameters carry over from one batch to the next.
3. Merges the results into a single response containing blocks, transactions, logs, and traces for the entire batch.

This ensures that all data types in a response correspond to the same set of blocks.

### Pipeline Selection

Which pipelines run is determined by the query:

- **Block pipeline** runs if the query requests block or transaction fields, or uses `include_all_blocks`
- **Log pipeline** runs if the query has log requests or selects log fields
- **Trace pipeline** runs if the query has trace requests or selects trace fields

Cross-pipeline `include_*` flags (e.g. `include_transactions` on a log request) can also activate additional pipelines.

If a query selects fields from multiple pipelines (e.g. both log and block fields) without setting `include_*` flags on any request, the client will return an error. This prevents accidental multi-pipeline queries. Either use `include_*` flags to opt in to cross-pipeline coordination, or split into separate queries.

