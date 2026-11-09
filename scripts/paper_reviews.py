"""Validate and render original, source-located paper reading notes."""

import json
from collections import Counter
from pathlib import Path

from catalog import public_url_error


STATUSES = {"full-text-reviewed", "partial", "unavailable"}
SECTIONS = {
    "problem": "Research question",
    "method": "Method",
    "evaluation": "Evaluation",
    "findings": "What the results support",
    "limitations": "Limits and qualifications",
    "relevance": "Relevance to reliable Text-to-SQL",
}


def load_reviews(root):
    path = root / "data" / "paper-reviews.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def validate_reviews(reviews, papers, updated):
    from datetime import date

    errors = []
    if not isinstance(reviews, list):
        return ["paper-reviews: expected a list"]
    by_id = {p["id"]: p for p in papers}
    seen = set()
    for index, review in enumerate(reviews):
        label = f"paper-reviews[{index}]"
        if not isinstance(review, dict):
            errors.append(f"{label}: expected an object")
            continue
        allowed = {"paper_id", "status", "reviewed_on", "source_url", "additional_sources",
                   "version", "coverage", "unread", "claims", *SECTIONS}
        if set(review) - allowed:
            errors.append(f"{label}: unexpected fields in public reading record")
        pid = review.get("paper_id")
        if not isinstance(pid, str):
            errors.append(f"{label}: paper_id must be text")
            continue
        if pid not in by_id or pid in seen:
            errors.append(f"{label}: unknown or duplicate paper_id")
        seen.add(pid)
        status = review.get("status")
        if status not in STATUSES:
            errors.append(f"{label}: invalid reading status")
        for field in ("version", "coverage", *SECTIONS):
            if not isinstance(review.get(field), str) or not review[field].strip():
                errors.append(f"{label}.{field}: required nonempty text")
        if public_url_error(review.get("source_url")):
            errors.append(f"{label}.source_url: invalid public source")
        extra = review.get("additional_sources", [])
        if not isinstance(extra, list) or any(
            not isinstance(source, dict)
            or set(source) != {"label", "url"}
            or not isinstance(source.get("label"), str)
            or not source["label"].strip()
            or public_url_error(source.get("url"))
            for source in extra
        ):
            errors.append(f"{label}.additional_sources: expected labeled public sources")
        try:
            checked = date.fromisoformat(review.get("reviewed_on", ""))
            if checked > date.fromisoformat(updated):
                errors.append(f"{label}.reviewed_on: later than collection update")
        except (ValueError, TypeError):
            errors.append(f"{label}.reviewed_on: required ISO date")
        unread = review.get("unread")
        if not isinstance(unread, list) or any(not isinstance(x, str) or not x.strip() for x in unread):
            errors.append(f"{label}.unread: expected a list of text")
        elif status == "full-text-reviewed" and unread:
            errors.append(f"{label}: completed reading cannot have unread material")
        elif status != "full-text-reviewed" and not unread:
            errors.append(f"{label}: incomplete reading must identify missing material")
        claims = review.get("claims")
        if not isinstance(claims, list) or (status == "full-text-reviewed" and not claims):
            errors.append(f"{label}.claims: completed reading needs located claim checks")
        else:
            for n, claim in enumerate(claims):
                if not isinstance(claim, dict) or any(
                    not isinstance(claim.get(k), str) or not claim[k].strip()
                    for k in ("claim", "evidence", "locator", "disposition")
                ):
                    errors.append(f"{label}.claims[{n}]: incomplete claim check")
        if pid in by_id and status == "full-text-reviewed" and by_id[pid]["source_depth"] != status:
            errors.append(f"{label}: full reading must match catalog source_depth")
    for paper in papers:
        if paper["source_depth"] == "full-text-reviewed" and not any(
            r.get("paper_id") == paper["id"] and r.get("status") == "full-text-reviewed"
            for r in reviews if isinstance(r, dict)
        ):
            errors.append(f"{paper['id']}: full-text-reviewed needs a completed reading record")
    return errors


def render_reviews(root, papers):
    reviews = load_reviews(root)
    if not reviews:
        return {}
    from render import NOTICE, cell_link, cell_text, table

    by_id = {p["id"]: p for p in papers}
    counts = Counter(r["status"] for r in reviews)
    labels = {"full-text-reviewed": "Full paper read", "partial": "Partial reading", "unavailable": "Full text unavailable"}
    lines = [NOTICE, "# Paper reading notes", "",
             "[Overview](../README.md) · [Paper tables](README.md) · [By year](by-year.md)", "",
             "Source-located reading notes and explicit full-text access gaps. Completed notes cover "
             "the paper body, methods, results and available appendices. "
             "These readings are not independent reproductions or guarantees that a paper's claims are correct.", "",
             f"Coverage: **{counts['full-text-reviewed']} full-paper readings**, "
             f"**{counts['partial']} partial readings**, **{counts['unavailable']} unavailable full texts**, "
             f"and **{len(papers) - len(reviews)} papers awaiting this audit**.", "",
             "Each note identifies the exact version, material read, remaining access gaps and source locations. "
             "Missing access is not evidence that a scientific claim is false.", ""]
    rows, result = [], {}
    for review in sorted(reviews, key=lambda r: (-by_id[r['paper_id']]['year'], by_id[r['paper_id']]['title'].casefold())):
        pid = review["paper_id"]
        paper = by_id[pid]
        rows.append("| " + " | ".join([str(paper["year"]), cell_link(paper["title"], f"notes/{pid}.md"), labels[review["status"]]]) + " |")
        note = [NOTICE, f"# {paper['title']}", "",
                "[All reading notes](../reading-notes.md) · " + cell_link("Catalog entry", f"../README.md#{pid}"), "",
                f"**{labels[review['status']]} · {review['reviewed_on']}**", "",
                cell_link("Original source", review["source_url"]) + " · " + review["version"], "",
                "**Reading coverage:** " + review["coverage"], ""]
        if review.get("additional_sources"):
            note += ["**Additional inspected sources:** " + " · ".join(
                cell_link(source["label"], source["url"]) for source in review["additional_sources"]
            ), ""]
        if review["unread"]:
            note += ["**Unread or unavailable material:**", "", *[f"- {x}" for x in review["unread"]], ""]
        for key, heading in SECTIONS.items():
            note += [f"## {heading}", "", review[key], ""]
        if review["claims"]:
            note += ["## Checks against the paper", "",
                     "These are interpretations checked against the source, not verbatim quotations attributed to its authors.", ""]
            checks = ["| " + " | ".join(cell_text(claim[k]) for k in ("claim", "evidence", "locator", "disposition")) + " |" for claim in review["claims"]]
            note += [table(["Claim or inference examined", "Original evidence", "Location", "Assessment"], checks), ""]
        note += ["Reading and source inspection do not establish independent reproduction. Artifact availability is recorded separately in the catalog.", ""]
        result[Path("papers") / "notes" / f"{pid}.md"] = "\n".join(note)
    lines += [table(["Year", "Paper", "Reading coverage"], rows), ""]
    result[Path("papers/reading-notes.md")] = "\n".join(lines)
    return result
