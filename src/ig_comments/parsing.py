from __future__ import annotations

import re
from typing import Dict, List, Set, Tuple


def parse_comments(text: str) -> Tuple[Dict[str, List[str]], Set[str]]:
    """
    Parse instagram comments and extract:
    - user_tag_map: { commenter -> [list of tagged usernames in order, duplicates kept] }
    - all_djs: set of all unique usernames ever tagged

    Expected raw format per comment block:
        username's profile picture
        username
        <time like 2d/5h/43m/etc>
        <comment text containing @tags>
    """
    user_tag_map: Dict[str, List[str]] = {}
    all_djs: Set[str] = set()

    blockz = re.split(r"\n(?=[A-Za-z0-9_.]+'s profile picture)", text)

    for block in blockz:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue

        m = re.match(r"([A-Za-z0-9_\.]+)'s profile picture", lines[0])
        if not m:
            continue
        commenter = m.group(1)

        body = " ".join(lines[1:])
        tags = re.findall(r"@([A-Za-z0-9_.]+)", body)

        if tags:
            user_tag_map.setdefault(commenter, [])
            for t in tags:
                user_tag_map[commenter].append(t)
                all_djs.add(t)

    return user_tag_map, all_djs
