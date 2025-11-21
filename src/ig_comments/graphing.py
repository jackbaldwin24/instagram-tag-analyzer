from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Set, Tuple

import networkx as nx


def build_graph(user_tag_map: Dict[str, List[str]]) -> nx.DiGraph:
    """Build a directed graph where commenters point to DJs they tag."""
    graph = nx.DiGraph()

    for commenter, tagged in user_tag_map.items():
        if commenter not in graph:
            graph.add_node(commenter, type="commenter")

        for dj in tagged:
            # If DJ node already exists AND was previously marked as commenter → upgrade to DJ
            if dj in graph:
                if graph.nodes[dj].get("type") == "commenter":
                    graph.nodes[dj]["type"] = "dj"
            else:
                graph.add_node(dj, type="dj")

            graph.add_edge(commenter, dj)

    return graph


def compute_dj_stats(user_tag_map: Dict[str, List[str]]) -> Tuple[Counter, Dict[str, Set[str]]]:
    """Compute per-DJ stats used for sizing and click/hover details."""
    dj_mentions = Counter()  # total raw tags (with duplicates)
    dj_unique_taggers: Dict[str, Set[str]] = defaultdict(set)  # dj -> set(commenters who tagged them)

    for commenter, tagged_list in user_tag_map.items():
        for dj in tagged_list:
            dj_mentions[dj] += 1
            dj_unique_taggers[dj].add(commenter)

    return dj_mentions, dj_unique_taggers
