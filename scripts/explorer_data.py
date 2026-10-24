"""Generate the static explorer from explicit catalog links, preserving source records."""
from collections import Counter
import json
from catalog import CATEGORIES, load_catalog, load_benchmarks

REPO = 'https://github.com/duyvuleo/awesome-reliable-text-to-sql'


def build_payload(papers, resources, benchmarks, meta, taxonomy=None):
    taxonomy = taxonomy or {"excluded_tags": ["benchmark"], "aliases": {}, "labels": {}}
    paper_map = {p['id']: p for p in papers}
    records = []
    for p in papers:
        records.append(dict(id=p['id'], name=p['title'], kind='paper', year=p['year'],
            date=str(p['year']), date_label='Publication year', summary=p['summary'],
            tags=p['topics'], categories=[p['category']], evidence=p['publication_status'],
            status=p.get('artifact_status', ''), sources=p['evidence'], checked=p['checked_on'],
            added_on=p['added_on'], url=p['primary_url'], code_links=[p['code_url']] if p['code_url'] else [],
            catalog_url=f"{REPO}/blob/main/papers/README.md#{p['id']}", original=p, work_id=p['id']))
    for r in resources:
        linked = [paper_map[i] for i in r['paper_ids']]
        year = max((p['year'] for p in linked), default=None)
        folder = 'datasets' if r['kind'] == 'dataset' else 'systems'
        records.append(dict(id=r['id'], name=r['name'], kind='benchmark' if r['kind']=='dataset' else r['kind'],
            year=year, date=str(year) if year else 'Undated', date_label='Latest linked paper year',
            summary=r['description'], tags=sorted({t for p in linked for t in p['topics']}),
            categories=sorted({p['category'] for p in linked}), evidence='resource', status=r['availability'],
            sources=r['evidence'], checked=r['checked_on'], added_on=None, url=r['url'],
            code_links=[r['url']] if r['kind'] in {'system','tool'} else [],
            catalog_url=f"{REPO}/blob/main/{folder}/README.md#{r['id']}", original=r,
            work_id=linked[0]['id'] if len(linked)==1 else r['id']))
    groups = {}
    for r in records:
        groups.setdefault(r['work_id'], []).append(r)
    works = []
    for wid, members in groups.items():
        primary = next(r for r in members if r['id']==wid)
        works.append(dict(id=wid, name=primary['name'], date=primary['date'], year=primary['year'],
            kind=primary['kind'], summary=primary['summary'], entry_ids=[r['id'] for r in members],
            themes=sorted({taxonomy['aliases'].get(t,t) for r in members for t in r['tags'] if t not in taxonomy['excluded_tags']}),
            categories=sorted({c for r in members for c in r['categories']}),
            kinds=sorted({r['kind'] for r in members}), years=sorted({r['year'] for r in members if r['year']})))
    works.sort(key=lambda w: (-(w['year'] or 0), w['name'].casefold(), w['id']))
    work_of = {r['id']:r['work_id'] for r in records}
    relations = []
    for r in resources:
        for pid in r['paper_ids']:
            if work_of[r['id']] != pid:
                relations.append(dict(source=work_of[r['id']], target=pid, kind='paper-resource', entry_pairs=[[r['id'],pid]]))
    counts = Counter(t for w in works for t in w['themes'])
    themes = [dict(id=t, label=taxonomy['labels'].get(t,t.replace('-', ' ').capitalize()), count=n) for t,n in sorted(counts.items(), key=lambda p:(-p[1],p[0]))]
    return dict(schema_version=1, checked=max(r['checked'] for r in records), updated=meta['updated'],
        repository=REPO, counts=dict(Counter(r['kind'] for r in records)), categories=CATEGORIES,
        works=works, records=records, themes=themes, relations=relations, comparisons=benchmarks)


def render_data(root):
    papers, resources, meta = load_catalog(root)
    return json.dumps(build_payload(papers, resources, load_benchmarks(root), meta, json.loads((root/'data/explorer-taxonomy.json').read_text())), ensure_ascii=False, indent=2)+'\n'
