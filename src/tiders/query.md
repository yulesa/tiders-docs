# Query

The query defines what blockchain data to fetch: the block range, which tables to include, what filters to apply, and which fields to select.
Queries are specific to a blockchain type (Kind), and can be either:

- EVM (for Ethereum and compatible chains) or
- SVM (for Solana).

Each query consists of a request to select subsets of tables/data (block, logs, instructions) and field selectors to specify what columns should be included in the response for each table.

## Structure

```python
from tiders_core.ingest import Query, QueryKind
```

A query has:
- **`kind`** — `QueryKind.EVM` or `QueryKind.SVM`
- **`params`** — chain-specific query parameters

---

## EVM Queries

**Python**

```python
from tiders_core.ingest import evm

query = Query(
    kind=QueryKind.EVM,
    params=evm.Query(
        from_block=18_000_000,          # required
        to_block=18_001_000,            # optional — defaults to chain head
        include_all_blocks=False,       # optional — include blocks with no matching data
        logs=[evm.LogRequest(...)],     # optional — log filters
        transactions=[evm.TransactionRequest(...)],  # optional — transaction filters
        traces=[evm.TraceRequest(...)], # optional — trace filters
        fields=evm.Fields(...),         # field selection
    ),
)
```

**yaml**

```yaml
query:
  kind: evm
  from_block: 18000000
  to_block: 18001000          # optional — defaults to chain head
  include_all_blocks: false   # optional — default: false
  logs: [...]
  transactions: [...]
  traces: [...]
  fields: {...}
```
---

### EVM Table filters

The `logs`, `transactions`and `traces` params enable fine-grained row filtering through `[table]Request` objects. Each request individually filters for a subset of rows in the tables. You can combine multiple requests to build complex queries tailored to your needs. Except for blocks, table selection is made through explicit inclusion in a dedicated request or an `include_[table]` parameter.

#### Log Requests

Filter event logs by contract address and/or topic. All filter fields are combined with OR logic within a field and AND logic across fields.

**Python**

```python
evm.LogRequest(
    address=["0xabc..."],       # optional — list of log emitter addresses
    topic0=["0xabc..."],        # optional — list of keccak256 hash or event signature
    topic1=["0xabc..."],        # optional — list of first indexed parameter
    topic2=["0xabc..."],        # optional — list of second indexed parameter
    topic3=["0xabc..."],        # optional — list of third indexed parameter
    include_transactions=False,           # optional — include parent transaction
    include_transaction_logs=False,       # optional — include all logs from matching txs
    include_transaction_traces=False,     # optional — include traces from matching txs
    include_blocks=True,                  # optional — include block data
)
```

**yaml**

```yaml
query:
  kind: evm
  logs:
    - address: "0xdabc..."                           # optional
      topic0: "Transfer(address,address,uint256)"    # optional — signature or 0x hex hash
      topic1: "0xabc..."                             # optional
      topic2: "0xabc..."                             # optional
      topic3: "0xabc..."                             # optional
      include_transactions: false                    # optional, default: false
      include_transaction_logs: false                # optional, default: false
      include_transaction_traces: false              # optional, default: false
      include_blocks: true                           # optional, default: false
```

---

#### Transaction Requests

Filter transactions by sender, recipient, function selector, or other fields. Filtering transaction data at the source in a request is not supported by standart ETH JSON-RPC calls of RPC providers.

All filter fields are combined with OR logic within a field and AND logic across fields.

**Python**

```python
evm.TransactionRequest(
    from_=["0xabc..."],                   # optional — list of sender addresses
    to=["0xabc..."],                      # optional — list of recipient addresses
    sighash=["0xa9059cbb"],               # optional — list of 4-byte function selectors (hex)
    status=[1],                           # optional — list of status, 1=success, 0=failure
    type_=[2],                            # optional — list of type, 0=legacy, 1=access list, 2=EIP-1559
    contract_deployment_address=["0x..."],# optional — list of deployed contract addresses
    hash=["0xabc..."],                    # optional — list of specific transaction hashes
    include_logs=False,                   # optional — include emitted logs
    include_traces=False,                 # optional — include execution traces
    include_blocks=False,                 # optional — include block data
)
```

