# Adaptive Concurrency

The RPC client automatically adjusts its parallelism and request pacing based on provider responses, maximizing throughput without overwhelming the provider or hitting rate limits.

There are three independent adaptive concurrency controllers, one for each type of RPC call pattern. Each controller's value determines how many parallel tasks run concurrently for that pipeline.

| Controller | Used by | Initial | Min | Max |
|---|---|---|---|---|
| Block | Block pipeline (`eth_getBlockByNumber` batches) | 10 | 2 | 200 |
| Log | Log pipeline (`eth_getLogs` batches) | 10 | 2 | 200 |
| Single-block | Traces (`trace_block`, `debug_traceBlockByNumber`) and tx receipts (`eth_getBlockReceipts`) | 100 | 10 | 2000 |

The single-block controller is shared between traces and transaction receipts requests. It starts more aggressively because per-block calls are smaller and faster than batch calls.

## How It Works

All controllers use the same adaptive algorithm, implemented lock-free with atomics.

### Scaling Up

On each successful RPC call:

1. Backoff delay is reduced by 25%
2. A consecutive success counter increments
3. After reaching the scale-up threshold, concurrency increases:
   - Block and log controllers: **+20%** after **10** consecutive successes
   - Single-block controller: **+33%** after **50** consecutive successes

The single-block controller requires more consecutive successes before scaling up because it runs many more concurrent calls.

### Scaling Down on Rate Limits

When a rate-limit error is detected (HTTP 429 or provider rate-limit message):

1. Consecutive success counter resets to 0
2. Backoff delay doubles (starting from 500 ms, capped at 30 s)
3. Concurrency is halved (down to the minimum)

### Scaling Down on General Errors

When a non-rate-limit error occurs:

1. Consecutive success counter resets to 0
2. Concurrency is reduced by 10% (gentler than rate limits)

## Chunk Size Adaptation

The block and log controllers also adapt the **chunk size** — the number of blocks per RPC call.

| Controller | Default chunk size |
|---|---|
| Block | 200 blocks |
| Log | 1000 blocks |
| Single-block | 200 blocks (batch grouping only, each block is a separate call) |

The initial chunk size can be set by the `batch_size` configuration option.

### Block Range Fallback

When a provider rejects a request because the block range is too large, the log controller tries to parse the error to extract a suggested range. It understands error formats from many providers:

- **Alchemy** — `"this block range should work: [0x..., 0x...]"`
- **Infura / Thirdweb / zkSync / Tenderly** — `"try with this block range [0x..., 0x...]"`
- **Ankr** — `"block range is too wide"`
- **QuickNode / 1RPC / zkEVM / Blast / BlockPI** — `"limited to a 10,000"`
- **Base** — `"block range too large"`

When no provider hint is available, the pipeline falls through a tiered fallback: 5000 → 500 → 75 → 50 → 45 → 40 → 35 → 30 → 25 → 20 → 15 → 10 → 5 → 1 blocks.

The block controller uses a simpler strategy: on block-range errors it halves the range.

### Chunk Size Recovery

After chunk size has been reduced due to errors, the block and log controllers periodically attempt to reset it to the original value. On each successful call, there is a **10% probability** of resetting the chunk size back to the configured (or default) value. This allows the system to recover from temporary provider issues without permanently degrading throughput.

## Backoff

Each controller maintains a backoff delay that is applied before every RPC call:

- Starts at **0 ms** (no delay)
- On rate limit: doubles, starting from **500 ms**, capped at **30 s**
- On success: reduced by **25%** per call
- Backoff applies to all concurrent calls sharing the same controller
