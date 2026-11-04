#!/usr/bin/env python3
"""Build a dependency-free usage site from validated, disjoint journal counters."""

import argparse
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from html import escape
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote

import interactions as conversation_export

ROOT = Path(__file__).resolve().parents[2]
FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)
MODES = {"total_tokens": "Combined", "input_tokens": "Input", "output_tokens": "Output"}
REPOSITORY = "https://github.com/asalzburger/nodd"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def journal_module(root):
    spec = importlib.util.spec_from_file_location(
        "usage_journal", root / "tools/session_logging/session_log.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def utc(value):
    if type(value) in (int, float):
        return datetime.fromtimestamp(value, timezone.utc)
    require(
        type(value) is str and value.endswith("Z"),
        "Expected a recorded UTC completion time",
    )
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def inventory_turns(data):
    for turn in data.get("completed_turns", []):
        yield turn, data.get("thread_id")
    for thread in data.get("threads", []):
        for turn in thread.get("turns", []):
            yield turn, thread.get("thread_id")


def collect(root):
    logger = journal_module(root)
    records = logger.load_records(root)
    summary = logger.summarize(records)
    owned = {
        (entry["client_thread_id"], entry["turn_id"]): (record, entry)
        for record in records
        for entry in record["usage"]
    }
    dates = {}
    for path in sorted((root / "logs/usage").glob("*.json")):
        data = logger.read_json(path)
        for turn, thread in inventory_turns(data):
            entry = turn.get("usage_entry") or {}
            key = (
                entry.get("client_thread_id") or turn.get("thread_id") or thread,
                entry.get("turn_id") or turn.get("turn_id"),
            )
            if key not in owned:
                continue  # Inventories are evidence, never extra usage.
            counters = turn.get("tokens") or entry
            completed = turn.get("completed_at")
            if (
                turn.get("status") == "inProgress"
                and turn.get("closed") is False
                and completed is None
                and turn.get("end_ordinal") is None
            ):
                # Retained recovery snapshots can predate a turn's completion.
                # They corroborate lower bounds, never final counters or dates.
                for field in FIELDS:
                    partial = counters.get(field)
                    final = owned[key][1][field]
                    require(
                        partial is None or (
                            type(partial) is int and partial >= 0
                            and (final is None or partial <= final)
                        ),
                        f"{path.name}: invalid provisional counters for an owned turn",
                    )
                continue
            require(
                all(counters.get(field) == owned[key][1][field] for field in FIELDS),
                f"{path.name}: conflicting counters for an owned turn",
            )
            if completed is None:
                continue
            require(
                turn.get("closed") is True,
                f"{path.name}: owned turn has an unclosed accounting boundary",
            )
            at = utc(completed)
            require(
                key not in dates or dates[key] == at,
                f"{path.name}: conflicting completion times",
            )
            dates[key] = at
    grouped = defaultdict(list)
    undated = []
    for key, (record, entry) in owned.items():
        if key in dates:
            grouped[dates[key].date().isoformat()].append((record, entry))
        else:
            undated.append(entry)
    cumulative = {field: 0 for field in FIELDS}
    known = {field: 0 for field in FIELDS}
    series = []
    for step, (day, contributions) in enumerate(sorted(grouped.items()), 1):
        entries = [entry for _, entry in contributions]
        sessions = {}
        for record, entry in contributions:
            item = sessions.setdefault(record['session_id'], {
                'session_id': record['session_id'], 'title': record['title'],
                'narrative': record['narrative'], 'entries': [],
                'prs': sorted({int(match[1]) for identifier in record['work']['related_ids']
                               if (match := re.fullmatch(r'PR(?:\s*#|-?)([1-9][0-9]*)', identifier))}),
            })
            item['entries'].append(entry)
        work = []
        for item in sessions.values():
            session_entries = item.pop('entries')
            work.append({**item, 'turns': len(session_entries), 'tokens': {
                field: logger.observed([entry[field] for entry in session_entries])
                for field in FIELDS}})
        work.sort(key=lambda item: (-(item['tokens']['total_tokens']['sum'] or 0), item['session_id']))
        values = {
            field: logger.observed([entry[field] for entry in entries])
            for field in FIELDS
        }
        for field in FIELDS:
            cumulative[field] += values[field]["sum"] or 0
            known[field] += values[field]["known"]
        series.append(
            {
                "date": day,
                "step": step,
                "work": work,
                "turns": len(entries),
                "daily": values,
                "cumulative": {
                    field: cumulative[field] if known[field] else None
                    for field in FIELDS
                },
            }
        )
    manifest = logger.read_json(root / "project/token-milestones.json")
    require(manifest.get("schema_version") == 1, "Unsupported token milestone schema")
    features = manifest["features"]
    require(
        type(features) is list and len(features) <= 12,
        "Use at most twelve curated feature markers",
    )
    ids = set()
    for feature in features:
        require(
            set(feature) == {"id", "label", "at", "revision", "url"},
            "Unexpected feature fields",
        )
        require(
            type(feature["id"]) is str
            and re.fullmatch(r"PR-[1-9][0-9]*", feature["id"])
            and feature["id"] not in ids,
            "Duplicate/invalid feature ID",
        )
        ids.add(feature["id"])
        require(
            type(feature["label"]) is str and 0 < len(feature["label"]) <= 60,
            "Invalid feature label",
        )
        utc(feature["at"])
        require(
            re.fullmatch("[0-9a-f]{40}", feature["revision"]) is not None,
            "Feature needs a full source revision",
        )
        require(
            re.fullmatch(re.escape(REPOSITORY) + r"/pull/[1-9][0-9]*", feature["url"])
            is not None,
            "Invalid feature evidence URL",
        )
        require(
            feature["url"].endswith("/" + feature["id"].removeprefix("PR-")),
            "Feature ID and evidence URL disagree",
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "cat-file",
                "-e",
                feature["revision"] + "^{commit}",
            ],
            check=True,
            capture_output=True,
        )
    return {
        "schema_version": 1,
        "summary": {
            key: summary[key]
            for key in (
                "sessions",
                "sessions_with_usage",
                "sessions_without_usage",
                "usage_turns",
                "tokens",
            )
        },
        "dated_turns": len(dates),
        "undated_turns": len(undated),
        "undated_tokens": {
            field: logger.observed([entry[field] for entry in undated])
            for field in FIELDS
        },
        "series": series,
        "features": sorted(features, key=lambda feature: feature["at"]),
    }


