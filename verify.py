"""
Human-in-the-loop verification. Run in two steps:

  python verify.py sample        -> prints a random sample of N apps with
                                      their pass1 AND pass2 records side by
                                      side, plus the evidence URL, for you
                                      to manually check against real docs.

  python verify.py score         -> after you've hand-edited
                                      data/human_checks.json (see format
                                      below), computes pass1 vs pass2 vs
                                      human accuracy and writes
                                      data/verification_report.json,
                                      which the HTML page reads directly.

human_checks.json format (you fill this in by hand after checking docs):
{
  "Slack": {"pass1_correct": false, "pass2_correct": true, "wrong_fields_pass1": ["access_tier"], "wrong_fields_pass2": [], "notes": "..."},
  ...
}
"""
import json
import random
import sys
from collections import Counter

FIELDS_TO_CHECK = ["auth_methods", "access_tier", "api_type", "buildability"]


def sample(n: int = 20, seed: int = 42):
    pass1 = json.load(open("data/pass1.json"))
    pass2 = json.load(open("data/pass2.json"))
    random.seed(seed)
    apps = random.sample(list(pass1.keys()), min(n, len(pass1)))

    template = {}
    for app in apps:
        p1, p2 = pass1[app], pass2.get(app, {})
        print(f"\n{'='*70}\n{app}")
        print(f"  evidence_url: {p2.get('evidence_url', p1.get('evidence_url'))}")
        for f in FIELDS_TO_CHECK:
            print(f"  {f:15s} pass1={p1.get(f)!r:40s} pass2={p2.get(f)!r}")
        if p2.get("corrected_fields"):
            print(f"  corrected:    {p2['corrected_fields']}")
        template[app] = {
            "pass1_correct": None,
            "pass2_correct": None,
            "wrong_fields_pass1": [],
            "wrong_fields_pass2": [],
            "notes": ""
        }

    with open("data/human_checks_TEMPLATE.json", "w") as f:
        json.dump(template, f, indent=2)
    print(f"\n\nSample of {len(apps)} written to data/human_checks_TEMPLATE.json")
    print("Manually check each against real docs, fill in true/false, save as data/human_checks.json")


def score():
    checks = json.load(open("data/human_checks.json"))
    n = len(checks)
    p1_correct = sum(1 for v in checks.values() if v["pass1_correct"])
    p2_correct = sum(1 for v in checks.values() if v["pass2_correct"])

    # Field-level accuracy breakdown
    p1_wrong_fields = Counter()
    p2_wrong_fields = Counter()
    for v in checks.values():
        for f in v.get("wrong_fields_pass1", []):
            p1_wrong_fields[f] += 1
        for f in v.get("wrong_fields_pass2", []):
            p2_wrong_fields[f] += 1

    field_accuracy = {}
    for f in FIELDS_TO_CHECK:
        p1_acc = round((n - p1_wrong_fields.get(f, 0)) / n * 100, 1) if n else 0
        p2_acc = round((n - p2_wrong_fields.get(f, 0)) / n * 100, 1) if n else 0
        field_accuracy[f] = {"pass1_pct": p1_acc, "pass2_pct": p2_acc}

    report = {
        "sample_size": n,
        "pass1_accuracy": round(p1_correct / n, 3) if n else 0,
        "pass2_accuracy": round(p2_correct / n, 3) if n else 0,
        "improvement_pts": round((p2_correct - p1_correct) / n * 100, 1) if n else 0,
        "field_level_accuracy": field_accuracy,
        "pass1_wrong_field_counts": dict(p1_wrong_fields.most_common()),
        "pass2_wrong_field_counts": dict(p2_wrong_fields.most_common()),
        "per_app": checks,
    }
    with open("data/verification_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps({k: v for k, v in report.items() if k != "per_app"}, indent=2))
    print("\nWritten to data/verification_report.json")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sample"
    if cmd == "sample":
        sample()
    elif cmd == "score":
        score()
    else:
        print("usage: python verify.py [sample|score]")
