Introducing Tiders: An Open-Source Framework for Pipelines
Yule Andrade | 2025-05-05
Tiders is fully open-source. Dive into the code, browse the docs, or contribute in https://github.com/yulesa/tiders.

Blockchain data isn't what it used to be. As chains grow faster and user activity surges, the volume and complexity of data have exploded. Applications today demand real-time insights, richer context, and highly specialized access patterns. Yet traditional approaches to indexing—designed for simpler times—are struggling to keep up.

At the same time, we're seeing a new wave of data tooling emerge. Specialized libraries are stepping in to deliver solutions for common pitfalls in data indexing. Tiders is our take on this trend: a purpose-built multichain indexer designed from the ground up for performance, flexibility, and simple developer ergonomics. Whether you're building an analytics dashboard, a DeFi backend, or a real-time alerting system, Tiders helps you get the data you need—fast, reliably, and with context.

At its core, Tiders reflects a simple belief: permissionless access to data is as fundamental to blockchains as consensus itself. Regardless of design, every blockchain shares the same basic elements: blocks, transactions, logs, etc. These core data types are the building blocks of everything from analytics, to search, to application logic.

Tiders empowers teams to take control of their data pipelines—whether running their own infrastructure or contributing as data providers. Most importantly, Tiders is completely open-source, because we believe the best tools should be available to everyone. By making advanced indexing capabilities freely available, the result is a healthier, more competitive, and democratized ecosystem—where onchain data becomes a shared public good, not a walled garden.

Rethinking Raw Data Access
Traditionally, raw blockchain data has been accessed through the JSON-RPC interface. While this approach prioritizes decentralization—especially when running your own node—most users today rely on third-party RPC providers like Infura or QuickNode. This introduces an intermediary without solving the fundamental scaling challenges. In fact, at production scale, the standard EVM JSON-RPC API quickly becomes a bottleneck—slow, expensive, rate-limited, and ill-suited for modern data needs. Users end up with the worst of both worlds: centralized dependencies and underpowered tooling.

Many providers now offer proprietary APIs optimized for performance to work around these limitations. While faster, these solutions come with trade-offs: fragmented ecosystems, inconsistent schemas, and vendor lock-in. Each provider effectively maintains their own closed database with unique semantics—creating friction for developers and limiting interoperability.

Tiders takes a different approach. Rather than building yet another siloed API, Tiders defines a generalized, open-source query layer based on shared schemas and semantics. Providers can integrate directly with Tiders or use simple adapters to make them compatible with Tiders's interface. This architecture gives data consumers flexibility to choose between providers and chains, while also lowering the barrier to entry for new data providers to participate in the ecosystem.

The Tiders query format lets users interact with blockchain data as structured tables—such as blocks, logs, and transactions. Queries are expressive and efficient: rather than retrieving entire datasets, users can select specific fields and apply filters at the source (e.g. fetch only token transfers for a given wallet). This minimizes bandwidth usage, reduces processing time, and enables more scalable data pipelines.

