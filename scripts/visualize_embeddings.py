"""Plot existing TradeTutor embeddings without changing the application database."""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
# Match app/rag/retriever.py; do not import it (it loads an embedding model).
DATABASE = ROOT / "data/chroma_db"
COLLECTION = "tradetutor_knowledge"
OUTPUT = ROOT / "outputs/embeddings/tradetutor_embeddings_pca.png"
QUERIES = [
    "How does a stop-loss protect a trader?",
    "How do I calculate my position size?",
    "Which stock should I buy today?",
    "How does risk management protect my trading capital?",
    "How do I calculate the risk/reward ratio for a trade?",
]


def application_guardrail():
    """Load the actual threshold and predicate without running application startup."""
    tree = ast.parse((ROOT / "app/rag/llm_client.py").read_text())
    nodes = [node for node in tree.body if
             (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "DISTANCE_THRESHOLD" for t in node.targets))
             or (isinstance(node, ast.FunctionDef) and node.name == "is_context_relevant")]
    namespace = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "application_guardrail", "exec"), namespace)
    return namespace["DISTANCE_THRESHOLD"], namespace["is_context_relevant"]


def encode_queries():
    from huggingface_hub import snapshot_download
    from sentence_transformers import SentenceTransformer

    # Same model and default encode preprocessing as app/rag/retriever.py.
    cached_model = snapshot_download("sentence-transformers/all-MiniLM-L6-v2", local_files_only=True)
    model = SentenceTransformer(cached_model, local_files_only=True)
    return model.encode(QUERIES)


def read_collection(database: Path = DATABASE, name: str = COLLECTION, query_embeddings=None) -> dict:
    """Read stored vectors via an isolated snapshot; never open the original in Chroma."""
    if not (database / "chroma.sqlite3").is_file():
        raise ValueError(f"Existing ChromaDB database not found: {database}")

    import chromadb
    from chromadb.config import Settings
    from chromadb.errors import NotFoundError

    with tempfile.TemporaryDirectory(prefix="tradetutor-pca-") as temporary:
        snapshot = Path(temporary) / "chroma_db"
        shutil.copytree(database, snapshot)
        # Include SQLite's committed WAL data using a read-only source connection.
        with sqlite3.connect((database / "chroma.sqlite3").as_uri() + "?mode=ro", uri=True) as source:
            with sqlite3.connect(snapshot / "chroma.sqlite3") as destination:
                source.backup(destination)
        client = chromadb.PersistentClient(
            path=str(snapshot), settings=Settings(anonymized_telemetry=False)
        )
        try:
            collection = client.get_collection(name=name, embedding_function=None)
        except NotFoundError as exc:
            raise ValueError(f"Collection {name!r} not found in {database}") from exc
        result = collection.get(include=["embeddings", "metadatas"])
        if query_embeddings is not None:
            if not result["ids"]:
                raise ValueError("The existing collection is empty.")
            result["retrieval"] = collection.query(
                query_embeddings=query_embeddings.tolist(),
                n_results=min(3, len(result["ids"])),
                include=["metadatas", "distances"],
            )
        return {**result, "collection_metadata": collection.metadata}


def chunk_key(chunk_id: str) -> tuple:
    match = re.fullmatch(r"chunk_(\d+)", chunk_id)
    return (0, int(match[1])) if match else (1, chunk_id)


