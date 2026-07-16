#!/usr/bin/env python3
"""spec-lint — mechanical checks for spec-monkey specs.

Rides the parse contract the templates define (frontmatter scalars, FR/SC/INV
join keys, canonical section homes) to catch the defects a script settles faster
and cheaper than an LLM reviewer: unfilled placeholders, duplicate or unpaired
IDs, dangling INV citations, unresolved parents, bad status values, a missing
gate record on an approved spec, missing frontmatter. It judges no engineering —
that stays with reviewing-specs.

Not part of the portable skills; it's optional tooling. Stdlib only, no install.

Usage:
    tools/spec-lint.py [ROOT ...]           # lint; ROOT defaults to docs/specs
    tools/spec-lint.py --status [ROOT ...]   # roll up every spec's status/gate, no lint

Exit code: 0 if no ERROR, 1 if any ERROR (WARN never fails). CI-friendly. --status
always exits 0; it reports, it does not judge.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WORK_ITEM_STATUS = {"draft", "approved", "implemented", "shipped", "archived"}
PROJECT_STATUS = {"draft", "approved"}
DESIGN_STATUS = {"draft", "approved"}
PROFILES = {"full", "light"}
REQUIRED_FRONTMATTER = ("spec_monkey", "id", "kind", "status", "created", "updated")
# States that imply a human granted a gate: once approved, the approval record
# (approved_by) should persist through implementation and shipping.
GATED_STATUS = {"approved", "implemented", "shipped"}

# A placeholder is an <...> span that contains whitespace (a descriptive slot
# like "<short imperative title>"). Single-token spans (<id>, <base>..HEAD in a
# command) are legitimate and never flagged.
PLACEHOLDER_RE = re.compile(r"<[^<>\n]*\s[^<>\n]*>")
FR_DEF_RE = re.compile(r"^\s*-\s+\*\*(FR-\d+)\*\*")
SC_DEF_RE = re.compile(r"^\s*-\s+\*\*(SC-\d+)\*\*")
INV_DEF_RE = re.compile(r"\*\*(INV-\d+)\*\*")
INV_REF_RE = re.compile(r"\bINV-\d+\b")
HEADING_RE = re.compile(r"^(#{1,6})\s")


class Report:
    def __init__(self) -> None:
        self.errors = 0
        self.warns = 0

    def error(self, path: Path, msg: str) -> None:
        self.errors += 1
        print(f"{path}: ERROR {msg}")

    def warn(self, path: Path, msg: str) -> None:
        self.warns += 1
        print(f"{path}: WARN  {msg}")


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def has_approver(value: str) -> bool:
    """True if approved_by names someone. An empty scalar or an empty list ([]) does not."""
    v = value.strip().strip("[]").strip()
    return bool(v)


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Return the top YAML block's scalar keys, or None if there is no block."""
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None
    fm: dict[str, str] = {}
    for line in lines[1:end]:
        line = line.split("#", 1)[0].rstrip()
        if not line or line[0].isspace():
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm


def find_placeholders(path: Path, text: str, rep: Report) -> None:
    body = strip_html_comments(text)
    for n, line in enumerate(body.splitlines(), 1):
        for m in PLACEHOLDER_RE.finditer(line):
            rep.error(path, f"line {n}: unfilled placeholder {m.group(0)!r}")


def section_body(text: str, heading: str) -> str | None:
    """Text under a `## heading` (any level), up to the next same-or-higher heading."""
    lines = text.splitlines()
    start = None
    level = 0
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m and line[m.end():].strip() == heading:
            start = i + 1
            level = len(m.group(1))
            break
    if start is None:
        return None
    out = []
    for line in lines[start:]:
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) <= level:
            break
        out.append(line)
    return "\n".join(out)


def check_ids_and_pairing(path: Path, text: str, rep: Report) -> None:
    """FR/SC uniqueness and each FR carrying an SC (or a coverage exception)."""
    body = strip_html_comments(text)
    section = section_body(body, "Requirements & success criteria")
    if section is None:
        return  # contract.md without the section is handled elsewhere; nothing to pair

    coverage = section_body(body, "Known limitations & honest gaps") or ""
    cov_after = coverage.split("Coverage exceptions", 1)
    excepted = set(re.findall(r"FR-\d+", cov_after[1])) if len(cov_after) > 1 else set()

    fr_ids: dict[str, int] = {}
    sc_ids: dict[str, int] = {}
    fr_has_sc: dict[str, bool] = {}
    current_fr: str | None = None

    for line in section.splitlines():
        fm = FR_DEF_RE.match(line)
        if fm:
            fid = fm.group(1)
            fr_ids[fid] = fr_ids.get(fid, 0) + 1
            fr_has_sc.setdefault(fid, False)
            current_fr = fid
            continue
        sm = SC_DEF_RE.match(line)
        if sm:
            sid = sm.group(1)
            sc_ids[sid] = sc_ids.get(sid, 0) + 1
            if current_fr is not None:
                fr_has_sc[current_fr] = True

    for fid, count in fr_ids.items():
        if count > 1:
            rep.error(path, f"duplicate requirement id {fid} ({count} definitions)")
    for sid, count in sc_ids.items():
        if count > 1:
            rep.error(path, f"duplicate success-criterion id {sid} ({count} definitions)")

    for fid, has in fr_has_sc.items():
        if not has and fid not in excepted:
            rep.error(
                path,
                f"{fid} has no success criterion beneath it and no Coverage exceptions entry",
            )