query = ingest.Query(
    kind=ingest.QueryKind.EVM,
    params=ingest.evm.Query(
        from_block=from_block, # Required: Starting block number
        to_block=to_block, # Opt: Ending block number
        include_all_blocks=True, # Opt: Whether to include blocks with no matches in the tables request
        logs=[ingest.evm.LogRequest( # Opt: filters for logs where topic0 is the Transfer Event
                topic0=[  # ERC20 transfer event signature hash - Transfer(address,address,uint256)
                        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef" ]
        )],
        transactions=[ingest.evm.TransactionRequest()], # Opt: filters for tx (all tx with Transfer Event)
        fields=ingest.evm.Fields(
            log=ingest.evm.LogFields( # Required: Logs fields to include.
                transaction_hash=True, log_index=True, address=True
            ),
            transaction=ingest.evm.TransactionFields( # Required: tx fields to include.
                hash=True,
                from_=True,
                to=True,
                value=True,
                block_number=True,
                block_hash=True,
                transaction_index=True,
            ),
        ),
    ),
)
An example of Tiders's Python query

In-Pipeline Flexible Transformations
Once data is ingested, what you do with it is entirely up to you. Tiders is designed with flexibility at its core, supporting both ETL (Extract, Transform, Load) and ELT (Extract, Load, Transform) workflows depending on your preferences and infrastructure.

Tiders ships with a set of built-in transformation steps to make everyday tasks easier and faster. The user can select any of these operations, which are applied sequentially, during pipeline execution. Each transformation is optimized for performance using a Rust backend. The included transformations cover the most frequent needs of blockchain data processing:

Type casting
ABI or IDL-based decoding
Record validation
Encoding values (e.g. hex, base58)
Joining columns across tables
These built-in steps allow you to quickly normalize and enrich data without writing custom logic. But Tiders doesn't stop there.

Because Tiders pipelines run entirely in Python, you can plug in any processing engine or library you like—whether it's Pandas, Polars, DuckDB, DataFusion, or anything else in your toolchain. This makes Tiders ideal for teams that want a solid base layer with the freedom to extend, override, or enhance any part of the pipeline.

Need to apply a specialized transformation from your own library or use a domain-specific framework? No problem—Tiders lets you integrate those seamlessly into the pipeline.

Lastly, Tiders also supports fetching data from external providers or from your databases directly into the pipeline execution. This enables rich data enrichment, composing modular pipelines, and fine-grained control over execution cadence.

With Tiders, you get the whole flexibility of Python, and the freedom to shape your data pipelines exactly the way you need—no compromises, just flow.

return cc.Pipeline(
    provider=provider,
    query=query,
    writer=writer,
    steps=[
        # Built-in: Decode Swap events
        cc.Step(
            kind=cc.StepKind.EVM_DECODE_EVENTS,
            config=cc.EvmDecodeEventsConfig(
                event_signature=dex.event_signature,
                output_table="decoded_logs",
                hstack=True,
            ),
        ),
        # Built-in: Join transaction data to logs
        cc.Step(
            kind=cc.StepKind.JOIN_EVM_TRANSACTION_DATA,
            config=cc.JoinEvmTransactionDataConfig(),
        ),
        # Built-in: Join block data to logs and transactions
        cc.Step(
            kind=cc.StepKind.JOIN_BLOCK_DATA,
            config=cc.JoinBlockDataConfig(),
        ),
        # Built-in: Hex encode binary fields
        cc.Step(
            kind=cc.StepKind.HEX_ENCODE,
            config=cc.HexEncodeConfig(),
        ),
        # Custom: Fetching data from external provider to enrich with token metadata
        cc.Step(
            kind=cc.StepKind.CUSTOM,
            config=cc.CustomStepConfig(
                runner=enrich_with_metadata, # Custom function with provider request
                context=writer.config.connection, # fuction params: db connection checks if data already exist
                ),
        ),
        # Custom: Apply DEX-specific logic using polars
        cc.Step(
            kind=cc.StepKind.CUSTOM,
            config=cc.CustomStepConfig(
                runner=apply_dex_specific_logic,  # Custom function with polars transformation
                context=dex, # Custom fuction params as object
            ),
        ),
    ],
)
An example of Tiders's transformation steps

Modular Indexing: Reusable Pipelines
In the blockchain world, protocols often fork from one another or reuse the same data structures. That means your indexing logic probably doesn't need to be written from scratch every time—and Tiders makes sure you don't have to.

Tiders pipelines are just regular Python objects, meaning you can build functions around them, reuse them across modules, or set input parameters to customize them as needed. This avoids code repetition, reduces maintenance overhead, and speeds up development—especially when working with familiar or protocol forks.

Whether you're feeling lazy or need a quick way to extract boilerplate logs or transactions, Tiders has you covered.

The library comes with a growing set of ready-to-use pipelines—called Datasets—that handle common blockchain data patterns out of the box. Just plug in a few inputs like smart contract addresses to generate full indexers with minimal setup. These prebuilt datasets are a great starting point and can be extended or composed with your own logic when needed.

provider = ingest.ProviderConfig(
    kind=ProviderKind.Hypersync,
    url="https://eth.hypersync.xyz",
)

writer = cc.Writer(
    kind=cc.WriterKind.DUCKDB,
    config=cc.DuckdbWriterConfig(
        connection=connection.cursor(),
    ),
)

event_full_signature = "PairCreated(address indexed token0, address indexed token1, address pair,uint256)"
address = ["0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f"]
topic0 = ["0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9"]

# Create the pipeline using the built-in make_log_pipeline function with the above params
pipeline = datasets.evm.make_log_pipeline(
    provider=provider,
    writer=writer,
    event_full_signature=event_full_signature,
    from_block=from_block,
    to_block=to_block,
    address=address,
    topic0=topic0,
)
An example of creating a pipeline from a built-in pipeline

Write It Anywhere: Database connections in Tiders
After transformations are complete, Tiders offers flexible options for writing output to a wide range of storage backends. Whether you're integrating into a production data warehouse, building an analytics layer, or simply persisting intermediate results, Tiders ensures seamless compatibility across systems.

Supported targets include ClickHouse, Apache Iceberg, Delta Lake, DuckDB, Arrow Datasets, and Parquet files—ensuring compatibility with both modern and traditional data architectures.

Tiders's modular architecture means it's easy to swap storage targets or write to multiple destinations. This makes it especially powerful for experimentation, production analytics, and reporting workflows.

Need to write to custom sinks like PostgreSQL, S3, or BigQuery? Tiders's plugin system allows you to define and register your own output connectors with minimal boilerplate.

Why Tiders Matters
Tiders is built for a new era of blockchain data—where speed, flexibility, and openness are no longer Opt. As data demands evolve, legacy indexing tools fall short. Tiders meets this moment with a developer-first platform that scales effortlessly, integrates cleanly, and stays out of your way.

From raw ingestion to complex transformation and final storage, Tiders gives you full control over how data flows—without locking you into rigid patterns or proprietary systems. Whether bootstrapping a quick prototype or operating a production-grade pipeline, Tiders adapts to your needs.

Open-source at its core, Tiders isn't just a tool—it's a foundation for a more modular, collaborative, and permissionless data future.