**yaml**

```yaml
query:
  kind: evm
  transactions:
    - from: ["0xabc..."]                        # optional
      to: ["0xabc..."]                          # optional
      sighash: ["0xa9059cbb"]                   # optional
      status: [1]                               # optional
      type: [2]                                 # optional
      contract_deployment_address: ["0x..."]    # optional
      hash: ["0xabc..."]                        # optional
      include_logs: false                       # optional, default: false
      include_traces: false                     # optional, default: false
      include_blocks: false                     # optional, default: false
```

---

#### Trace Requests

Filter execution traces (internal transactions). Filtering trace data at the source in a request is not supported by standart ETH JSON-RPC calls of RPC providers.

All filter fields are combined with OR logic within a field and AND logic across fields.

**Python**

```python
evm.TraceRequest(
    from_=["0xabc..."],                   # optional — list of caller addresses
    to=["0xabc..."],                      # optional — list of callee addresses
    address=["0xabc..."],                 # optional — list of ontract addresses in the trace
    call_type=["call"],                   # optional — list of call types, "call", "delegatecall", "staticcall"
    reward_type=["block"],                # optional — list of reward_type, "block", "uncle"
    type_=["call"],                       # optional — list of trace type, "call", "create", "suicide"
    sighash=["0xa9059cbb"],               # optional — list of 4-byte function selectors
    author=["0xabc..."],                  # optional — list of block reward author addresses
    include_transactions=False,           # optional — include parent transaction
    include_transaction_logs=False,       # optional — include logs from matching txs
    include_transaction_traces=False,     # optional — include all traces from matching txs
    include_blocks=False,                 # optional — include block data
)
```

**yaml**

```yaml
query:
  kind: evm
  traces:
    - from: ["0xabc..."]                        # optional
      to: ["0xabc..."]                          # optional
      address: ["0xabc..."]                     # optional
      call_type: ["call"]                       # optional — call, delegatecall, staticcall
      reward_type: ["block"]                    # optional — block, uncle
      type: ["call"]                            # optional — call, create, suicide
      sighash: ["0xa9059cbb"]                   # optional
      author: ["0xabc..."]                      # optional
      include_transactions: false               # optional, default: false
      include_transaction_logs: false           # optional, default: false
      include_transaction_traces: false         # optional, default: false
      include_blocks: false                     # optional, default: false
```

---

### EVM Field Selection

Select only the columns you need. All fields default to `false`.

**Python**

```python
evm.Fields(
    block=evm.BlockFields(number=True, timestamp=True, hash=True),
    transaction=evm.TransactionFields(hash=True, from_=True, to=True, value=True),
    log=evm.LogFields(block_number=True, address=True, topic0=True, data=True),
    trace=evm.TraceFields(from_=True, to=True, value=True, call_type=True),
)
```

**yaml**

```yaml
query:
  kind: evm
  fields:
    block: [number, timestamp, hash]
    transaction: [hash, from, to, value]
    log: [block_number, address, topic0, data]
    trace: [from, to, value, call_type]
```

**Available Block Fields**

`number`, `hash`, `parent_hash`, `nonce`, `sha3_uncles`, `logs_bloom`, `transactions_root`, `state_root`, `receipts_root`, `miner`, `difficulty`, `total_difficulty`, `extra_data`, `size`, `gas_limit`, `gas_used`, `timestamp`, `uncles`, `base_fee_per_gas`, `blob_gas_used`, `excess_blob_gas`, `parent_beacon_block_root`, `withdrawals_root`, `withdrawals`, `l1_block_number`, `send_count`, `send_root`, `mix_hash`

