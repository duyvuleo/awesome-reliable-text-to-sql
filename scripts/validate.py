#!/usr/bin/env python3
"""Validate catalog records, public-content hygiene, and local Markdown links."""

from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from catalog import (BENCHMARK_COVERAGE, BENCHMARK_FIELDS, CLARIFICATION_MODES,
                     DATA_ACCESS, INTERACTION_MODES, CATEGORIES, ROOT, canonical_url,
                     load_benchmarks, load_catalog, public_url_error)


URL_RE = re.compile(r"https?://[^\s<>\"'\])}]+")
LOCAL_PATH_RE = re.compile(r"(?:/(?:Users|home|private|tmp|var/folders)/[^\s]+|" + "file" + r":/+[^\s]+|[A-Za-z]:\\(?:Users|Windows)\\)")
LINK_RE = re.compile(r"!?\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\)")
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", ".pytest_cache"}
TEXT_SUFFIXES = {".md", ".json", ".py", ".yml", ".yaml", ".txt", ".cff", ".toml", ".sh"}


def iso_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def validate_data(papers, resources, meta):
    errors = []
    if not isinstance(meta, dict):
        return ["meta: must be an object"]
    for name in ("updated", "search_cutoff", "owner", "repo", "title"):
        if not isinstance(meta.get(name), str) or not meta[name].strip():
            errors.append(f"meta.{name}: required nonempty string")
    updated = iso_date(meta.get("updated"))
    cutoff = iso_date(meta.get("search_cutoff"))
    if not updated:
        errors.append("meta.updated: required ISO date")
    if not cutoff:
        errors.append("meta.search_cutoff: required ISO date")
    if updated and cutoff and cutoff > updated:
        errors.append("meta.search_cutoff: later than meta.updated")
    if not isinstance(papers, list) or not isinstance(resources, list):
        return errors + ["papers and resources must be lists"]
    seen_ids = set()
    paper_ids = set()
    seen_titles = set()
    seen_urls = set()

    def check_string(item, field, label):
        if not isinstance(item.get(field), str) or not item[field].strip():
            errors.append(f"{label}.{field}: required nonempty string")

    def check_list(item, field, label, nonempty=True):
        value = item.get(field)
        if not isinstance(value, list) or (nonempty and not value) or any(not isinstance(entry, str) or not entry.strip() for entry in value):
            errors.append(f"{label}.{field}: required {'nonempty ' if nonempty else ''}string list")
            return []
        if len(value) != len(set(value)):
            errors.append(f"{label}.{field}: duplicate values")
        return value

    def check_url(value, label):
        problem = public_url_error(value)
        if problem:
            errors.append(f"{label}: {problem}")
            return False
        return True

    def check_common(item, label):
        identifier = item.get("id")
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier):
            errors.append(f"{label}.id: expected stable lowercase slug")
        elif identifier in seen_ids:
            errors.append(f"{label}.id: duplicate ID {identifier}")
        else:
            seen_ids.add(identifier)
        checked = iso_date(item.get("checked_on"))
        if not checked:
            errors.append(f"{label}.checked_on: required ISO date")
        elif updated and checked > updated:
            errors.append(f"{label}.checked_on: later than meta.updated")
        for index, value in enumerate(check_list(item, "evidence", label)):
            check_url(value, f"{label}.evidence[{index}]")

    for index, item in enumerate(papers):
        label = f"papers[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}: must be an object")
            continue
        check_common(item, label)
        added = iso_date(item.get("added_on"))
        checked = iso_date(item.get("checked_on"))
        if not added:
            errors.append(f"{label}.added_on: required ISO date")
        elif updated and added > updated:
            errors.append(f"{label}.added_on: later than meta.updated")
        elif checked and added > checked:
            errors.append(f"{label}.added_on: later than checked_on")
        if isinstance(item.get("id"), str):
            paper_ids.add(item["id"])
        for field in ("title", "publication_status", "summary", "source_depth"):
            check_string(item, field, label)
        title = item.get("title")
        if isinstance(title, str):
            normalized = re.sub(r"\W+", "", title.casefold())
            if normalized in seen_titles:
                errors.append(f"{label}.title: duplicate title")
            seen_titles.add(normalized)
        year = item.get("year")
        if isinstance(year, bool) or not isinstance(year, int) or year < 1900 or (updated and year > updated.year):
            errors.append(f"{label}.year: expected plausible year no later than meta.updated")
        if not isinstance(item.get("category"), str) or item["category"] not in CATEGORIES:
            errors.append(f"{label}.category: unsupported category")
        if item.get("scope") not in ("core", "adjacent"):
            errors.append(f"{label}.scope: expected core or adjacent")
        if item.get("source_depth") not in ("primary-record", "targeted-full-text"):
            errors.append(f"{label}.source_depth: unsupported evidence depth")
        check_list(item, "topics", label)
        url = item.get("primary_url")
        if check_url(url, f"{label}.primary_url"):
            normalized = canonical_url(url)
            if normalized in seen_urls:
                errors.append(f"{label}.primary_url: duplicate canonical URL")
            seen_urls.add(normalized)
        for field in ("code_url", "dataset_url"):
            if field not in item:
                errors.append(f"{label}.{field}: required URL or null")
            elif item[field] is not None:
                check_url(item[field], f"{label}.{field}")
        if "artifact_status" in item:
            check_string(item, "artifact_status", label)

    resource_names = set()
    resource_urls = set()
    for index, item in enumerate(resources):
        label = f"resources[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}: must be an object")
            continue
        check_common(item, label)
        for field in ("name", "description", "protocol", "availability", "license_note"):
            check_string(item, field, label)
        kind = item.get("kind")
        if kind not in ("system", "tool", "dataset"):
            errors.append(f"{label}.kind: unsupported kind")
            kind = "invalid"
        if isinstance(item.get("name"), str):
            key = (kind, re.sub(r"\W+", "", item["name"].casefold()))
            if key in resource_names:
                errors.append(f"{label}.name: duplicate name within resource kind")
            resource_names.add(key)
        for identifier in check_list(item, "paper_ids", label, nonempty=False):
            if identifier not in paper_ids:
                errors.append(f"{label}.paper_ids: unknown paper ID {identifier}")
        if check_url(item.get("url"), f"{label}.url"):
            key = (kind, canonical_url(item["url"]))
            if key in resource_urls:
                errors.append(f"{label}.url: duplicate canonical URL within resource kind")
            resource_urls.add(key)
    return errors


