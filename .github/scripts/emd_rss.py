
REPO_DEFAULT = "WCRP-CMIP/Essential-Model-Documentation"
FEED_URL     = "https://wcrp-cmip.github.io/Essential-Model-Documentation/emd_rss.xml"

STAMP_RE    = re.compile(r"^\s*\|\s*([^|]+?)\s*\|")
CATEGORY_LABELS = {
    "horizontal_grid_cell",
    "horizontal_computational_grid",
    "vertical_computational_grid",
    "model_family",
    "model_component",
    "component_config",
    "link_existing_component",
    "model",
}

CATEGORY_COLORS = {
    "horizontal_grid_cell":          "#2980b9",
    "horizontal_computational_grid": "#3498db",
    "vertical_computational_grid":   "#16a085",
    "model_family":                  "#f39c12",
    "model_component":               "#d35400",
    "component_config":              "#1abc9c",
    "link_existing_component":       "#1abc9c",
    "model":                         "#e67e22",
}


# =============================================================================
# GitHub API
# =============================================================================

def gh(*args):
    result = os.popen(f"gh {' '.join(args)}").read().strip()
    return result or None


def fetch_closed_issues(repo, since=None):
    """Fetch all closed emd-submission issues, paginated."""
    all_issues = []
    page = 1
    while True:
        cmd = (
            f"api repos/{repo}/issues "
            f"--method GET "
            f"-f state=closed "
            f"-f labels=emd-submission "
            f"-f per_page=100 "
            f"-f page={page}"
        )
        raw = gh(cmd)
        if not raw:
            break
        batch = json.loads(raw)
        batch = [i for i in batch if "pull_request" not in i]
        if not batch:
            break
        if since:
            batch = [i for i in batch if i.get("closed_at", "") >= since]
        all_issues.extend(batch)
        print(f"  page {page}: {len(batch)} issues (total: {len(all_issues)})")
        if len(batch) < 100:
            break
        page += 1
    return all_issues


# =============================================================================
# Parsing
# =============================================================================

def extract_stamp(title):
    """Return the pipe-stamped ID, or None."""
    m = STAMP_RE.match(title)
    return m.group(1).strip() if m else None


def extract_category(labels):
    """Return the first matching category label, or 'unknown'."""
    for lbl in labels:
        name = lbl["name"] if isinstance(lbl, dict) else lbl
        if name in CATEGORY_LABELS:
            return name
    return "unknown"


def extract_submitter(issue):
    """Return the GitHub login of the issue author."""
    user = issue.get("user") or {}
    return user.get("login", "unknown")


def parse_closed_at(issue):
    """Return a datetime from closed_at, or None."""
    raw = issue.get("closed_at")
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None


# =============================================================================
# RSS
# =============================================================================

def escape_html(text):
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def format_rss_date(dt):
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


def build_rss(items, repo, feed_url):
    repo_url = f"https://github.com/{repo}"

    rss = Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    rss.set("xmlns:dc",   "http://purl.org/dc/elements/1.1/")

    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text       = "EMD Submissions"
    SubElement(channel, "link").text        = repo_url
    SubElement(channel, "description").text = "Merged Essential Model Documentation submissions"
    SubElement(channel, "language").text    = "en-us"
    SubElement(channel, "lastBuildDate").text = format_rss_date(datetime.utcnow())

    atom_link = SubElement(channel, "atom:link")
    atom_link.set("href", feed_url)
    atom_link.set("rel",  "self")
    atom_link.set("type", "application/rss+xml")

    for entry in sorted(items, key=lambda x: x["closed_at"], reverse=True):
        item = SubElement(channel, "item")

        stamp     = entry["stamp"]
        category  = entry["category"]
        submitter = entry["submitter"]
        issue_url = entry["url"]
        closed_at = entry["closed_at"]
        number    = entry["number"]
        color     = CATEGORY_COLORS.get(category, "#666666")

        SubElement(item, "title").text   = f"[{category}] {stamp}"
        SubElement(item, "link").text    = issue_url
        SubElement(item, "guid").text    = issue_url
        SubElement(item, "pubDate").text = format_rss_date(closed_at)
        SubElement(item, "dc:creator").text = submitter
        SubElement(item, "category").text   = category

        avatar_url  = f"https://github.com/{submitter}.png?size=32"
        profile_url = f"https://github.com/{submitter}"

        desc = (
            f'<div style="font-family:system-ui,sans-serif;">'
            f'<p><span style="display:inline-block;padding:2px 8px;border-radius:4px;'
            f'background:{color};color:white;font-size:0.8em;">{escape_html(category)}</span></p>'
            f'<p style="font-size:1.1em;font-weight:600;">{escape_html(stamp)}</p>'
            f'<p>'
            f'<a href="{profile_url}" target="_blank">'
            f'<img src="{avatar_url}" width="20" height="20" '
            f'style="border-radius:50%;vertical-align:middle;margin-right:6px;" />'
            f'{escape_html(submitter)}'
            f'</a>'
            f'</p>'
            f'<p><a href="{issue_url}">View issue #{number} on GitHub →</a></p>'
            f'</div>'
        )
        SubElement(item, "description").text = desc

    xml_str = tostring(rss, encoding="unicode")
    return minidom.parseString(xml_str).toprettyxml(indent="  ")


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo",   default=REPO_DEFAULT)
    parser.add_argument("--output", default="emd_rss.xml")
    parser.add_argument("--since",  default=None,
                        help="Only include issues closed after this date (YYYY-MM-DD)")
    args = parser.parse_args()

    since = args.since + "T00:00:00Z" if args.since else None

    print(f"Fetching closed emd-submission issues from {args.repo}...")
    issues = fetch_closed_issues(args.repo, since=since)
    print(f"  {len(issues)} total closed issues fetched.")

    entries = []
    for issue in issues:
        stamp = extract_stamp(issue["title"])
        if not stamp or stamp.lower() == "skip":
            continue

        closed_at = parse_closed_at(issue)
        if not closed_at:
            continue

        entries.append({
            "number":    issue["number"],
            "stamp":     stamp,
            "category":  extract_category(issue.get("labels", [])),
            "submitter": extract_submitter(issue),
            "closed_at": closed_at,
            "url":       issue["html_url"],
        })

    print(f"  {len(entries)} stamped merged entries found.")

    rss = build_rss(entries, args.repo, FEED_URL)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rss, encoding="utf-8")
    print(f"  RSS written to {out}  ({len(entries)} items)")


if __name__ == "__main__":
    main()
