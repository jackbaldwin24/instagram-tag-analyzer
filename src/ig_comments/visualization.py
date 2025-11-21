from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Set

from pyvis.network import Network  # pyright: ignore[reportMissingImports]


def _build_leaderboard_html(dj_mentions, dj_unique_taggers) -> str:
    top10_total = dj_mentions.most_common(10)
    top10_unique = sorted(
        dj_unique_taggers.items(),
        key=lambda kv: (len(kv[1]), dj_mentions.get(kv[0], 0)),
        reverse=True,
    )[:10]

    max_total_top = top10_total[0][1] if top10_total else 1
    max_unique_top = len(top10_unique[0][1]) if top10_unique else 1

    def bar_row(label: str, value: int, max_value: int, bar_color: str) -> str:
        pct = (value / max_value) * 100 if max_value else 0
        return (
            f"<div style='margin:6px 0;'>"
            f"  <div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:2px;'>"
            f"    <span>@{label}</span><span>{value}</span>"
            f"  </div>"
            f"  <div style='background:#eee; border-radius:6px; height:10px; overflow:hidden;'>"
            f"    <div style='width:{pct:.1f}%; height:10px; background:{bar_color};'></div>"
            f"  </div>"
            f"</div>"
        )

    total_bars_html = "".join(
        [bar_row(dj, count, max_total_top, "#ff6b6b") for dj, count in top10_total]
    ) or "<div style='font-size:13px;'>(none)</div>"

    unique_bars_html = "".join(
        [bar_row(dj, len(taggers), max_unique_top, "#76a9ff") for dj, taggers in top10_unique]
    ) or "<div style='font-size:13px;'>(none)</div>"

    return f"""
    <div id='leaderboardPanel' style='position:absolute; bottom:12px; left:12px; z-index:9999; padding:12px; background:rgba(255,255,255,0.98); border:1px solid #e5e5e7; border-radius:10px; font-family:Arial; width:560px; max-height:50vh; overflow:auto; box-shadow:0 4px 16px rgba(0,0,0,0.08);'>
        <div id='leaderboardHeader' style='font-weight:bold; cursor:pointer; display:flex; align-items:center; justify-content:space-between;'>
            <span>Leaderboards</span>
            <span id='leaderboardCaret' style='font-size:12px;'>▶</span>
        </div>
        <div id='leaderboardContent' style='display:none; margin-top:8px;'>
            <div style='display:flex; gap:12px; align-items:flex-start;'>
                <div style='flex:1; min-width:0;'>
                    <div style='font-weight:bold; font-size:14px; margin-bottom:4px;'>Top 10 — Total Tags</div>
                    {total_bars_html}
                </div>
                <div style='flex:1; min-width:0;'>
                    <div style='font-weight:bold; font-size:14px; margin-bottom:4px;'>Top 10 — Unique User Tags</div>
                    {unique_bars_html}
                </div>
            </div>
        </div>
    </div>
    """


def _add_nodes_and_edges(
    net: Network,
    graph,
    user_tag_map: Dict[str, List[str]],
    dj_mentions,
    dj_unique_taggers,
) -> None:
    max_mentions = max(dj_mentions.values()) if dj_mentions else 1

    for node, data in graph.nodes(data=True):
        ntype = data.get("type", "commenter")

        if ntype == "commenter":
            tagged = user_tag_map.get(node, [])
            hover_title = f"@{node}\nTags made: {len(tagged)}"

            unique_tagged = sorted(set(tagged))
            tagged_list_html = ", ".join([f"@{u}" for u in unique_tagged]) if unique_tagged else "(none)"

            panel_html = (
                f"<b>@{node}</b><br>"
                f"<b>Tags made:</b> {len(tagged)}<br>"
                f"<b>They tagged ({len(unique_tagged)}):</b> {tagged_list_html}"
            )
            net.add_node(
                node,
                label=node,
                color="#76a9ff",
                size=8,
                title=hover_title,
                panel=panel_html,
                font={
                    "size": 18,
                    "face": "Arial Black",
                    "color": "#0f172a",
                    "background": "rgba(255,255,255,0.92)",
                    "strokeWidth": 4,
                    "strokeColor": "#ffffff",
                },
            )
        else:
            mentions = dj_mentions.get(node, 0)
            unique_taggers = sorted(dj_unique_taggers.get(node, set()))

            taggers_list_csv = ", ".join([f"@{u}" for u in unique_taggers]) if unique_taggers else "(none)"

            unique_they_tagged = sorted(set(user_tag_map.get(node, [])))
            they_tagged_csv = ", ".join([f"@{u}" for u in unique_they_tagged]) if unique_they_tagged else "(none)"

            scaled = (mentions / max_mentions) if max_mentions else 0
            dj_size = 12 + scaled * 35

            hover_title = f"@{node}\nTotal tags: {mentions}\nUnique users: {len(unique_taggers)}"

            panel_html = (
                f"<b>@{node}</b><br>"
                f"<b>Total tags:</b> {mentions}<br>"
                f"<b>Unique users tagging:</b> {len(unique_taggers)}<br>"
                f"<b>Tagged by:</b> {taggers_list_csv}<br><br>"
                f"<b>They tagged:</b> {they_tagged_csv}"
            )
            net.add_node(
                node,
                label=node,
                color="#ff6b6b",
                size=dj_size,
                title=hover_title,
                panel=panel_html,
                font={
                    "size": 18,
                    "face": "Arial Black",
                    "color": "#0f172a",
                    "background": "rgba(255,255,255,0.92)",
                    "strokeWidth": 4,
                    "strokeColor": "#ffffff",
                },
            )

    for source, target in graph.edges():
        net.add_edge(source, target, color="#999999")