def number(value):
    return "Unknown" if value is None else f"{value:,}"


def work_label(point):
    """Name the largest recorded session and make additional work explicit."""
    work = point['work']
    label = work[0]['title']
    if len(work) > 1:
        label += f' + {len(work)-1} more session' + ('s' if len(work) > 2 else '')
    return label


def work_breakdown(data):
    revision = data['metadata']['source_commit']
    steps = []
    for point in reversed(data['series']):
        sessions = []
        for item in point['work']:
            source = REPOSITORY + '/blob/' + revision + '/' + quote(item['narrative'], safe='/')
            prs = ''.join(f' · <a href="{REPOSITORY}/pull/{pr}">PR #{pr}</a>' for pr in item['prs'])
            counters = []
            for field, label in (('total_tokens', 'Combined'), ('input_tokens', 'Input'), ('output_tokens', 'Output')):
                counter = item['tokens'][field]
                coverage = f' · {counter["known"]}/{counter["records"]} turns measured' if counter['known'] < counter['records'] else ''
                counters.append(f'<div><dt>{label}</dt><dd>{number(counter["sum"])}<small>{coverage}</small></dd></div>')
            sessions.append(f'<li><h4><a href="{escape(source,quote=True)}">{escape(item["title"])}</a></h4><p class="work-meta">{item["turns"]} recorded turn(s){prs}</p><dl>{"".join(counters)}</dl></li>')
        daily_total = point['daily']['total_tokens']['sum']
        total_label = 'Unknown' if daily_total is None else '+' + number(daily_total)
        steps.append(f'<details class="work-step" id="usage-step-{point["date"]}"><summary><span class="step-badge">{point["step"]}</span><span class="step-description"><span class="step-date">{point["date"]} UTC</span><strong>{escape(work_label(point))}</strong></span><span class="step-total">{total_label}<small>observed combined tokens</small></span></summary><div class="step-body"><p>Recorded session contributions for this UTC day. A session can cover several tasks or PRs; the linked journal defines its scope.</p><ul class="work-sessions">{"".join(sessions)}</ul></div></details>')
    return ''.join(steps) or '<p class="empty">No dated work observations. Undated usage stays outside the curve.</p>'


