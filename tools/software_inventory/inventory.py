#!/usr/bin/env python3
"""Offline software inventory, generated page and dependency-review receipts."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
DATA = "software/inventory.json"
PAGE = "docs/software-inventory.md"
CATEGORIES = {
    "spack": "Externals from the pre-existing Spack build",
    "validation": "External simulation, testing and validation software",
    "acts-examples": "nODD source used with ActsExamples",
    "cross-validation": "nODD cross-validation and design controls",
    "analysis": "Analysis software and nODD analysis source",
    "infrastructure": "Build, documentation and repository tooling",
}
CODE_SUFFIXES = {".py", ".sh", ".cpp", ".cc", ".cxx", ".hpp", ".h", ".js", ".cmake"}
SCOPES = {"software", "tools", "detector", "prototypes", "skills"}
EXPLICIT_INPUTS = {
    ".gitmodules", "Makefile", "software/Makefile", "software/env/run.sh",
    "software/env/truth_tracking.sh", "software/env/build_idres.py",
    "software/env/doctor.py", "skills/acts-spack/references/nodes.json",
}


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args]).decode()


def files_in(root):
    # Include new worktree files, exclude ignored build/runtime data, never recurse
    # into gitlinks. Thus this also works in CI without submodule initialization.
    return sorted(set(git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0")) - {""})


def pins_in(root):
    pins = {}
    for record in git(root, "ls-files", "--stage", "-z").split("\0"):
        if not record:
            continue
        header, path = record.split("\t", 1)
        mode, sha, stage = header.split()
        if mode == "160000" and path.startswith("software/submodules/"):
            if stage != "0":
                raise ValueError(f"unmerged gitlink: {path}")
            pins[path] = sha
    return pins


def families_in(files):
    families = set()
    for path in files:
        p = PurePosixPath(path)
        parts = p.parts
        if parts[0] not in SCOPES or (p.suffix not in CODE_SUFFIXES and p.name != "CMakeLists.txt"):
            continue
        if parts[:3] == ("software", "source", "ActsExamples") and len(parts) > 4:
            family = "/".join(parts[:4])
        elif parts[:2] in (("software", "analysis"), ("software", "source")):
            family = "/".join(parts[:3])
        elif parts[:2] == ("software", "running"):
            family = path  # Steering entry points have separate purposes.
        elif parts[0] == "detector":
            family = "detector"
        elif len(parts) > 2:
            family = "/".join(parts[:2])
        else:
            family = path
        families.add(family)
    return families


def inputs_in(files):
    inputs = set()
    for path in files:
        p = PurePosixPath(path)
        if path in EXPLICIT_INPUTS or path.startswith(".github/workflows/"):
            inputs.add(path)
        elif p.parts[0] in SCOPES or len(p.parts) == 1:
            if ("requirements" in p.name or p.name in {
                "CMakeLists.txt", "pyproject.toml", "Pipfile", "Pipfile.lock",
                "uv.lock", "spack.yaml", "spack.lock", "environment.yml",
                "environment.yaml", "package.json", "package-lock.json",
                "conanfile.py", "conanfile.txt", "conan.lock", "Makefile",
            } or p.suffix == ".cmake"):
                inputs.add(path)
    return inputs


def receipts(root, files):
    return {path: hashlib.sha256((root / path).read_bytes()).hexdigest()
            for path in sorted(inputs_in(files)) if (root / path).is_file()}


def safe_path(path):
    return isinstance(path, str) and bool(path) and not PurePosixPath(path).is_absolute() and ".." not in PurePosixPath(path).parts and "\\" not in path


def validate(root, data, files, pins):
    if data.get("schema_version") != 1:
        raise ValueError("unsupported inventory schema_version")
    date.fromisoformat(data["updated"])
    if not re.fullmatch(r"[0-9a-f]{40}", data["source_revision"]):
        raise ValueError("source_revision must be the full evidence commit SHA")
    ids, owners, gitlinks = set(), set(), set()
    families = families_in(files)
    for c in data["components"]:
        if c["id"] in ids:
            raise ValueError(f"duplicate component ID: {c['id']}")
        ids.add(c["id"])
        if c["category"] not in CATEGORIES:
            raise ValueError(f"unknown category: {c['category']}")
        for key in ("id", "name", "usage", "integration", "version", "installation"):
            if not isinstance(c[key], str) or not c[key].strip():
                raise ValueError(f"{c['id']}: missing {key}")
        if not c["evidence"]:
            raise ValueError(f"{c['id']}: missing evidence")
        for path in c["evidence"] + c["paths"]:
            if (not safe_path(path) or not (root / path).exists()
                    or not (root / path).resolve().is_relative_to(root.resolve())):
                raise ValueError(f"{c['id']}: unsafe or missing path: {path}")
        for path in c["paths"]:
            if path not in families:
                raise ValueError(f"{c['id']}: obsolete/unknown code family: {path}")
            if path in owners:
                raise ValueError(f"duplicate family ownership: {path}")
            owners.add(path)
        for pr in c["prs"]:
            if not re.fullmatch(r"https://github.com/[\w.-]+/[\w.-]+/pull/[1-9][0-9]*", pr):
                raise ValueError(f"{c['id']}: invalid PR URL: {pr}")
        if c.get("gitlink"):
            if c["gitlink"] not in pins or c["gitlink"] in gitlinks:
                raise ValueError(f"{c['id']}: unknown/duplicate software gitlink")
            gitlinks.add(c["gitlink"])
    if missing := families - owners:
        raise ValueError("uninventoried code families: " + ", ".join(sorted(missing)))
    if missing := set(pins) - gitlinks:
        raise ValueError("uninventoried software submodules: " + ", ".join(sorted(missing)))


def render(data):
    def link(path):
        return f"[{path}](../{path})"

    def cell(value):
        return value.replace("|", "\\|").replace("\n", " ")

    lines = [
        "<!-- Generated by tools/software_inventory/inventory.py; edit software/inventory.json. -->",
        "# Software inventory", "",
        f"Updated: {data['updated']}. Request: [issue #124](https://github.com/asalzburger/nodd/issues/124).",
        f"Initial evidence revision: `{data['source_revision']}`; subsequent changes are recorded in Git.", "",
        "This inventories nODD's maintained software families and directly used externals, including optional and historical tools. "
        "It is not a complete export of Spack's transitive dependency graph. Versions below are recorded observations or source pins, "
        "not a claim that this checkout has a working native runtime. No shared installation was changed or activated for this inventory.", "",
        "The September node registry is historical; later campaign receipts record different Spack versions. "
        "Keep each result bound to its own environment receipt. Follow the "
        "[ACTS Spack preflight](../skills/acts-spack/SKILL.md) before native execution, then use "
        "[make doctor](../software/env/doctor.py) to record actual versions, fingerprints and datasets. "
        "Installed headers/libraries do not establish full source availability.", "",
        "PR links flag recorded source or integration work, not the installer, sole author, merge status or design approval. "
        "For migrated source, consult the [source notices](../software/source/NOTICE.md). "
        "A missing PR is explicitly reported; no PR number is inferred from a file's timestamp.", "",
        "## Keeping this page current", "",
        "When adding, removing or changing software, update its stable component entry in "
        "[software/inventory.json](../software/inventory.json) in the same PR. Record keywords, integration, installation/use recipe, "
        "version or unknown status, evidence and related PRs. Include a new analysis environment, an optional tool and "
        "a new external used inside an existing script. Describe unexecuted plans as such.", "",
        "After reviewing dependency/source-pin changes and updating component descriptions, run from the repository root:", "",
        "```sh", "python3 -B tools/software_inventory/inventory.py refresh",
        "python3 -B tools/software_inventory/inventory.py check",
        "python3 -B -m unittest discover -s tools/software_inventory -p 'test_*.py' -v", "```", "",
        "`refresh` updates reviewed input fingerprints and renders this page; it does not discover installation facts or approve descriptions. "
        "Stage an intentional gitlink update before refreshing its indexed pin. Review both JSON and generated Markdown diffs. "
        "Project CI and `make check` reject uncovered code families/submodules, changed dependency/build/runtime recipes, "
        "stale source pins and stale page output. Checks run offline without initializing submodules or activating Spack.", "",
        "Automatic discovery covers executable source families in `software`, `tools`, `detector`, `prototypes` and `skills`, "
        "plus dependency manifests, CMake/Make recipes and CI workflows. It excludes ignored builds, third-party gitlink contents, "
        "historical source snapshots under `logs` and publication snapshots under `docs`. "
        "New imports or tools introduced within an existing family still require author/reviewer inventory review; "
        "a matching fingerprint alone cannot establish semantic completeness.", "",
    ]
    for category, title in CATEGORIES.items():
        lines += [f"## {title}", "", "| Component / keywords | Integration and installation/use | Version / status | Source and PR evidence |",
                  "| --- | --- | --- | --- |"]
        for c in data["components"]:
            if c["category"] != category:
                continue
            evidence = list(dict.fromkeys(c["paths"] + c["evidence"]))
            refs = "; ".join(link(p) for p in evidence)
            refs += "; " + (", ".join(f"[{pr.split('github.com/')[1]}]({pr})" for pr in c["prs"]) if c["prs"] else "PR: not established")
            version = c["version"]
            if c.get("gitlink"):
                version += f"; gitlink `{data['source_pins'][c['gitlink']]}`"
            row = [f"**{c['name']}**<br>{c['usage']}", f"{c['integration']}<br>{c['installation']}", version, refs]
            lines.append("| " + " | ".join(cell(v) for v in row) + " |")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "refresh"))
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        data = json.loads((root / DATA).read_text())
        files, pins = files_in(root), pins_in(root)
        validate(root, data, files, pins)
        current = receipts(root, files)
        if args.command == "refresh":
            data["checked_inputs"], data["source_pins"] = current, pins
            (root / DATA).write_text(json.dumps(data, indent=2) + "\n")
            (root / PAGE).write_text(render(data))
        else:
            changed = sorted(k for k in current.keys() | data["checked_inputs"].keys()
                             if current.get(k) != data["checked_inputs"].get(k))
            if changed:
                raise ValueError("review changed dependency/build inputs, update inventory and refresh: " + ", ".join(changed))
            if pins != data["source_pins"]:
                raise ValueError("software source pins changed; review component versions and refresh")
            if (root / PAGE).read_text() != render(data):
                raise ValueError("generated inventory page is stale; refresh after editing inventory")
        print(f"Software inventory {args.command}: {len(data['components'])} components, "
              f"{len(families_in(files))} code families, {len(current)} reviewed inputs, {len(pins)} software pins")
        return 0
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Software inventory: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
