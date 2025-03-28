from map.abstract import MapStore
from pathlib import Path
import shutil
import unittest
from uuid import uuid4

testdata_path_prefix = "./src/tests/testdata-"
schema_path = "./src/map/schema.sql"
init_path = "./src/map/init.sql"

class TestMapStore(unittest.TestCase):
    def setUp(self):
        self.test_path = testdata_path_prefix + str(uuid4())
        self.testdata_dir = Path(self.test_path)
        self.store = MapStore(path=self.test_path, init_path=init_path, schema_path=schema_path)

    def tearDown(self):
        self.store.close()
        if self.testdata_dir.exists():
            shutil.rmtree(self.testdata_dir)
        return super().tearDown()

    def test_init_values(self):
        self.assertEqual(self.store.store_folder, self.testdata_dir)
        self.assertEqual(self.store.init_file, Path(init_path))
        self.assertEqual(self.store.schema_file, Path(schema_path))
        self.assertEqual(self.store._maps, [])

    def test_create(self):
        map = self.store.create_map("secret-name", "test-map")
        self.assertEqual(map.name, "secret-name")
        self.assertEqual(map.elements, [])
        self.assertEqual(map.map_file, Path(self.test_path) / "test-map.dmap")

    def test_list(self):
        self.assertEqual(len(self.store.list()), 0)
        map = self.store.create_map("secret-name", "test-map")
        list = self.store.list()
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0].map_file, map.map_file)

    def test_list_no_refresh(self):
        self.store.create_map("secret-name", "test-map")
        list = self.store.list(no_refresh=True)
        self.assertEqual(len(list), 0)

    def test_delete(self):
        self.store.create_map("secret-name", "test-map")
        list = self.store.list()
        self.assertEqual(len(list), 1)
        self.store.delete_map(list[0])
        list = self.store.list()
        self.assertEqual(len(list), 0)