def chart(data, field, built_at):
    points = [
        point for point in data["series"] if point["cumulative"][field] is not None
    ]
    if not points:
        return '<p class="empty">No dated observations for this counter. Missing measurements are unknown.</p>'
    times = [utc(point["date"] + "T00:00:00Z").timestamp() for point in points]
    end = max(
        [utc(built_at).timestamp(), max(times)]
        + [utc(feature["at"]).timestamp() for feature in data["features"]]
    )
    start = (
        min(
            [times[0]]
            + [utc(feature["at"]).timestamp() for feature in data["features"]]
        )
        - 86400
    )
    span = max(86400, end - start)
    left, right, top, bottom = 84, 1044, 28, 308
    maximum = max(point["cumulative"][field] for point in points) or 1
    ylimit = maximum * 1.12
    x = lambda value: left + (right - left) * (value - start) / span
    y = lambda value: bottom - (bottom - top) * value / ylimit
    labels = []
    occupied = []
    for index, feature in enumerate(data["features"], 1):
        at = utc(feature["at"]).timestamp()
        position = x(at)
        width = min(192, max(118, len(feature["label"]) * 6.1))
        begin = max(left, min(position - width / 2, right - width))
        row = 0
        while row < len(occupied) and any(
            begin < stop + 14 and begin + width > other - 14
            for other, stop in occupied[row]
        ):
            row += 1
        if row == len(occupied):
            occupied.append([])
        occupied[row].append((begin, begin + width))
        labels.append((feature, position, begin, row, index))
    height = 402 + len(occupied) * 52
    parts = [
        f'<svg viewBox="0 0 1100 {height}" role="group" aria-label="{MODES[field]} cumulative observed tokens, with work steps and feature milestones">'
    ]
    for tick in range(5):
        value = ylimit * tick / 4
        yy = y(value)
        label = f"{value/1e6:.1f}M" if ylimit >= 1e6 else f"{value:,.0f}"
        parts.append(
            f'<line class="grid" x1="{left}" x2="{right}" y1="{yy:.2f}" y2="{yy:.2f}"/><text class="axis" x="{left-15}" y="{yy+4:.2f}" text-anchor="end">{label}</text>'
        )
    for tick in range(6):
        at = start + span * tick / 5
        label = datetime.fromtimestamp(at, timezone.utc).strftime("%d %b")
        parts.append(
            f'<text class="axis" x="{x(at):.2f}" y="338" text-anchor="middle">{label}</text>'
        )
    for feature, position, begin, row, index in labels:
        label_y = 389 + row * 52
        parts.append(
            f'<line class="milestone-line" x1="{position:.2f}" x2="{position:.2f}" y1="{top}" y2="{label_y-18}"/>'
        )
        parts.append(
            f'<a href="{escape(feature["url"],quote=True)}"><circle class="feature-dot" cx="{position:.2f}" cy="{bottom}" r="4"/><text class="feature" x="{begin:.2f}" y="{label_y}">{escape(feature["label"])}</text><text class="feature-date" x="{begin:.2f}" y="{label_y+17}">{utc(feature["at"]).strftime("%d %b")} · #{feature["id"].removeprefix("PR-")}</text></a>'
        )
    coordinates = [(x(times[0] - 86400), y(0))] + [
        (x(at), y(point["cumulative"][field])) for at, point in zip(times, points)
    ]
    path = f"M{coordinates[0][0]:.2f},{coordinates[0][1]:.2f}" + "".join(
        f" H{xx:.2f} V{yy:.2f}" for xx, yy in coordinates[1:]
    )
    area = (
        path
        + f" L{coordinates[-1][0]:.2f},{bottom} L{coordinates[0][0]:.2f},{bottom} Z"
    )
    parts.append(f'<path class="area" d="{area}"/><path class="curve" d="{path}"/>')
    for at, point in zip(times, points):
        value = point["cumulative"][field]
        tip = (f"Step {point['step']} · {point['date']} UTC\n{work_label(point)}\n"
               f"+{number(point['daily'][field]['sum'])} observed {MODES[field].lower()} tokens this day\n"
               f"{number(value)} cumulative · {point['turns']} recorded turns. Select for the session breakdown.")
        xx, yy = x(at), y(value)
        parts.append(
            f'<a class="step-link" href="#usage-step-{point["date"]}" data-step="usage-step-{point["date"]}" data-tip="{escape(tip,quote=True)}" aria-label="{escape(tip,quote=True)}"><title>{escape(tip)}</title><circle class="observation" cx="{xx:.2f}" cy="{yy:.2f}" r="4"/><circle class="step-marker" cx="{xx:.2f}" cy="{yy-17:.2f}" r="10"/><text class="step-number" x="{xx:.2f}" y="{yy-14:.2f}" text-anchor="middle" aria-hidden="true">{point["step"]}</text></a>'
        )
    if end > times[-1] + 86400:
        parts.append(
            f'<line class="carry" x1="{x(times[-1]):.2f}" x2="{right}" y1="{y(points[-1]["cumulative"][field]):.2f}" y2="{y(points[-1]["cumulative"][field]):.2f}"/>'
        )
    parts.append("</svg>")
    return "".join(parts)