def validate_benchmarks(benchmarks, resources, meta):
    """Check complete dataset coverage, explicit unknowns, and field-level provenance."""
    if not isinstance(benchmarks, list):
        return ["benchmarks: must be a list"]
    datasets = {item["id"] for item in resources if isinstance(item, dict)
                and item.get("kind") == "dataset" and isinstance(item.get("id"), str)}
    seen = set()
    labels = set()
    errors = []
    updated = iso_date(meta.get("updated"))
    for index, item in enumerate(benchmarks):
        label = f"benchmarks[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}: must be an object")
            continue
        identifier = item.get("resource_id")
        if not isinstance(identifier, str) or identifier not in datasets:
            errors.append(f"{label}.resource_id: must reference a dataset resource")
        elif identifier in seen:
            errors.append(f"{label}.resource_id: duplicate benchmark resource")
        else:
            seen.add(identifier)
        for field in ("label", "domain", "evaluation"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{label}.{field}: required nonempty string")
        if isinstance(item.get("label"), str):
            normalized = item["label"].casefold().strip()
            if normalized in labels:
                errors.append(f"{label}.label: duplicate benchmark label")
            labels.add(normalized)
        if not isinstance(item.get("relevance"), str) or item["relevance"] not in {"direct", "adjacent"}:
            errors.append(f"{label}.relevance: expected direct or adjacent")
        for field, status_key, choices in (("ambiguity", "status", BENCHMARK_COVERAGE),
                                            ("unanswerability", "status", BENCHMARK_COVERAGE),
                                            ("clarification", "mode", CLARIFICATION_MODES),
                                            ("interaction", "mode", INTERACTION_MODES)):
            value = item.get(field)
            if not isinstance(value, dict):
                errors.append(f"{label}.{field}: required status and detail object")
                continue
            if not isinstance(value.get(status_key), str) or value[status_key] not in choices:
                errors.append(f"{label}.{field}.{status_key}: unsupported value; record unknowns explicitly")
            if not isinstance(value.get("detail"), str) or not value["detail"].strip():
                errors.append(f"{label}.{field}.detail: required nonempty string")
        if not isinstance(item.get("data_access"), str) or item["data_access"] not in DATA_ACCESS:
            errors.append(f"{label}.data_access: unsupported access state")
        checked = iso_date(item.get("checked_on"))
        if not checked:
            errors.append(f"{label}.checked_on: required ISO date")
        elif updated and checked > updated:
            errors.append(f"{label}.checked_on: later than meta.updated")
        evidence = item.get("evidence")
        supported = set()
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{label}.evidence: required nonempty evidence list")
            evidence = []
        for source_index, source in enumerate(evidence):
            location = f"{label}.evidence[{source_index}]"
            if not isinstance(source, dict):
                errors.append(f"{location}: must be an object")
                continue
            problem = public_url_error(source.get("url"))
            if problem:
                errors.append(f"{location}.url: {problem}")
            if not isinstance(source.get("locator"), str) or not source["locator"].strip():
                errors.append(f"{location}.locator: required inspected section or artifact locator")
            fields = source.get("supports")
            if not isinstance(fields, list) or not fields or any(not isinstance(field, str) or field not in BENCHMARK_FIELDS for field in fields):
                errors.append(f"{location}.supports: required list of comparison fields")
            else:
                supported.update(fields)
        missing = BENCHMARK_FIELDS - supported
        if missing:
            errors.append(f"{label}.evidence: missing field provenance for " + ", ".join(sorted(missing)))
    if datasets - seen:
        errors.append("benchmarks: missing dataset resources: " + ", ".join(sorted(datasets - seen)))
    return errors


def text_files(root):
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts) or not path.is_file():
            continue
        if path.is_symlink():
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"LICENSE", ".gitignore"}:
            yield path