def load_project(root: Path) -> tuple[Path | None, str | None, set[str]]:
    """Locate the project spec; return (path, id, defined INV ids)."""
    proj = root / "project" / "spec.md"
    if not proj.is_file():
        # search one level down for any kind: project
        for cand in root.glob("*/spec.md"):
            fm = parse_frontmatter(cand.read_text(encoding="utf-8"))
            if fm and fm.get("kind") == "project":
                proj = cand
                break
        else:
            return None, None, set()
    text = proj.read_text(encoding="utf-8")
    fm = parse_frontmatter(text) or {}
    invs = set(INV_DEF_RE.findall(strip_html_comments(text)))
    return proj, fm.get("id"), invs


def check_frontmatter(path: Path, fm: dict[str, str], rep: Report) -> str:
    for key in REQUIRED_FRONTMATTER:
        if not fm.get(key):
            rep.error(path, f"frontmatter missing required key {key!r}")
    kind = fm.get("kind", "")
    status = fm.get("status", "")
    if kind == "project":
        allowed = PROJECT_STATUS
    elif kind == "design":
        allowed = DESIGN_STATUS
    else:
        allowed = WORK_ITEM_STATUS
    if status and status not in allowed:
        rep.error(path, f"invalid status {status!r} for kind {kind!r} (allowed: {sorted(allowed)})")
    profile = fm.get("profile", "full")
    if profile not in PROFILES:
        rep.error(path, f"invalid profile {profile!r} (allowed: {sorted(PROFILES)})")
    if status in GATED_STATUS and not has_approver(fm.get("approved_by", "")):
        rep.warn(
            path,
            f"status {status!r} but no approved_by recorded; an approval gate has no owner "
            "(record who granted it, or regress the status)",
        )
    return kind


def lint_spec(path: Path, rep: Report, project_id: str | None, project_invs: set[str]) -> None:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        rep.error(path, "no YAML frontmatter block")
        return
    kind = check_frontmatter(path, fm, rep)

    slug_dir = path.parent
    detail = slug_dir / "detail"
    files = [path]
    if detail.is_dir():
        files += sorted(detail.glob("*.md"))

    for f in files:
        find_placeholders(f, f.read_text(encoding="utf-8"), rep)

    # The design.md (shaping's output) is a separately gated artifact. When it's
    # present with its own frontmatter, validate its keys, design status, and gate
    # record; placeholders and INV citations are already covered by the loops above.
    design = detail / "design.md"
    if design.is_file():
        dfm = parse_frontmatter(design.read_text(encoding="utf-8"))
        if dfm is not None:
            check_frontmatter(design, dfm, rep)

    if kind == "project":
        return

    # work-item checks
    if not fm.get("parent"):
        rep.warn(path, "work-item spec has no parent (fine only for a one-off with no project spec)")
    elif project_id is None:
        rep.error(path, f"parent {fm['parent']!r} set but no project spec found under the root")
    elif fm["parent"] != project_id:
        rep.error(path, f"parent {fm['parent']!r} does not resolve to the project spec id {project_id!r}")

    # A light-lane spec (frontmatter profile: light) is a single spec.md that
    # carries the FR/SC directly, with no detail/ split; a full spec keeps the
    # binding sections in detail/contract.md. Pair-check wherever they live.
    if fm.get("profile", "full") == "light":
        check_ids_and_pairing(path, text, rep)
    else:
        contract = detail / "contract.md"
        if contract.is_file():
            check_ids_and_pairing(contract, contract.read_text(encoding="utf-8"), rep)

    # dangling INV citations across all files of the spec
    for f in files:
        cited = set(INV_REF_RE.findall(strip_html_comments(f.read_text(encoding="utf-8"))))
        for inv in sorted(cited):
            if project_id is None:
                rep.warn(f, f"{inv} cited but no project spec to resolve it against")
            elif inv not in project_invs:
                rep.error(f, f"cites {inv}, which the project spec does not define")


def discover(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(root.glob("*/spec.md"))


def status_rollup(roots: list[Path]) -> int:
    """Tabulate every spec's kind/profile/status/gate across the roots. Never fails."""
    rows: list[tuple[str, str, str, str, str, str]] = []
    for root in roots:
        if not root.exists():
            print(f"{root}: path does not exist")
            continue
        for spec in discover(root):
            fm = parse_frontmatter(spec.read_text(encoding="utf-8")) or {}
            gate = fm.get("approved_by", "") or ""
            gate = gate.strip().strip("[]").strip() or "—"
            rows.append((
                str(spec.parent.name),
                fm.get("id", "?"),
                fm.get("kind", "?"),
                fm.get("profile", "full") if fm.get("kind") != "project" else "—",
                fm.get("status", "?"),
                gate,
            ))
    if not rows:
        print("spec-lint --status: no specs found")
        return 0
    headers = ("slug", "id", "kind", "profile", "status", "approved_by")
    widths = [max(len(h), *(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*("-" * w for w in widths)))
    for r in rows:
        print(fmt.format(*r))
    return 0


def main(argv: list[str]) -> int:
    args = argv[1:]
    if "--status" in args:
        roots = [Path(a) for a in args if a != "--status"] or [Path("docs/specs")]
        return status_rollup(roots)
    roots = [Path(a) for a in args] or [Path("docs/specs")]
    rep = Report()
    for root in roots:
        if not root.exists():
            rep.error(root, "path does not exist")
            continue
        base = root if root.is_dir() else root.parent
        project_path, project_id, project_invs = load_project(base)
        for spec in discover(root):
            lint_spec(spec, rep, project_id, project_invs)
    total = rep.errors + rep.warns
    if total == 0:
        print("spec-lint: clean")
    else:
        print(f"spec-lint: {rep.errors} error(s), {rep.warns} warning(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