def navigation(active):
    return '<nav class="site-tabs" aria-label="Views">' + ''.join(
        f'<a href="{url}"' + (' aria-current="page"' if name == active else '') + f'>{label}</a>'
        for name, label, url in (('usage', 'Token usage', './'),
                                 ('interactions', 'Interactions', 'interactions.html'))
    ) + '</nav>'


def render(data):
    summary = data["summary"]
    metadata = data["metadata"]
    totals = summary["tokens"]
    cards = []
    for label, field in [
        ("Observed tokens", "total_tokens"),
        ("Input", "input_tokens"),
        ("Output", "output_tokens"),
    ]:
        cards.append(
            f'<article class="metric"><span>{label}</span><strong>{number(totals[field]["sum"])}</strong><small>{totals[field]["known"]} observed turns with this counter</small></article>'
        )
    cards.append(
        f'<article class="metric coverage"><span>Session coverage</span><strong>{summary["sessions_with_usage"]}<i> / {summary["sessions"]}</i></strong><small>{summary["sessions_without_usage"]} sessions have no recorded counters</small></article>'
    )
    buttons = "".join(
        f'<button type="button" data-mode="{field}" aria-pressed="{str(index==0).lower()}">{label}</button>'
        for index, (field, label) in enumerate(MODES.items())
    )
    charts = "".join(
        f'<div data-chart="{field}" {"hidden" if index else ""}>{chart(data,field,metadata["built_at"])}</div>'
        for index, field in enumerate(MODES)
    )
    feature_links = "".join(
        f'<li><a href="{escape(feature["url"],quote=True)}">{escape(feature["label"])} · {utc(feature["at"]).date().isoformat()}</a></li>'
        for feature in data["features"]
    )
    rows = []
    for point in data["series"]:
        values = point["daily"]
        cumulative = point["cumulative"]["total_tokens"]
        rows.append(
            f'<tr><th scope="row">{point["date"]}</th><td>{point["turns"]}</td><td>{number(values["input_tokens"]["sum"])}</td><td>{number(values["output_tokens"]["sum"])}</td><td>{number(cumulative)}</td></tr>'
        )
    timeline_end = data["series"][-1]["date"] if data["series"] else "unavailable"
    content = f"""<header><a class="brand" href="./">nODD<span> / resource ledger</span></a><a href="{REPOSITORY}">Repository ↗</a></header>{navigation('usage')}
<main><section class="intro"><p class="eyebrow">PROJECT RESOURCES</p><h1>Cumulative token usage</h1><p>Recorded input and output over time, alongside major project features.</p><div class="chips"><span>{summary['usage_turns']} disjoint turn observations</span><span>Latest observations: {timeline_end} UTC</span><span>Coverage is partial</span></div></section>
<section class="metrics" aria-label="Observed token totals">{''.join(cards)}</section>
<section class="chart-panel"><div class="chart-heading"><div><p class="eyebrow">THE BUILD-UP</p><h2>Usage & recorded work</h2></div><div class="modes" aria-label="Token counter">{buttons}</div></div><p class="chart-note">Each numbered step links to the recorded work for that UTC day. Hover or focus for its label; select it for the session breakdown. Feature markers below show merge dates, not scientific sign-off.</p><div class="chart-shell">{charts}<div class="tooltip" role="status" hidden></div></div><div class="legend"><span class="solid">Observed cumulative counters · numbered work steps</span><span class="dashed">Known subtotal carried forward; new usage unmeasured</span></div></section>
<section class="work-panel" aria-labelledby="work-heading"><p class="eyebrow">WHERE THE TOKENS WENT</p><h2 id="work-heading">Work behind each step</h2><p class="work-note">Every recorded step has a label from its owning sessions, ordered by observed combined tokens. Expand a day for all contributions and source journals. Counts are observed input + output; missing measurements remain unknown.</p><div class="work-steps">{work_breakdown(data)}</div></section>
<section class="accounting"><div><p class="eyebrow">COUNTED ONCE</p><h2>Input + output = total</h2><p>Cached input ({number(totals['cached_input_tokens']['sum'])}) and reasoning output ({number(totals['reasoning_output_tokens']['sum'])}) are already included in their parent counters.</p></div><div><p class="eyebrow">VISIBLE GAPS</p><h2>Observed, not complete</h2><p>Missing counters are unknown, never zero. {data['dated_turns']} of {summary['usage_turns']} observations have exact completion dates. {data['undated_turns']} undated observations stay outside the curve. This is a usage ledger, not a billing estimate.</p></div></section>
<details class="daily"><summary>Daily observations and exact cumulative totals</summary><div class="table-scroll"><table><thead><tr><th scope="col">UTC date</th><th scope="col">Turns</th><th scope="col">Input</th><th scope="col">Output</th><th scope="col">Cumulative total</th></tr></thead><tbody>{''.join(rows) or '<tr><td colspan="5">No dated token observations.</td></tr>'}</tbody></table></div></details>
<details class="daily"><summary>Feature milestone sources</summary><ul>{feature_links}</ul></details>
<footer><p>Source <a href="{REPOSITORY}/commit/{metadata['source_commit']}"><code>{metadata['source_commit'][:12]}</code></a> · Built {metadata['built_at']}<br>{'Preview includes uncommitted changes.' if metadata['working_tree_dirty'] else 'Versioned source snapshot.'}</p><p><a href="usage.json">Download chart data</a> · <a href="{REPOSITORY}/tree/{metadata['source_commit']}/logs/usage">Accounting evidence</a> · <a href="{REPOSITORY}/blob/{metadata['source_commit']}/tools/token_usage/README.md">Method</a></p></footer></main>"""
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="nODD cumulative observed token usage and project feature milestones"><title>nODD · Token usage</title><link rel="stylesheet" href="style.css"><link rel="stylesheet" href="interactions.css"><script src="app.js" defer></script></head><body>{content}</body></html>'


