#!/usr/bin/env python3
import json
from pathlib import Path

d = json.loads(Path("_stats.json").read_text(encoding="utf-8"))
out = []
out.append(f"CYCLE n={d['cycle']['n']} median={d['cycle']['median']:.1f} mean={d['cycle']['mean']:.1f} min={d['cycle']['min']:.1f} max={d['cycle']['max']:.1f} p90={d['cycle']['p90']:.1f}")
out.append(f"OUTLIERS>{30}: {len(d['cycle']['outliers_gt_30'])} MISSING_RES={len(d['cycle']['missing_resolutiondate'])}")
out.append("===EPICS===")
for epic, issues in sorted(d["by_epic_issues"].items(), key=lambda kv: -len(kv[1])):
    out.append(f"## {epic} ({len(issues)})")
    for i in issues:
        out.append(f"  {i['key']}|{i['type']}|{i['assignee']}|{i['summary']}")
out.append("===ASSIGNEES===")
for name, issues in sorted(d["by_assignee_issues"].items()):
    out.append(f"## {name} ({len(issues)})")
    for i in issues:
        out.append(f"  {i['key']}|{i['type']}|{i['epic'] or 'NONE'}|{i['summary']}")
Path("_narratives.txt").write_text("\n".join(out), encoding="utf-8")
print("wrote _narratives.txt", len(out), "lines")
