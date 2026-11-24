# SESSION-2026-11-24-repo-size — Measure nODD repository size at current main

## Scope and evidence

A small infrastructure investigation of repository scale. The connected GitHub
branch API confirmed `main` at `78bef505c4e623739da204ce92e3aa7bc6f931c5`
(2026-11-19); all content measurements refer to that commit, before this journal
is added. Source: <https://api.github.com/repos/asalzburger/nodd/branches/main>.
The isolated task worktree began clean. Unrelated changes in existing checkouts
were preserved. No detector design, ADR, issue, or scientific tracking state changes.

## Selected conversation

User, exact: “How big (lines of and text code, number of files, gb) is the current nODD git repo?”

Assistant outcome, paraphrase: measure the current committed main separately
from history, local artifacts and submodule contents, and report physical source
lines separately from all text lines. Repository instructions require a draft
PR even for investigations; this journal is the reviewable deliverable.

## Decisions and outcomes

The [machine-readable measurement](../evidence/SESSION-2026-11-24-repo-size/repo-size.json)
retains totals, extension/directory breakdowns, largest files and submodule pins.
GB means decimal gigabytes (1,000,000,000 bytes).

| Metric | Files | Physical lines | Bytes |
| --- | ---: | ---: | ---: |
| All tracked file content | 5,298 | — | 601,300,442 |
| Text (NUL-free UTF-8) | 4,184 | 7,474,487 | 255,790,935 |
| Source plus build scripts | 766 | 107,854 | 6,346,137 |
| Markdown | 805 | 85,312 | 6,006,991 |
| JSON | 2,199 | 5,980,451 | 184,908,622 |
| SVG | 186 | 1,221,742 | 45,290,974 |
| Binary/compressed | 1,114 | — | 345,509,507 |

Rows overlap: source, Markdown, JSON and SVG are subsets of text. The entire
tracked tree is **0.601 GB** (0.560 GiB). Most of the text-line count is JSON
and SVG evidence rather than program code. `docs/` holds 567,340,928 bytes,
about 94% of tracked content.

The source definition includes `.py`, `.cpp`, `.hpp`, `.h`, `.c`, `.sh`, `.js`,
`.css`, and files named `CMakeLists.txt` or `Makefile`, wherever tracked.
Physical lines include comments, blank lines and any unterminated final line.
It is not a language-aware count of executable statements or uncommented lines.
The source breakdown is Python 95,756; C/C++ 9,835; JavaScript 715; shell 121;
CSS 108; CMake/Make 1,319 lines. No dependency source is recursively counted.

The pre-task local main clone's `.git` allocation was 793,696 KiB =
812,744,704 bytes (**0.813 GB**), including branches/worktree metadata. The
GitHub repository API returned `size: 775051` (about 0.794 GB when converted
from KiB). History/metadata size varies with packing, branches and local state;
it is not additional current source. Tracked content plus the observed local
Git allocation is roughly **1.41 GB**, before filesystem overhead and submodules.
The 13 pinned submodule contents, local datasets/caches/builds and sibling
worktrees are excluded. The existing local main working directory was behind
the measured remote commit, so its working-tree disk usage is not presented
as a current-main clean-checkout measurement.

## Commands and validation

The measurement used the Python standard library to stream `git archive` for
the full source commit, inspect each file's bytes, classify NUL-free UTF-8 text,
and count LF characters plus an unterminated final line. Summed sizes and file
count were independently verified with `git ls-tree -rlz` at the same commit:
5,298 blobs and 601,300,442 bytes. The 13 entries with mode `160000` were
recorded separately. No export attributes affect the measured tree.

A compact reproduction for the primary metrics, from a checkout containing the commit:

```sh
python3 - <<'PYCODE'
import collections, subprocess, tarfile
from pathlib import PurePosixPath
ref = '78bef505c4e623739da204ce92e3aa7bc6f931c5'
groups = collections.defaultdict(lambda: [0, 0, 0])
source = {'.py', '.cpp', '.hpp', '.h', '.c', '.sh', '.js', '.css'}
proc = subprocess.Popen(['git', 'archive', '--format=tar', ref], stdout=subprocess.PIPE)
with tarfile.open(fileobj=proc.stdout, mode='r|') as archive:
    for member in archive:
        if not member.isfile() and not member.issym():
            continue
        data = archive.extractfile(member).read() if member.isfile() else member.linkname.encode()
        path = PurePosixPath(member.name)
        is_text = b'\0' not in data
        if is_text:
            try:
                data.decode('utf-8')
            except UnicodeDecodeError:
                is_text = False
        lines = data.count(b'\n') + bool(data and not data.endswith(b'\n')) if is_text else 0
        keys = ['all', 'text' if is_text else 'binary']
        if path.suffix.lower() in source or path.name in {'CMakeLists.txt', 'Makefile'}:
            keys.append('source')
        for key in keys:
            for index, value in enumerate([1, len(data), lines]):
                groups[key][index] += value
assert proc.wait() == 0
print('group: [files, bytes, physical_text_lines]')
print(dict(groups))
PYCODE
```

Other observations: `git count-objects -vH`, `du -sk .git`, and connected GitHub
repository metadata. An initial worktree command ran from the parent workspace
and failed to resolve `origin/main` (exit 128); it succeeded from the nODD clone.
Final journal/interaction validators and token-site build results are retained
in the paired JSON once actually run. No geometry/runtime tests are relevant.

## Changes and revision links

Only the paired journal, compact measurement evidence and this PR's interaction
record are changed. The enclosing Git history provides the result commit.
No source implementation or dependency/inventory changes are made.

## Token accounting

Exact per-turn counters were not exposed for this active task; `usage` remains
empty. This means unknown usage, not zero. No private client archives were read.
`session_log.py summary` passed: 305 sessions, 589 historical observed turns;
observed input 3,319,239,723 and output 13,881,824. This task has no observed
usage and contributes no counters to those historical sums.

## Follow-up

Review the draft infrastructure PR. No design approval or merge is requested.
Counts remain pinned to the stated source commit and exclude this task's files.
