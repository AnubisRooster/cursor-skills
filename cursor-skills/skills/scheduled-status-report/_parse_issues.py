#!/usr/bin/env python3
"""Parse Models weekly-status Jira pages into structured stats."""
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

PAGE1 = Path(r"C:\Users\mfink\.cursor\projects\C-Users-mfink-claude-skills-scheduled-status-report\agent-tools\5f1abeeb-a085-4572-8352-2baed5dbbc49.txt")
PAGE2 = Path(r"C:\Users\mfink\.cursor\projects\C-Users-mfink-claude-skills-scheduled-status-report\agent-tools\a93365f2-e9f0-4fc6-a348-9034064e2059.txt")
PAGE3 = Path(r"C:\Users\mfink\.claude\skills\scheduled-status-report\_page3.json")
OUT = Path(r"C:\Users\mfink\.claude\skills\scheduled-status-report\_stats.json")


def parse_created(s):
    if not s:
        return None
    for fmt in (
        "%Y-%m-%d %H:%M:%S Eastern Daylight Time",
        "%Y-%m-%d %H:%M:%S Eastern Standard Time",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
    ):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def parse_res(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def load_issues():
    issues = []
    for p in (PAGE1, PAGE2, PAGE3):
        data = json.loads(p.read_text(encoding="utf-8"))
        issues.extend(data["issues"])
    return issues


def normalize(issue):
    epic_raw = issue.get("customfield_10006")
    epic = None
    if isinstance(epic_raw, dict):
        epic = epic_raw.get("value")
        if epic in (None, "", "(This issue is an Epic)"):
            epic = None
    elif isinstance(epic_raw, str) and epic_raw not in ("", "(This issue is an Epic)"):
        epic = epic_raw
    assignee = issue.get("assignee") or {}
    name = assignee.get("display_name") or "Unassigned"
    itype = (issue.get("issue_type") or {}).get("name") or "Unknown"
    created = parse_created(issue.get("created"))
    resolved = parse_res(issue.get("resolutiondate"))
    cycle = None
    if created and resolved:
        # drop tz for created (naive EDT) vs aware res — compare dates only
        c = created.replace(tzinfo=None) if created.tzinfo is None else created.replace(tzinfo=None)
        r = resolved.replace(tzinfo=None)
        cycle = max(0.0, (r - c).total_seconds() / 86400.0)
    return {
        "key": issue["key"],
        "summary": issue.get("summary", ""),
        "assignee": name,
        "type": itype,
        "epic": epic,
        "created": issue.get("created"),
        "resolutiondate": issue.get("resolutiondate"),
        "cycle_days": cycle,
    }


def main():
    raw = load_issues()
    issues = [normalize(i) for i in raw]
    assert len(issues) == 143, f"expected 143, got {len(issues)}"

    epics = sorted({i["epic"] for i in issues if i["epic"]})
    by_type = Counter(i["type"] for i in issues)
    by_epic = Counter(i["epic"] or "No Epic linked" for i in issues)
    by_assignee = Counter(i["assignee"] for i in issues)
    cycles = [i["cycle_days"] for i in issues if i["cycle_days"] is not None]
    cycles_sorted = sorted(cycles)

    grouped = defaultdict(list)
    for i in issues:
        grouped[i["assignee"]].append(i)

    by_epic_detail = defaultdict(list)
    for i in issues:
        by_epic_detail[i["epic"] or "No Epic linked"].append(i)

    out = {
        "count": len(issues),
        "unique_epics": epics,
        "by_type": by_type.most_common(),
        "by_epic": by_epic.most_common(),
        "by_assignee": by_assignee.most_common(),
        "assignee_count_named": sum(1 for a in by_assignee if a != "Unassigned"),
        "unassigned": by_assignee.get("Unassigned", 0),
        "cycle": {
            "n": len(cycles),
            "median": statistics.median(cycles) if cycles else None,
            "mean": statistics.mean(cycles) if cycles else None,
            "min": min(cycles) if cycles else None,
            "max": max(cycles) if cycles else None,
            "p90": cycles_sorted[int(0.9 * (len(cycles_sorted) - 1))] if cycles_sorted else None,
            "outliers_gt_30": [
                {"key": i["key"], "days": round(i["cycle_days"], 1), "summary": i["summary"], "assignee": i["assignee"]}
                for i in issues
                if i["cycle_days"] is not None and i["cycle_days"] > 30
            ],
            "missing_resolutiondate": [i["key"] for i in issues if i["cycle_days"] is None],
        },
        "issues": issues,
        "by_assignee_issues": {k: v for k, v in grouped.items()},
        "by_epic_issues": {k: v for k, v in by_epic_detail.items()},
    }
    OUT.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print("count", out["count"])
    print("unique_epics", len(epics), epics)
    print("by_type", out["by_type"])
    print("by_epic", out["by_epic"])
    print("by_assignee", out["by_assignee"])
    print("cycle", {k: out["cycle"][k] for k in ("n", "median", "mean", "min", "max", "p90")})
    print("outliers", out["cycle"]["outliers_gt_30"])
    print("missing_res", out["cycle"]["missing_resolutiondate"])
    print("named_assignees", out["assignee_count_named"], "unassigned", out["unassigned"])


if __name__ == "__main__":
    main()
