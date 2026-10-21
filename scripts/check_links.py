#!/usr/bin/env python3
"""Check catalog URLs without changing the catalog; network failures are inconclusive."""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from catalog import load_catalog, public_url_error


class PublicRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        if public_url_error(new_url):
            raise ValueError("Redirect target is not a public HTTP(S) URL")
        return super().redirect_request(request, response, code, message, headers, new_url)


def inspect_url(url, timeout):
    problem = public_url_error(url)
    if problem:
        return {"url": url, "status": "invalid", "detail": problem}
    headers = {"User-Agent": "awesome-reliable-text-to-sql-link-checker/1.0"}
    opener = urllib.request.build_opener(PublicRedirectHandler())
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, headers=headers, method=method)
        try:
            with opener.open(request, timeout=timeout) as response:
                return {"url": url, "status": "reachable", "http_status": response.status, "final_url": response.geturl()}
        except urllib.error.HTTPError as error:
            if method == "HEAD" and error.code in {403, 405, 501}:
                continue
            status = "unavailable" if error.code in {404, 410} else "inconclusive"
            return {"url": url, "status": status, "http_status": error.code}
        except (OSError, ValueError) as error:
            return {"url": url, "status": "inconclusive", "detail": type(error).__name__}
    return {"url": url, "status": "inconclusive"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional JSON report path; do not commit fetched reports")
    parser.add_argument("--timeout", type=float, default=10, help="timeout per request in seconds")
    parser.add_argument("--workers", type=int, default=6, help="parallel requests, capped at 12")
    args = parser.parse_args()
    if not 0 < args.timeout <= 60 or not 1 <= args.workers <= 12:
        parser.error("timeout must be in (0, 60] and workers in [1, 12]")
    try:
        papers, resources, _ = load_catalog()
    except (OSError, ValueError) as error:
        print(f"Cannot read catalog: {error}", file=sys.stderr)
        return 1
    urls = set()
    for item in papers:
        urls.update(item["evidence"])
        urls.update(item[field] for field in ("primary_url", "code_url", "dataset_url") if item.get(field))
    for item in resources:
        urls.update(item["evidence"])
        urls.add(item["url"])
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        results = list(executor.map(lambda url: inspect_url(url, args.timeout), sorted(urls)))
    report = {"checked_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
              "meaning": "HTTP reachability only; failures require review and are not automatic removal decisions.",
              "results": results}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    counts = {status: sum(result["status"] == status for result in results)
              for status in ("reachable", "unavailable", "inconclusive", "invalid")}
    print(json.dumps({"urls_checked": len(results), **counts}, sort_keys=True))
    return 0  # This advisory check never treats transient network failures as catalog validation failures.


if __name__ == "__main__":
    raise SystemExit(main())