**Available Transaction Fields**

`block_hash`, `block_number`, `from`, `gas`, `gas_price`, `hash`, `input`, `nonce`, `to`, `transaction_index`, `value`, `v`, `r`, `s`, `max_priority_fee_per_gas`, `max_fee_per_gas`, `chain_id`, `cumulative_gas_used`, `effective_gas_price`, `gas_used`, `contract_address`, `logs_bloom`, `type`, `root`, `status`, `sighash`, `y_parity`, `access_list`, `l1_fee`, `l1_gas_price`, `l1_fee_scalar`, `gas_used_for_l1`, `max_fee_per_blob_gas`, `blob_versioned_hashes`, `deposit_nonce`, `blob_gas_price`, `deposit_receipt_version`, `blob_gas_used`, `l1_base_fee_scalar`, `l1_blob_base_fee`, `l1_blob_base_fee_scalar`, `l1_block_number`, `mint`, `source_hash`

**Available Log Fields**

`removed`, `log_index`, `transaction_index`, `transaction_hash`, `block_hash`, `block_number`, `address`, `data`, `topic0`, `topic1`, `topic2`, `topic3`

**Available Trace Fields**

`from`, `to`, `call_type`, `gas`, `input`, `init`, `value`, `author`, `reward_type`, `block_hash`, `block_number`, `address`, `code`, `gas_used`, `output`, `subtraces`, `trace_address`, `transaction_hash`, `transaction_position`, `type`, `error`, `sighash`, `action_address`, `balance`, `refund_address`

---

## SVM Queries

**Python**

```python
from tiders_core.ingest import svm

query = Query(
    kind=QueryKind.SVM,
    params=svm.Query(
        from_block=330_000_000,
        to_block=330_001_000,               # optional — defaults to chain head
        include_all_blocks=False,           # optional — include blocks with no matching data
        instructions=[svm.InstructionRequest(...)],     # optional
        transactions=[svm.TransactionRequest(...)],     # optional
        logs=[svm.LogRequest(...)],                     # optional
        balances=[svm.BalanceRequest(...)],             # optional
        token_balances=[svm.TokenBalanceRequest(...)],  # optional
        rewards=[svm.RewardRequest(...)],               # optional
        fields=svm.Fields(...),
    ),
)
```

**yaml**

```yaml
query:
  kind: svm
  from_block: 330000000
  to_block: 330001000          # optional — defaults to chain head
  include_all_blocks: false    # optional — default: false
  instructions: [...]
  transactions: [...]
  logs: [...]
  balances: [...]
  token_balances: [...]
  rewards: [...]
  fields: {...}
```

---

### SVM Table filters

The `instructions`, `transactions`, `logs`, `balances` , `token_balances`, `rewards` and `fields` params enable fine-grained row filtering through `[table]Request` objects. Each request individually filters for a subset of rows in the tables. You can combine multiple requests to build complex queries tailored to your needs. Except for blocks, table selection is made through explicit inclusion in a dedicated request or an `include_[table]` parameter.

#### Instruction Requests

Filter Solana instructions by program, discriminator, or account. Discriminator and account filters (`d1`–`d8`, `a0`–`a9`) use OR logic within a field and AND logic across fields.

**Python**

```python
svm.InstructionRequest(
    program_id=["JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"],  # optional — list of program ids, base58
    discriminator=["0xe445a52e51cb9a1d40c6cde8260871e2"],           # optional — list of discriminators, bytes or hex
    d1=["0xe4"],          # optional — list of 1-byte data prefix filter
    d2=["0xe445"],        # optional — list of 2-byte data prefix filter
    d4=["0xe445a52e"],    # optional — list of 4-byte data prefix filter
    d8=["0xe445a52e51cb9a1d"],  # optional — list of 8-byte data prefix filter
    a0=["0xabc..."],      # optional — list of account at index 0 (base58)
    a1=["0xabc..."],      # optional — list of account at index 1
    # a2–a9 follow the same pattern
    is_committed=False,                         # optional — only committed instructions
    include_transactions=True,                  # optional — include parent transaction
    include_transaction_token_balances=False,    # optional — include token balance changes
    include_logs=False,                         # optional — include program logs
    include_inner_instructions=False,           # optional — include inner (CPI) instructions
    include_blocks=True,                        # optional — default: true
)
```

