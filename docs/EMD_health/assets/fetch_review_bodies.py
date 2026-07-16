#!/usr/bin/env python3
"""Fetch review bodies for PRs with CHANGES_REQUESTED, create common mistakes guide."""

import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR / "pr_all_timeline_data.json"
DEFAULT_OUTPUT = SCRIPT_DIR / "common_mistakes_guide.json"
REPO = "WCRP-CMIP/Essential-Model-Documentation"


def run_gh(cmd):
    """Run gh command, return parsed JSON or None."""
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def get_reviews(pr_num):
    """Fetch reviews for PR, filter to CHANGES_REQUESTED with body."""
    data = run_gh(f"gh api /repos/{REPO}/pulls/{pr_num}/reviews")
    if not data or not isinstance(data, list):
        return []
    return [r for r in data 
            if r.get("state") == "CHANGES_REQUESTED" and r.get("body")
            and "[bot]" not in r.get("user", {}).get("login", "")]


def get_comments(pr_num):
    """Fetch issue comments for PR."""
    # Get comments one by one or use api list without paginate to avoid issues
    proc = subprocess.run(
        f'gh api /repos/{REPO}/issues/{pr_num}/comments -q ".[]"',
        capture_output=True, text=True, shell=True
    )
    if proc.returncode != 0:
        return []
    
    comments = []
    for line in proc.stdout.strip().split('\n'):
        if line.strip():
            try:
                c = json.loads(line)
                if isinstance(c, dict) and "[bot]" not in c.get("user", {}).get("login", "") and c.get("body"):
                    comments.append(c)
            except (json.JSONDecodeError, AttributeError):
                pass
    return comments


def classify_form_type(title):
    """Extract simplified form type."""
    for kw in ["Model_component", "Model_family", "Horizontal_grid_cell",
               "Horizontal_computational_grid", "Vertical_computational_grid", "Model"]:
        if kw in title:
            action = "New" if "New " in title else "Modify"
            return f"{action} {kw}"
    return "Other"


def extract_patterns(feedback_list):
    """Extract common mistake patterns from feedback text."""
    patterns = collections.defaultdict(int)
    
    keywords = {
        "Missing field": ["missing", "not specified", "empty", "required field", "null"],
        "Invalid value": ["invalid", "incorrect", "wrong", "bad", "malformed", "doesn't match"],
        "Naming/Convention": ["naming", "convention", "should be named", "name doesn't", "inconsistent name"],
        "Duplicate": ["duplicate", "already exists", "repeated", "already submitted"],
        "Grid mismatch": ["grid", "resolution", "doesn't match grid", "grid type", "vertical grid"],
        "Component reference": ["component", "reference", "not found", "undefined", "missing component"],
        "Configuration": ["config", "configuration", "attribute", "missing attribute", "incomplete"],
        "Metadata": ["metadata", "description", "source", "author", "reference"],
    }
    
    for feedback in feedback_list:
        text = feedback.lower()
        found = False
        for pattern, keywords_list in keywords.items():
            if any(kw in text for kw in keywords_list):
                patterns[pattern] += 1
                found = True
                break
        if not found:
            patterns["Other"] += 1
    
    return dict(sorted(patterns.items(), key=lambda x: -x[1]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        sys.exit(f"✗ Input file not found: {input_path}")

    print(f"Loading {input_path} ...", flush=True)
    with open(input_path) as f:
        data = json.load(f)

    # Find all PRs with CHANGES_REQUESTED
    cr_prs = {}
    for e in data["events"]:
        if e["type"] == "review" and e.get("detail", {}).get("state") == "CHANGES_REQUESTED":
            pr_num = e["pr"]
            if pr_num not in cr_prs:
                cr_prs[pr_num] = e["title"]

    print(f"Found {len(cr_prs)} PRs with CHANGES_REQUESTED", flush=True)

    if args.limit:
        cr_prs = dict(sorted(cr_prs.items())[:args.limit])
        print(f"Limited to {len(cr_prs)} for debug", flush=True)

    # Collect feedback by form type
    by_type = collections.defaultdict(lambda: {"feedback": [], "examples": []})

    for i, (pr_num, title) in enumerate(sorted(cr_prs.items()), 1):
        form_type = classify_form_type(title)
        print(f"  [{i}/{len(cr_prs)}] PR #{pr_num}: {form_type} ... ", end="", flush=True)

        reviews = get_reviews(pr_num)
        comments = get_comments(pr_num)
        
        feedback_count = len(reviews) + len(comments)
        print(f"{feedback_count} feedback items", flush=True)

        # Collect review bodies
        for r in reviews:
            by_type[form_type]["feedback"].append(r["body"])
            by_type[form_type]["examples"].append({
                "pr": pr_num,
                "type": "review",
                "reviewer": r.get("user", {}).get("login"),
                "excerpt": r["body"][:200],
            })

        # Collect comment bodies
        for c in comments:
            by_type[form_type]["feedback"].append(c["body"])
            by_type[form_type]["examples"].append({
                "pr": pr_num,
                "type": "comment",
                "author": c.get("user", {}).get("login"),
                "excerpt": c["body"][:200],
            })

    # Analyze patterns
    output = {
        "repository": REPO,
        "source": str(input_path),
        "total_prs_analyzed": len(cr_prs),
        "by_form_type": {},
    }

    for form_type in sorted(by_type.keys()):
        data_for_type = by_type[form_type]
        patterns = extract_patterns(data_for_type["feedback"])
        
        output["by_form_type"][form_type] = {
            "pr_count": len([x for x in cr_prs.values() if classify_form_type(x) == form_type]),
            "feedback_items": len(data_for_type["feedback"]),
            "common_mistakes": patterns,
            "example_feedback": data_for_type["examples"][:3],  # First 3 examples
        }

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Wrote {output_path}")
    print(f"\nSummary by form type:")
    for ft in sorted(output["by_form_type"].keys()):
        data = output["by_form_type"][ft]
        print(f"\n{ft} ({data['pr_count']} PRs, {data['feedback_items']} feedback items):")
        for mistake, count in data["common_mistakes"].items():
            print(f"  - {mistake}: {count}")


if __name__ == "__main__":
    main()
