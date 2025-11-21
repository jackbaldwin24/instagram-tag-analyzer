from __future__ import annotations

import sys
from pathlib import Path
from typing import Union

SCRIPT_DIR = Path(__file__).resolve().parent
SRC_ROOT = SCRIPT_DIR / "src"

# Ensure local src/ is importable without installation
if SRC_ROOT.exists():
    sys.path.insert(0, str(SRC_ROOT))

from ig_comments import build_graph, compute_dj_stats, make_interactive_graph, parse_comments  # noqa: E402

DEFAULT_INPUT = SCRIPT_DIR / "comments.txt"
DEFAULT_OUTPUT = SCRIPT_DIR / "interactive_graph.html"


def generate_graph(input_path: Union[str, Path] = DEFAULT_INPUT, output_path: Union[str, Path] = DEFAULT_OUTPUT) -> None:
    """Generate the interactive graph HTML from an Instagram comments export."""
    input_path = Path(input_path)
    output_path = Path(output_path)

    text = input_path.read_text(encoding="utf-8")
    user_tag_map, _ = parse_comments(text)
    dj_mentions, dj_unique_taggers = compute_dj_stats(user_tag_map)

    graph = build_graph(user_tag_map)
    make_interactive_graph(graph, user_tag_map, dj_mentions, dj_unique_taggers, output_path)


if __name__ == "__main__":
    generate_graph()
