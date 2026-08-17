"""
Turns data/pass2.json into the aggregate patterns that are the actual
point of the assignment. Writes data/patterns.json for the HTML build.
"""
import json
from collections import Counter, defaultdict


def analyze(path: str = "data/pass2.json"):
    records = list(json.load(open(path)).values())
    n = len(records)

    auth_counts = Counter()
    for r in records:
        for a in r.get("auth_methods", []):
            auth_counts[a] += 1

    access_counts = Counter(r.get("access_tier", "unknown") for r in records)
    buildability_counts = Counter(r.get("buildability", "blocked") for r in records)

    by_category = defaultdict(lambda: Counter())
    for r in records:
        by_category[r["category"]][r.get("access_tier", "unknown")] += 1

    category_selfserve_pct = {}
    for cat, counts in by_category.items():
        total = sum(counts.values())
        selfserve = counts.get("self-serve-free", 0) + counts.get("self-serve-trial", 0)
        category_selfserve_pct[cat] = round(selfserve / total * 100, 1) if total else 0

    blockers = Counter(r["blocker"] for r in records if r.get("blocker"))
    mcp_count = sum(1 for r in records if r.get("has_existing_mcp"))

    ready_today = [r["app"] for r in records if r.get("buildability") == "ready-today"]
    blocked = [r["app"] for r in records if r.get("buildability") == "blocked"]

    patterns = {
        "total_apps": n,
        "auth_method_distribution": dict(auth_counts.most_common()),
        "access_tier_distribution": dict(access_counts.most_common()),
        "buildability_distribution": dict(buildability_counts.most_common()),
        "category_selfserve_pct": dict(
            sorted(category_selfserve_pct.items(), key=lambda x: -x[1])
        ),
        "top_blockers": dict(blockers.most_common(8)),
        "apps_with_existing_mcp": mcp_count,
        "ready_today_apps": ready_today,
        "blocked_apps": blocked,
    }
    json.dump(patterns, open("data/patterns.json", "w"), indent=2)
    print(json.dumps(patterns, indent=2))
    return patterns


if __name__ == "__main__":
    analyze()