def project_embeddings(result: dict, *, return_pca: bool = False):
    """Validate stored vectors and compute a deterministic, unscaled PCA projection."""
    import numpy as np
    from sklearn.decomposition import PCA

    ids = result["ids"]
    if not ids:
        raise ValueError("The existing collection is empty.")
    vectors = np.asarray(result["embeddings"], dtype=float)
    if vectors.ndim != 2 or min(vectors.shape) < 2:
        raise ValueError("2D PCA requires at least two stored embeddings with two dimensions each.")
    if len(ids) != len(vectors) or not np.isfinite(vectors).all():
        raise ValueError("Stored embeddings are incomplete or contain non-finite values.")
    if not np.any(np.ptp(vectors, axis=0)):
        raise ValueError("Stored embeddings have no variance; PCA cannot describe their relationships.")
    order = sorted(range(len(ids)), key=lambda index: chunk_key(ids[index]))
    metadata = result.get("metadatas") or [None] * len(ids)
    rows = [(ids[index], metadata[index] or {}) for index in order]
    pca = PCA(n_components=2, svd_solver="full")
    points = pca.fit_transform(vectors[order])
    projected = (rows, points, pca.explained_variance_ratio_ * 100)
    return (*projected, pca) if return_pca else projected


def source_group(metadata: dict) -> str:
    return str(metadata.get("source") or metadata.get("topic") or metadata.get("lesson") or "Unknown source")