**yaml**

```yaml
query:
  kind: svm
  instructions:
    - program_id: ["JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"]   # optional
      discriminator: ["0xe445a52e51cb9a1d40c6cde8260871e2"]            # optional
      d1: ["0xe4"]         # optional
      d2: ["0xe445"]       # optional
      d4: ["0xe445a52e"]   # optional
      d8: ["0xe445a52e51cb9a1d"]   # optional
      a0: ["TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"]   # optional
      is_committed: false                        # optional, default: false
      include_transactions: true                 # optional, default: false
      include_transaction_token_balances: false  # optional, default: false
      include_logs: false                        # optional, default: false
      include_inner_instructions: false          # optional, default: false
      include_blocks: true                       # optional, default: true
```

---

#### Transaction Requests (SVM)

Filter Solana transactions by fee payer.

**Python**

```python
svm.TransactionRequest(
    fee_payer=["0xabc..."],       # optional — list of fee payer public keys (base58)
    include_instructions=False,   # optional — include all instructions
    include_logs=False,           # optional — include program logs
    include_blocks=False,         # optional — include block data
)
```

**yaml**

```yaml
query:
  kind: svm
  transactions:
    - fee_payer: ["0xabc..."]       # optional
      include_instructions: false   # optional, default: false
      include_logs: false           # optional, default: false
      include_blocks: false         # optional, default: false
```

---

#### Log Requests (SVM)

Filter Solana program log messages by program ID and/or log kind.

**Python**

```python
svm.LogRequest(
    program_id=["JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"],  # optional — list of program ids
    kind=[svm.LogKind.LOG],       # optional — list of kinds, log, data, other
    include_transactions=False,   # optional — include parent transaction
    include_instructions=False,   # optional — include the emitting instruction
    include_blocks=False,         # optional — include block data
)
```

**yaml**

```yaml
query:
  kind: svm
  logs:
    - program_id: ["JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"]   # optional
      kind: [log]                    # optional — log, data, other
      include_transactions: false    # optional, default: false
      include_instructions: false    # optional, default: false
      include_blocks: false          # optional, default: false
```

---

#### Balance Requests

Filter native SOL balance changes by account.

**Python**

```python
svm.BalanceRequest(
    account=["0xabc..."],                     # optional — list of account public keys (base58)
    include_transactions=False,               # optional — include parent transaction
    include_transaction_instructions=False,   # optional — include transaction instructions
    include_blocks=False,                     # optional — include block data
)
```

**yaml**

```yaml
query:
  kind: svm
  balances:
    - account: ["0xabc..."]                       # optional — list of accounts
      include_transactions: false                 # optional, default: false
      include_transaction_instructions: false     # optional, default: false
      include_blocks: false                       # optional, default: false
```

---

#### Token Balance Requests

Filter SPL token balance changes. Pre/post filters match the state before and after the transaction.

**Python**

```python
svm.TokenBalanceRequest(
    account=["0xabc..."],               # optional — list of token account public keys (base58)
    pre_program_id=["TokenkegQ..."],    # optional — list of token program ID before tx
    post_program_id=["TokenkegQ..."],   # optional — list of token program ID after tx
    pre_mint=["0xabc..."],              # optional — list of token mint address before tx
    post_mint=["0xabc..."],             # optional — list of token mint address after tx
    pre_owner=["0xabc..."],             # optional — list of token account owner before tx
    post_owner=["0xabc..."],            # optional — list of token account owner after tx
    include_transactions=False,                 # optional — include parent transaction
    include_transaction_instructions=False,     # optional — include transaction instructions
    include_blocks=False,                       # optional — include block data
)
```