def _inject_custom_ui(output_html: Path, leaderboard_html: str) -> None:
    html = output_html.read_text(encoding="utf-8")

    injected = f"""
    <style>
        /* Clean page + remove weird borders/lines */
        html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; background: #f7f7f8; font-family: Arial, sans-serif; }}
        #mynetwork {{ width: 100% !important; height: 100% !important; border: none !important; outline: none !important; }}
        canvas {{ outline: none !important; }}

        /* Custom loading overlay */
        #graphLoader {{
            position: fixed;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle at 20% 20%, #ffffff 0%, #f0f2f5 45%, #e9ecf1 100%);
            z-index: 10000;
            transition: opacity 0.35s ease;
        }}
        #graphLoader.hidden {{
            opacity: 0;
            pointer-events: none;
        }}
        #graphLoader .loaderCard {{
            padding: 18px 20px;
            border-radius: 14px;
            background: #0f172a;
            color: #f8fafc;
            box-shadow: 0 20px 60px rgba(15, 23, 42, 0.28);
            min-width: 260px;
            display: flex;
            align-items: center;
            gap: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}
        #graphLoader .spinner {{
            width: 34px;
            height: 34px;
            border-radius: 50%;
            border: 3px solid rgba(255, 255, 255, 0.25);
            border-top-color: #60a5fa;
            animation: spin 0.8s linear infinite;
        }}
        #graphLoader .loadingText {{
            font-weight: 700;
            font-size: 16px;
            letter-spacing: 0.2px;
        }}
        #graphLoader .loadingHint {{
            font-size: 13px;
            opacity: 0.85;
            margin-top: 2px;
        }}
        @keyframes spin {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}

        /* Hide PyVis/vis.js loading bar (it can look glitchy/off-center) */
        #loadingBar, .vis-loading, .vis-progressbar {{ display: none !important; }}

        /* Search UI */
        #searchPanel {{
            position: absolute;
            top: 12px;
            left: 12px;
            z-index: 9999;
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 12px;
            background: rgba(255,255,255,0.98);
            border: 1px solid #e5e5e7;
            border-radius: 10px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            backdrop-filter: blur(4px);
        }}
        #searchNode {{
            padding: 8px 10px;
            width: 230px;
            font-size: 14px;
            border: 1px solid #d7d7db;
            border-radius: 8px;
            outline: none;
        }}
        #searchNode:focus {{ border-color: #999; box-shadow: 0 0 0 3px rgba(120,120,255,0.12); }}
        #searchBtn {{
            padding: 8px 12px;
            font-size: 14px;
            border: 1px solid #d7d7db;
            background: #111;
            color: #fff;
            border-radius: 8px;
            cursor: pointer;
        }}
        #searchBtn:hover {{ filter: brightness(1.06); }}

        /* Info panel */
        #infoPanel {{
            position: absolute;
            top: 12px;
            right: 12px;
            z-index: 9999;
            padding: 12px;
            background: rgba(255,255,255,0.98);
            border: 1px solid #e5e5e7;
            border-radius: 10px;
            font-family: Arial, sans-serif;
            width: 340px;
            max-height: 85vh;
            overflow: auto;
            display: none;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        }}

    </style>

    <div id='graphLoader'>
        <div class='loaderCard'>
            <div class='spinner'></div>
            <div>
                <div class='loadingText'>Loading graph…</div>
                <div class='loadingHint'>We are laying out nodes and edges.</div>
            </div>
        </div>
    </div>

    <div id='searchPanel'>
        <input id='searchNode' type='text' placeholder='Search username…' />
        <button id='searchBtn' onclick='highlightNode()'>Search</button>
    </div>

    {leaderboard_html}

    <div id='infoPanel'></div>

    <script>
    var highlightedId = null;
    var isFiltered = false;
    var loaderEl = document.getElementById('graphLoader');

    // Custom loader fades once vis.js finishes its first pass.
    function hideLoader() {{
        if (!loaderEl || loaderEl.classList.contains('hidden')) return;
        loaderEl.classList.add('hidden');
        setTimeout(function() {{
            loaderEl.style.display = "none";
        }}, 400);
    }}

    function attachLoaderHandlers() {{
        if (typeof network === "undefined" || !network) {{
            setTimeout(hideLoader, 1200);
            return;
        }}
        network.once("stabilizationIterationsDone", hideLoader);
        network.once("afterDrawing", function() {{
            setTimeout(hideLoader, 200);
        }});
        setTimeout(hideLoader, 5000);
    }}

    attachLoaderHandlers();

    function toggleLeaderboard() {{
        var content = document.getElementById('leaderboardContent');
        var caret = document.getElementById('leaderboardCaret');
        if (!content || !caret) return;
        var isOpen = content.style.display !== 'none';
        content.style.display = isOpen ? 'none' : 'block';
        caret.textContent = isOpen ? '▶' : '▼';
    }}

    document.getElementById('leaderboardHeader').addEventListener('click', toggleLeaderboard);

    function showAllNodes() {{
        var nodes = network.body.data.nodes.get();
        nodes.forEach(n => {{
            n.hidden = false;
            if (n.originalColor) n.color = n.originalColor;
            if (n.originalSize) n.size = n.originalSize;
        }});
        network.body.data.nodes.update(nodes);
        isFiltered = false;
        highlightedId = null;
        var panel = document.getElementById('infoPanel');
        if (panel) panel.style.display = "none";
    }}

    function focusIncomingTaggers(nodeId) {{
        // Get people who tagged this node (incoming neighbors)
        var incoming = network.getConnectedNodes(nodeId, 'from') || [];
        // Also keep people this node tagged (outgoing), so "taggers-only" users still show context.
        var outgoing = network.getConnectedNodes(nodeId, 'to') || [];
        var keep = new Set(incoming.concat(outgoing, [nodeId]));

        var nodes = network.body.data.nodes.get();
        nodes.forEach(n => {{
            n.hidden = !keep.has(n.id);
            if (n.originalColor) n.color = n.originalColor;
            if (n.originalSize) n.size = n.originalSize;
        }});
        network.body.data.nodes.update(nodes);
        isFiltered = true;
    }}

    function showPanelForNode(nodeId) {{
        var panel = document.getElementById('infoPanel');
        var nodeData = network.body.data.nodes.get(nodeId);
        panel.innerHTML = nodeData.panel || nodeData.title || ("<b>@" + nodeId + "</b>");
        panel.style.display = "block";
    }}

    function highlightNode() {{
        var name = document.getElementById('searchNode').value.trim();
        if (!name) return;

        var nodes = network.body.data.nodes.get();
        var matches = nodes.filter(n => n.id.toLowerCase().includes(name.toLowerCase()));
        if (matches.length === 0) {{
            alert("User not found in graph.");
            return;
        }}
        var found = matches[0];

        // Mirror click behavior: filter to relevant neighbors + open panel, no extra styling.
        focusIncomingTaggers(found.id);
        network.focus(found.id, {{
            scale: 1.35,
            animation: {{ duration: 800 }}
        }});

        showPanelForNode(found.id);
    }}

    document.getElementById('searchNode').addEventListener('keydown', function(e) {{
        if (e.key === 'Enter') {{
            e.preventDefault();
            highlightNode();
        }}
    }});

    document.addEventListener('keydown', function(e) {{
        if (e.key === 'Escape') {{
            showAllNodes();
        }}
    }});

    network.on("click", function(params) {{
        var panel = document.getElementById('infoPanel');

        if (params.nodes.length === 0) {{
            if (isFiltered || highlightedId) showAllNodes();
            if (panel) panel.style.display = "none";
            return;
        }}

        var clickedId = params.nodes[0];

        if (highlightedId) {{
            var nodes = network.body.data.nodes.get();
            nodes.forEach(n => {{
                if (n.originalColor) n.color = n.originalColor;
                if (n.originalSize) n.size = n.originalSize;
            }});
            network.body.data.nodes.update(nodes);
            highlightedId = null;
        }}

        focusIncomingTaggers(clickedId);
        showPanelForNode(clickedId);
    }});
    </script>
    """

    html = html.replace("</body>", injected + "</body>")
    output_html.write_text(html, encoding="utf-8")


def make_interactive_graph(
    graph,
    user_tag_map: Dict[str, List[str]],
    dj_mentions,
    dj_unique_taggers,
    output_html: str | Path = "interactive_graph.html",
) -> None:
    """Build an interactive draggable graph using pyvis and inject custom UI."""
    net = Network(height="900px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
    net.force_atlas_2based(gravity=-30)

    leaderboard_html = _build_leaderboard_html(dj_mentions, dj_unique_taggers)
    _add_nodes_and_edges(net, graph, user_tag_map, dj_mentions, dj_unique_taggers)

    output_html = Path(output_html)
    net.write_html(str(output_html))
    _inject_custom_ui(output_html, leaderboard_html)
    print(f"Interactive graph created: {output_html}")
