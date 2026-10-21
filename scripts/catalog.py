"""Shared, standard-library helpers for the public research catalog."""

from __future__ import annotations

import ipaddress
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = {
    "ambiguity": "Ambiguity and multiple interpretations",
    "answerability": "Answerability, uncertainty, and abstention",
    "interaction": "Clarification and interactive systems",
    "context": "Context, knowledge, and realistic workloads",
    "verification": "Verification and evaluation validity",
}
FEATURED_IDS = ("abiss", "clarity", "ambiqt", "practiq", "trustsql", "cosql")


def load_catalog(root: Path = ROOT):
    values = []
    for name in ("papers", "resources", "meta"):
        with (root / "data" / f"{name}.json").open(encoding="utf-8") as handle:
            values.append(json.load(handle))
    return tuple(values)


def public_url_error(value):
    if not isinstance(value, str) or not value.strip():
        return "must be a nonempty public HTTP(S) URL"
    try:
        parsed = urlsplit(value)
        host = (parsed.hostname or "").lower().rstrip(".")
        _ = parsed.port
    except ValueError:
        return "has invalid URL syntax"
    if parsed.scheme not in {"http", "https"} or not host:
        return "must use HTTP(S) with a hostname"
    if parsed.username or parsed.password:
        return "must not contain embedded credentials"
    if any(character.isspace() for character in value):
        return "must not contain whitespace"
    forbidden = {"localhost", "confluence.oraclecorp.com", "jira.oraclecorp.com", "wiki.cerner.com"}
    suffixes = (".localhost", ".local", ".internal", ".corp", ".lan", ".home.arpa", ".oraclecorp.com")
    if host in forbidden or host.endswith(suffixes):
        return "points to a local or internal host"
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        if "." not in host:
            return "must not use a single-label internal hostname"
    else:
        if not address.is_global:
            return "points to a nonpublic IP address"
    return None


def canonical_url(value: str):
    parsed = urlsplit(value.strip())
    host = (parsed.hostname or "").lower()
    path = parsed.path.rstrip("/")
    if host in {"arxiv.org", "www.arxiv.org", "export.arxiv.org"}:
        path = re.sub(r"^/(?:abs|pdf|html)/", "/abs/", path)
        path = re.sub(r"(?:v\d+)?(?:\.pdf)?$", "", path)
        return "https://arxiv.org" + path
    if host in {"doi.org", "dx.doi.org"}:
        return "https://doi.org" + path.lower()
    if host == "github.com":
        path = re.sub(r"\.git$", "", path.lower())
    tracking_parameters = {"fbclid", "gclid", "dclid", "msclkid", "_ga", "mc_cid", "mc_eid"}
    query = urlencode(sorted((key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True)
                             if not key.lower().startswith("utm_") and key.lower() not in tracking_parameters))
    return urlunsplit(("https", host, path, query, ""))


def markdown_text(value: str):
    return value.replace("[", "\\[").replace("]", "\\]").replace("\n", " ")


def sorted_papers(records):
    return sorted(records, key=lambda item: (-item["year"], item["title"].casefold()))


def recent_papers(records):
    """Order additions without modifying their stable first-added dates."""
    return sorted(records, key=lambda item: (-date.fromisoformat(item["added_on"]).toordinal(),
                                            -item["year"], item["title"].casefold()))