def public_content_errors(text, label):
    errors = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if LOCAL_PATH_RE.search(line):
            errors.append(f"{label}:{line_number}: local filesystem path is not public catalog content")
        for match in URL_RE.finditer(line):
            value = match.group().rstrip(".,;")
            problem = public_url_error(value)
            if problem:
                errors.append(f"{label}:{line_number}: URL {problem}")
    return errors


def anchors(text):
    found = set(re.findall(r'<a\s+(?:id|name)=[\"\']([^\"\']+)[\"\']', text))
    occurrences = {}
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            title = re.sub(r"!?\[([^\]]+)\]\([^)]+\)", r"\1", match.group(1))
            title = re.sub(r"<[^>]+>", "", title)
            slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
            count = occurrences.get(slug, 0)
            occurrences[slug] = count + 1
            found.add(slug if count == 0 else f"{slug}-{count}")
    return found


def markdown_link_errors(root, path, text):
    errors = []
    label = str(path.relative_to(root))
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or "{{" in target:
            if parsed.scheme and parsed.scheme not in {"https", "http", "mailto"}:
                errors.append(f"{label}: unsupported or local link scheme")
            continue
        if parsed.path.startswith("/"):
            errors.append(f"{label}: absolute local link is forbidden")
            continue
        destination = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path.resolve()
        try:
            destination.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{label}: relative link escapes the repository")
            continue
        if not destination.exists():
            errors.append(f"{label}: missing relative link target {target}")
        elif parsed.fragment and destination.is_file() and destination.suffix.lower() == ".md":
            if unquote(parsed.fragment) not in anchors(destination.read_text(encoding="utf-8")):
                errors.append(f"{label}: missing local anchor {target}")
    return errors


def validate_repository(root=ROOT):
    try:
        papers, resources, meta = load_catalog(root)
        errors = validate_data(papers, resources, meta)
        if isinstance(resources, list) and isinstance(meta, dict):
            errors.extend(validate_benchmarks(load_benchmarks(root), resources, meta))
    except (OSError, ValueError, TypeError) as error:
        return [f"Cannot read catalog: {error}"]
    for path in text_files(root):
        label = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8")
        errors.extend(public_content_errors(text, label))
        if path.suffix == ".md":
            if path.name == "README.template.md":
                link_base = root / "README.md"
            elif path.name.endswith(".template.md"):
                link_base = path.with_name(path.name.replace(".template.md", ".md"))
            else:
                link_base = path
            errors.extend(markdown_link_errors(root, link_base, text))
    return errors


def main():
    errors = validate_repository()
    if errors:
        print("Validation failed:\n" + "\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    papers, resources, _ = load_catalog()
    print(f"Validated {len(papers)} papers, {len(resources)} resources and {len(load_benchmarks())} benchmark comparisons, public-content hygiene, and local Markdown links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