def save_plot(rows: list, points, variance, output: Path, query_points=None, reports=None) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    groups = sorted({source_group(metadata) for _, metadata in rows})
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 11}):
        fig, ax = plt.subplots(figsize=(14, 9), layout="constrained")
        fig.set_facecolor("#FAFBFC")
        ax.set_facecolor("#FAFBFC")
        palette = plt.get_cmap("tab20", max(len(groups), 1))
        source_colors = {
            "risk_reward_lesson.md": "#399F99",
            "knowledge_stop_loss.md": "#9581C6",
            "knowledge_win_rate.md": "#D69576",
        }
        # Local visual halos, not density estimates or similarity boundaries.
        # Taking the maximum avoids building a broad cloud between distant chunks.
        span = np.maximum(np.ptp(points, axis=0), 0.1)
        softness = span * 0.055
        lower = points.min(axis=0) - softness * 2.5
        upper = points.max(axis=0) + softness * 2.5
        grid_x, grid_y = np.meshgrid(
            np.linspace(lower[0], upper[0], 360),
            np.linspace(lower[1], upper[1], 300),
        )
        for index, group in enumerate(groups):
            selected = [i for i, (_, metadata) in enumerate(rows) if source_group(metadata) == group]
            color = source_colors.get(group, palette(index))
            halo = np.zeros_like(grid_x)
            for x, y in points[selected]:
                local = np.exp(-0.5 * (((grid_x - x) / softness[0]) ** 2
                                       + ((grid_y - y) / softness[1]) ** 2))
                halo = np.maximum(halo, local)
            rgba = matplotlib.colors.to_rgba(color)
            ax.contourf(grid_x, grid_y, halo, levels=[0.08, 0.22, 0.45, 0.72, 1.01],
                        colors=[(*rgba[:3], alpha) for alpha in (0.045, 0.075, 0.11, 0.15)],
                        antialiased=True, zorder=0)
            ax.scatter(points[selected, 0], points[selected, 1], s=95,
                       color=color, edgecolors="white", linewidths=1, label=group, zorder=3)
        for number, (x, y) in enumerate(points, start=1):
            ax.annotate(str(number), (x, y), xytext=(6, 7 if number % 2 else -15), textcoords="offset points",
                        fontsize=9, fontweight="bold", color="#173F42")
        ax.set_title(
            f"TradeTutor AI · Knowledge embedding space\n"
            f"{len(rows)} stored chunks | PCA projection | PC1 + PC2 explain {sum(variance):.1f}% of variance",
            loc="left", fontsize=17, fontweight="bold", pad=20,
        )
        ax.set_xlabel(f"Principal component 1 ({variance[0]:.1f}% variance)")
        ax.set_ylabel(f"Principal component 2 ({variance[1]:.1f}% variance)")
        ax.grid(alpha=0.18)
        ax.set_axisbelow(True)
        ax.margins(0.15)
        ax.spines[["top", "right"]].set_visible(False)
        source_legend = ax.legend(title="Source document / topic", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
        if query_points is not None:
            import textwrap

            ax.add_artist(source_legend)
            handles = []
            for index, ((x, y), report) in enumerate(zip(query_points, reports), start=1):
                color = "#138568" if report["accepted"] else "#C73E46"
                label = f"Q{index}: {report['query']}\n{report['status']} · d={report['distance']:.4f}"
                label = "\n".join(textwrap.fill(line, width=39) for line in label.splitlines())
                handles.append(ax.scatter(x, y, marker="*", s=310, color=color,
                                          edgecolors="#173F42", linewidths=1, zorder=5, label=label))
                ax.annotate(f"Q{index}", (x, y), xytext=(-10, -23), textcoords="offset points",
                            fontsize=11, fontweight="bold", color=color,
                            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 1})
            ax.legend(handles=handles, title="Queries · distance guardrail only", bbox_to_anchor=(1.02, 0.71),
                      loc="upper left", frameon=False, labelspacing=1.2, fontsize=9)
        fig.supxlabel(
            "Numbers identify chunks; projected distances are approximate.\n"
            "Colored clouds group sources visually; they are not similarity or retrieval-threshold boundaries.",
            fontsize=10,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            fig.savefig(output, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
        finally:
            plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT, help="Destination PNG path")
    parser.add_argument("--queries", action="store_true", help="Overlay representative queries and report actual retrieval distances")
    args = parser.parse_args()
    if not (DATABASE / "chroma.sqlite3").is_file():
        print(f"Error: Existing ChromaDB database not found: {DATABASE}", file=sys.stderr)
        return 1
    missing = [package for module, package in
               [("numpy", "numpy"), ("matplotlib", "matplotlib"), ("sklearn", "scikit-learn")]
               if importlib.util.find_spec(module) is None]
    if missing:
        print("Missing dependencies. Install explicitly with:\nuv add --dev " + " ".join(missing), file=sys.stderr)
        return 1
    try:
        query_embeddings = encode_queries() if args.queries else None
        result = read_collection(query_embeddings=query_embeddings)
        rows, points, variance, pca = project_embeddings(result, return_pca=True)
        print(f"Database: {DATABASE}\nCollection: {COLLECTION}")
        print("Collection metadata:", json.dumps(result["collection_metadata"], ensure_ascii=False))
        print("\nChunk reference (point number | chunk ID | source | metadata):")
        for number, (chunk_id, metadata) in enumerate(rows, start=1):
            print(f"{number} | {chunk_id} | {source_group(metadata)} | {json.dumps(metadata, ensure_ascii=False, sort_keys=True)}")
        reports = None
        query_points = None
        if args.queries:
            threshold, is_context_relevant = application_guardrail()
            query_points = pca.transform(query_embeddings)
            reports = []
            retrieved = result["retrieval"]
            print(f"\nQuery retrieval (application rule: min(distances) < {threshold}):")
            for index, query in enumerate(QUERIES):
                distances = retrieved["distances"][index]
                nearest = min(range(len(distances)), key=distances.__getitem__)
                accepted = is_context_relevant(distances)
                report = {"query": query, "chunk_id": retrieved["ids"][index][nearest],
                          "source": source_group(retrieved["metadatas"][index][nearest] or {}),
                          "distance": distances[nearest], "accepted": accepted,
                          "status": "PASS" if accepted else "REJECT"}
                reports.append(report)
                print(f"Q{index + 1}: {json.dumps(report, ensure_ascii=False)}")
            print("PASS means distance relevance only; investment-advice restrictions still apply.")
        output = args.output
        if args.queries and output == OUTPUT:
            output = OUTPUT.with_name("tradetutor_embeddings_pca_queries.png")
        save_plot(rows, points, variance, output, query_points, reports)
        print(f"\nExplained variance: PC1 {variance[0]:.2f}%, PC2 {variance[1]:.2f}%, combined {sum(variance):.2f}%")
        print(f"Saved: {output.resolve()}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
