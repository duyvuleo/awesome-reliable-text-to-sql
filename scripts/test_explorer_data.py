"""Conservation and provenance tests for the public explorer adapter."""
import json
import unittest
from catalog import ROOT, load_catalog, load_benchmarks
from explorer_data import build_payload, render_data

class ExplorerTests(unittest.TestCase):
    def setUp(self):
        self.papers, self.resources, self.meta = load_catalog()
        self.benchmarks = load_benchmarks()
        self.data = build_payload(self.papers,self.resources,self.benchmarks,self.meta,json.loads((ROOT/'data/explorer-taxonomy.json').read_text()))

    def test_conservation(self):
        originals = {x['id']:x for x in self.papers+self.resources}
        records = self.data['records']
        self.assertEqual(len(records), len(originals))
        self.assertEqual({r['id'] for r in records},set(originals))
        for r in records:
            self.assertEqual(r['original'], originals[r['id']])
            self.assertEqual(r['sources'], originals[r['id']]['evidence'])
        members = [i for w in self.data['works'] for i in w['entry_ids']]
        self.assertCountEqual(members,originals)

    def test_explicit_grouping_and_shared_tools(self):
        records={r['id']:r for r in self.data['records']}
        self.assertEqual(records['clarity-data']['work_id'],'clarity')
        self.assertEqual(records['clarity-pipeline']['work_id'],'clarity')
        self.assertEqual(records['rts-sql-tool']['work_id'],'rts-sql-tool')
        edges={(e['source'],e['target']) for e in self.data['relations']}
        self.assertIn(('rts-sql-tool','rts'),edges)
        self.assertIn(('rts-sql-tool','rts-plus'),edges)
        ids={w['id'] for w in self.data['works']}
        self.assertTrue(all(e['source'] in ids and e['target'] in ids for e in self.data['relations']))

    def test_resource_year_is_not_release_date(self):
        r={r['id']:r for r in self.data['records']}
        self.assertIsNone(r['intentsql-system']['year'])
        self.assertEqual(r['clarity-data']['date_label'],'Latest linked paper year')
        self.assertIsNone(r['clarity-data']['added_on'])

    def test_comparisons_and_determinism(self):
        self.assertEqual(self.data['comparisons'],self.benchmarks)
        self.assertEqual(json.loads(render_data(ROOT)), self.data)
        self.assertEqual(render_data(ROOT),render_data(ROOT))
        for t in self.data['themes']:
            self.assertEqual(t['count'],sum(t['id'] in w['themes'] for w in self.data['works']))

if __name__=='__main__': unittest.main()