**yaml**

```yaml
query:
  kind: svm
  token_balances:
    - account: ["0xabc..."]                       # optional
      pre_mint: ["0xabc..."]                      # optional
      post_mint: ["0xabc..."]                     # optional
      pre_owner: ["0xabc..."]                     # optional
      post_owner: ["0xabc..."]                    # optional
      pre_program_id: ["TokenkegQ..."]            # optional
      post_program_id: ["TokenkegQ..."]           # optional
      include_transactions: false                 # optional, default: false
      include_transaction_instructions: false     # optional, default: false
      include_blocks: false                       # optional, default: false
```

---

#### Reward Requests

Filter Solana validator reward records by public key.

**Python**

```python
svm.RewardRequest(
    pubkey=["0xabc..."],   # optional — list of validator public keys (base58)
    include_blocks=False,  # optional — include block data
)
```

**yaml**

```yaml
query:
  kind: svm
  rewards:
    - pubkey: ["0xabc..."]   # optional
      include_blocks: false  # optional, default: false
```

---

### SVM Field Selection

Select only the columns you need. All fields default to `false`.

**Python**

```python
svm.Fields(
    instruction=svm.InstructionFields(block_slot=True, program_id=True, data=True),
    transaction=svm.TransactionFields(signature=True, fee=True),
    log=svm.LogFields(program_id=True, message=True),
    balance=svm.BalanceFields(account=True, pre=True, post=True),
    token_balance=svm.TokenBalanceFields(account=True, post_mint=True, post_amount=True),
    reward=svm.RewardFields(pubkey=True, lamports=True, reward_type=True),
    block=svm.BlockFields(slot=True, hash=True, timestamp=True),
)
```

**yaml**

```yaml
query:
  kind: svm
  fields:
    instruction: [block_slot, program_id, data]
    transaction: [signature, fee]
    log: [program_id, message]
    balance: [account, pre, post]
    token_balance: [account, post_mint, post_amount]
    reward: [pubkey, lamports, reward_type]
    block: [slot, hash, timestamp]
```

#### Available Instruction Fields

`block_slot`, `block_hash`, `transaction_index`, `instruction_address`, `program_id`, `a0`–`a9`, `rest_of_accounts`, `data`, `d1`, `d2`, `d4`, `d8`, `error`, `compute_units_consumed`, `is_committed`, `has_dropped_log_messages`

#### Available Transaction Fields (SVM)

`block_slot`, `block_hash`, `transaction_index`, `signature`, `version`, `account_keys`, `address_table_lookups`, `num_readonly_signed_accounts`, `num_readonly_unsigned_accounts`, `num_required_signatures`, `recent_blockhash`, `signatures`, `err`, `fee`, `compute_units_consumed`, `loaded_readonly_addresses`, `loaded_writable_addresses`, `fee_payer`, `has_dropped_log_messages`

#### Available Log Fields (SVM)

`block_slot`, `block_hash`, `transaction_index`, `log_index`, `instruction_address`, `program_id`, `kind`, `message`

#### Available Balance Fields

`block_slot`, `block_hash`, `transaction_index`, `account`, `pre`, `post`

#### Available Token Balance Fields

`block_slot`, `block_hash`, `transaction_index`, `account`, `pre_mint`, `post_mint`, `pre_decimals`, `post_decimals`, `pre_program_id`, `post_program_id`, `pre_owner`, `post_owner`, `pre_amount`, `post_amount`

#### Available Reward Fields

`block_slot`, `block_hash`, `pubkey`, `lamports`, `post_balance`, `reward_type`, `commission`

#### Available Block Fields (SVM)

`slot`, `hash`, `parent_slot`, `parent_hash`, `height`, `timestamp`
