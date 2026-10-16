# Visualizing stored knowledge embeddings

From the repository root, run:

```bash
uv run --no-sync scripts/visualize_embeddings.py
```

The script requires NumPy, Matplotlib, scikit-learn, and the application's
ChromaDB dependency. It reports missing plotting dependencies without installing
them. At implementation time, only Matplotlib was missing:

```bash
uv add --dev matplotlib
```

The default output is `outputs/embeddings/tradetutor_embeddings_pca.png`,
rendered at 300 DPI. Override it with `--output path/to/figure.png`.
Paths for the database and default output are resolved relative to the repository,
so the utility also works from another working directory.

The existing retriever and embedder configure `data/chroma_db` and collection
`tradetutor_knowledge`. Their modules load a SentenceTransformer model on import,
so this independent utility mirrors those two configuration values without
importing the RAG pipeline. Update the utility's constants if that configuration
changes. The default chunk-only mode loads no embedding model. Stored chunk
embeddings are never regenerated.

To prevent ChromaDB startup migrations or housekeeping from touching the source,
the script copies the existing persistent directory into temporary storage,
backs up SQLite through a read-only source connection, and calls `get_collection`
on the copy. It never calls `get_or_create_collection` or writes collection data.
Run while ingestion is idle so SQLite and vector index files reflect the same
state. The temporary snapshot requires space comparable to the database.

Each point is one stored chunk. Numbered annotations match the printed reference,
which lists the full chunk ID, source, and available metadata. IDs are ordered
numerically for `chunk_N` IDs. Colors identify `source` metadata, falling back to
`topic`, `lesson`, or `Unknown source`. Collection metadata is also printed.

Nearby points have similar coordinates along the two directions of greatest
variance in the stored vectors. PCA centers the actual vectors without scaling
or normalizing them. Axis labels show individual explained variance; the subtitle
shows their sum. This projection discards other dimensions, so points close in
2D may still be far apart in the original space. It does not reproduce retrieval
rankings or cosine similarities. The stored collection uses an L2 vector index.

Verification on the existing store found 18 vectors with 384 dimensions across
`risk_reward_lesson.md`, `knowledge_stop_loss.md`, and `knowledge_win_rate.md`.
Collection metadata was absent. PC1 explained 21.31% and PC2 16.46%, totaling
37.77%. Source database files had identical SHA-256 hashes before and after the
read. After Matplotlib was installed, the full command successfully generated
the 300 DPI PNG with all 18 numbered points and the three source groups.

Missing databases, missing collections, empty collections, insufficient vectors,
invalid values, and zero-variance embeddings produce an error and a nonzero exit
status. Importing the script does not connect to ChromaDB or require plotting
dependencies.

## Query overlay

```bash
uv run --no-sync scripts/visualize_embeddings.py --queries
```

This saves `outputs/embeddings/tradetutor_embeddings_pca_queries.png`, preserving
the original chunk-only PNG. `--output` also works with the overlay.
The five fixed queries are encoded using the locally cached
`sentence-transformers/all-MiniLM-L6-v2` model and default `encode()` preprocessing,
matching the application's retriever. No additional dependencies are required.
If that model is not cached, the script reports an error rather than substituting
another model or downloading one automatically.

PCA fits only the stored chunk vectors. The same fitted PCA transforms the query
vectors; chunk coordinates and source colors are unchanged. Stars labeled Q1–Q5
show queries, with green for PASS and red for REJECT. The legend includes the
question, status, and original ChromaDB distance.

The script queries the existing collection's temporary copy for the top three
chunks, as the application does, and prints the nearest chunk ID, actual source
metadata, and returned distance. It loads `DISTANCE_THRESHOLD` and
`is_context_relevant` from the AST of `app/rag/llm_client.py` to reuse the actual
rule without executing application imports or opening the original database.
The current rule is `min(distances) < 1.0`; equality is rejected.
No PCA distances determine acceptance. PASS indicates distance relevance only;
the application's separate investment-advice restrictions still apply.

Actual results from the existing collection:

| Query | Question | Nearest chunk | Source | ChromaDB distance | Result |
| --- | --- | --- | --- | --- | --- |
| Q1 | How does a stop-loss protect a trader? | chunk_10 | knowledge_stop_loss.md | 0.8112810254 | PASS |
| Q2 | How do I calculate my position size? | chunk_4 | risk_reward_lesson.md | 1.5293121338 | REJECT |
| Q3 | Which stock should I buy today? | chunk_11 | knowledge_stop_loss.md | 1.4035834074 | REJECT |
| Q4 | How does risk management protect my trading capital? | chunk_11 | knowledge_stop_loss.md | 1.0220534801 | REJECT |
| Q5 | How do I calculate the risk/reward ratio for a trade? | chunk_4 | risk_reward_lesson.md | 0.2372445762 | PASS |

Q4 illustrates that relevant-sounding wording can still fail this threshold.
Likewise, proximity on this plot cannot establish whether a query is supported.
The two retained components still explain 37.77% of chunk variance.