def render_interactions(index):
    metadata = index['metadata']
    count = len(index['pull_requests'])
    revision = metadata['source_commit']
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="nODD PR conversations between humans and agents, with sourced interaction evidence">
<title>nODD · PR interactions</title><link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="interactions.css"><script src="interactions.js" defer></script></head><body>
<header><a class="brand" href="./">nODD<span> / resource ledger</span></a><a href="{REPOSITORY}">Repository ↗</a></header>
{navigation('interactions')}
<main class="interaction-page"><section class="intro"><p class="eyebrow">PEOPLE, AGENTS & DECISIONS</p>
<h1>PR conversations</h1><p>Explore the inputs, questions and responses behind each pull request.</p>
<div class="chips"><span>{count} pull requests</span><span>Source-linked conversations</span><span>Historical coverage is partial</span></div></section>
<div class="interaction-layout"><aside class="pr-picker" aria-label="Pull request navigation">
<label for="pr-search">Find a pull request</label><input id="pr-search" type="search" placeholder="Number, title or party…" autocomplete="off">
<p id="pr-results" role="status" aria-live="polite">Loading pull requests…</p><div id="pr-list" class="pr-list"></div></aside>
<section id="conversation-panel" class="conversation-panel" aria-labelledby="pr-title">
<div id="interaction-status" role="status" aria-live="polite">Loading interaction records…</div>
<div id="pr-detail" hidden><div class="pr-heading"><div><p id="pr-number" class="eyebrow"></p><h2 id="pr-title">Pull request</h2><div id="pr-coverage"></div></div><a id="pr-github" href="{REPOSITORY}">View PR</a></div>
<div id="participants" class="participant-strip"></div><div class="conversation-controls"><label for="source-select">Conversation source</label><select id="source-select"></select></div>
<div id="conversation" role="feed" aria-label="PR interaction messages"></div>
<details class="evidence-panel"><summary>Roles, tools & token references</summary><div id="pr-evidence"></div></details></div></section></div>
<noscript><p>Enable JavaScript to navigate conversations, or <a href="{REPOSITORY}/tree/{revision}/interactions">read the canonical interaction records</a>.</p></noscript>
<footer><p>Source <a href="{REPOSITORY}/commit/{revision}"><code>{revision[:12]}</code></a> · Built {escape(metadata['built_at'])}<br>{'Preview includes uncommitted changes.' if metadata['working_tree_dirty'] else 'Versioned source snapshot.'}</p><p><a href="interactions.json">Download PR index</a> · <a href="{REPOSITORY}/blob/{revision}/interactions/README.md">Sources & method</a></p></footer>
</main></body></html>'''


def build(root, output, built_at):
    root = root.resolve()
    output = output.resolve()
    utc(built_at)
    require(
        not root.is_relative_to(output), "Output cannot contain the source repository"
    )
    if output.is_relative_to(root):
        require(
            output.relative_to(root).parts[0] == "_site",
            "Repository output must be under _site/",
        )
    data = collect(root)
    data["metadata"] = {
        "source_commit": subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip(),
        "working_tree_dirty": bool(
            subprocess.check_output(
                ["git", "-C", str(root), "status", "--porcelain"], text=True
            ).strip()
        ),
        "built_at": built_at,
    }
    interaction_index, interaction_details = conversation_export.collect(root, data['metadata'])
    allowed = {"index.html", "style.css", "app.js", "usage.json", ".nojekyll",
               "interactions.html", "interactions.css", "interactions.js", "interactions.json"}
    allowed.update(interaction_details)
    if output.exists():
        require(
            all(
                not path.is_symlink() and (
                    path.is_file() and path.relative_to(output).as_posix() in allowed
                    or path.is_dir() and path.relative_to(output).as_posix() == 'interactions'
                )
                for path in output.rglob("*")
            ),
            "Unexpected/stale output files; use a fresh build directory",
        )
    output.mkdir(parents=True, exist_ok=True)
    (output / "index.html").write_text(render(data))
    (output / "interactions.html").write_text(render_interactions(interaction_index))
    (output / "interactions.json").write_text(json.dumps(interaction_index, indent=2, allow_nan=False) + '\n')
    for name, detail in interaction_details.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(detail, indent=2, allow_nan=False) + '\n')
    (output / "usage.json").write_text(
        json.dumps(data, indent=2, allow_nan=False) + "\n"
    )
    (output / ".nojekyll").write_text("")
    for name in ["style.css", "app.js", "interactions.css", "interactions.js"]:
        (output / name).write_bytes(Path(__file__).with_name(name).read_bytes())
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "build"])
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "_site/pages")
    parser.add_argument(
        "--built-at",
        default=datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
    )
    args = parser.parse_args()
    try:
        data = (
            collect(args.repo)
            if args.command == "validate"
            else build(args.repo, args.output, args.built_at)
        )
        print(
            f"{args.command.title()}: {data['summary']['usage_turns']} disjoint turns; {number(data['summary']['tokens']['total_tokens']['sum'])} observed tokens; {data['dated_turns']} dated turns."
        )
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
