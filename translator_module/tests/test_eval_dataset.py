"""The evaluation dataset must stay consumable by the pipeline it scores.

Three contracts are checked here, all of which would otherwise break silently:

  * every gold IR validates against the pipeline's own Pydantic models;
  * every gold IR serialises to exactly the ``query_oks`` string stored in the
    dataset, so a generated query can be compared to it directly; and
  * the schema corpus parses through the same chunking the indexer performs.
"""

import json
import os
import unittest
import xml.etree.ElementTree as ET

from agent.ir_validator import validate_ir
from agent.serializer import serialize_ir_to_oks

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QUERIES = os.path.join(REPO_ROOT, "eval_dataset", "oks_eval_queries.jsonl")
CORPUS = os.path.join(REPO_ROOT, "eval_dataset", "oks_schema_corpus.xml")


def _load_rows():
    with open(QUERIES, "r", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


@unittest.skipUnless(os.path.isfile(QUERIES), "eval_dataset/oks_eval_queries.jsonl not built")
class TestEvalQueries(unittest.TestCase):
    def setUp(self):
        self.rows = _load_rows()

    def test_dataset_is_populated_and_stratified(self):
        self.assertGreater(len(self.rows), 100)
        bands = {r["difficulty"] for r in self.rows}
        self.assertEqual(bands, {"easy", "medium", "hard"})

    def test_every_gold_ir_validates_and_round_trips(self):
        checked = 0
        for row in self.rows:
            ir = row.get("query_ir")
            if ir is None:            # path queries have no IR representation yet
                self.assertFalse(row["ir_expressible"], row["id"])
                continue
            with self.subTest(row=row["id"]):
                validated = validate_ir(ir)
                self.assertEqual(serialize_ir_to_oks(validated), row["query_oks"])
            checked += 1
        self.assertGreater(checked, 100)

    def test_required_fields_are_present(self):
        required = {
            "id", "split", "difficulty", "question", "target_class", "scope",
            "constructs", "query_ir", "query_oks", "gold_schema_elements",
            "expected_object_ids", "expected_count", "ir_expressible",
            "oks_dump_cmd", "note", "source_file",
        }
        ids = set()
        for row in self.rows:
            self.assertEqual(required - set(row), set(), row.get("id"))
            self.assertNotIn(row["id"], ids, "duplicate row id")
            ids.add(row["id"])

    def test_few_shot_manager_can_read_the_rows(self):
        """FewShotManager only needs question/query_oks, and reads note if present."""
        for row in self.rows:
            self.assertTrue(row["question"].strip())
            self.assertTrue(row["query_oks"].strip())
            self.assertIsInstance(row.get("note", ""), str)


@unittest.skipUnless(os.path.isfile(CORPUS), "eval_dataset/oks_schema_corpus.xml not built")
class TestSchemaCorpus(unittest.TestCase):
    def test_corpus_chunks_the_way_the_indexer_does(self):
        """Mirror HybridIndexer.ingest_xml: example -> schema-file -> class."""
        root = ET.parse(CORPUS).getroot()
        self.assertEqual(root.tag, "training-examples")

        names = set()
        for example in root.findall(".//example"):
            for schema_file in example.findall(".//schema-file"):
                text = schema_file.text
                self.assertTrue(text and text.strip(), schema_file.get("name"))
                embedded = ET.fromstring(text.strip())   # must be a parseable document
                for cls in embedded.findall(".//class"):
                    names.add(cls.get("name"))

        self.assertGreater(len(names), 400)
        # configuration schema and the C++ API surface both have to be reachable
        self.assertIn("Partition", names)
        self.assertIn("BaseApplication", names)
        self.assertIn("OksQuery", names)
        self.assertIn("OksKernel", names)

    def test_data_blocks_are_parseable(self):
        root = ET.parse(CORPUS).getroot()
        blocks = root.findall(".//data-file")
        self.assertGreater(len(blocks), 0)
        for block in blocks:
            ET.fromstring((block.text or "").strip())


if __name__ == "__main__":
    unittest.main()
