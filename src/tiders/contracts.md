# Contracts

Contracts is an optional module that makes it easier to get contract information, such as Events, Functions and their params.

When you define a contract, tiders parses the ABI JSON file and extracts all events and functions with their signatures, selectors, and topic hashes — so you don't have to compute or hard-code them yourself.

## Event/Functions Fields

Each event/function parsed from the ABI exposes:

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Event/Function name (e.g. `"Swap"`) |
| `name_snake_case` | `str` | Event/Function name in snake_case (e.g. `"matched_orders"`) |
| `signature` | `str` | Human-readable signature with types, names and indexed markers (events) (e.g. `"Swap(address indexed sender, address indexed recipient, int256 amount0)"`) |
| `selector_signature` | `str` | Canonical signature without names (e.g. `"Swap(address,address,int256)"`) |
| `topic0` | `str` | (Event only) Keccak-256 hash of the selector signature, as 0x-prefixed hex |
| `selector` | `str` | (Function-only) 4-byte function selector as 0x-prefixed hex |

---

## YAML Usage

In YAML configs, define contracts under the `contracts:` key. Tiders automatically parses the ABI and makes all values available via reference syntax.

```yaml
contracts:
  - name: MyToken
    address: "0xae78736Cd615f374D3085123A210448E74Fc6393"
    abi: ./MyToken.abi.json # abi path
    chain_id: ethereum      # numeric chain ID or a chain name in some chains (used to download the ABI in the CLI command `tiders abi`)
```

**Reference Syntax**

Once a contract is defined, tiders parse will automatically extract ABI information, so you can reference its address, events, and functions by name anywhere in `query:` or `steps:` sections:

| Reference | Resolves to |
|---|---|
| `MyToken.address` | The contract address string |
| `MyToken.Events.Transfer.name` | Event name |
| `MyToken.Events.Transfer.topic0` | Keccak-256 hash of the event signature |
| `MyToken.Events.Transfer.signature` | Full event signature string |
| `MyToken.Events.Transfer.name_snake_case` | Event name in snake_case |
| `MyToken.Events.Transfer.selector_signature` | Canonical event signature without names |
| `MyToken.Functions.transfer.selector` | 4-byte function selector |
| `MyToken.Functions.transfer.signature` | Full function signature string |
| `MyToken.Functions.transfer.name_snake_case` | Function name in snake_case |
| `MyToken.Functions.transfer.selector_signature` | Canonical function signature without names |

---

## Python Usage

Use `evm_abi_events` and `evm_abi_functions` from `tiders_core`. These functions take a JSON ABI string and return a `list[EvmAbiEvent]` / `list[EvmAbiFunction]` with the fields described above.

```python
from pathlib import Path
from tiders_core import evm_abi_events, evm_abi_functions

# Contract address
my_token_address = "0xae78736Cd615f374D3085123A210448E74Fc6393"
# Load ABI
abi_path = Path("./MyToken.abi.json")
abi_json = abi_path.read_text()

# Parse events — dict keyed by event name
events = {
    ev.name: {
        "topic0": ev.topic0,
        "signature": ev.signature,
        "name_snake_case": ev.name_snake_case,
        "selector_signature": ev.selector_signature,
    }
    for ev in evm_abi_events(abi_json)
}

# Parse functions — dict keyed by function name
functions = {
    fn.name: {
        "selector": fn.selector,
        "signature": fn.signature,
        "name_snake_case": fn.name_snake_case,
        "selector_signature": fn.selector_signature,
    }
    for fn in evm_abi_functions(abi_json)
}

```

You can then use the parsed values in your query and steps:

```python
query = Query(
    kind=QueryKind.EVM,
    params=evm.Query(
        from_block=18_000_000,
        logs=[
            evm.LogRequest(
                address=[my_token_address],
                topic0=[events["Transfer"]["topic0"]],
            ),
        ],
    ),
)

steps = [
    Step(
        kind=StepKind.EVM_DECODE_EVENTS,
        config=EvmDecodeEventsConfig(
            event_signature=events["Transfer"]["signature"],
        ),
    ),
]
```