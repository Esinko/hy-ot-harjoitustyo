from map_store.store import MapStore
from pathlib import Path
from os.path import join
import shutil
import unittest
from uuid import uuid4

testdata_path_prefix = "./src/tests/testdata-"
schema_path = "./src/map_store/schema.sql"
init_path = "./src/map_store/init.sql"


class TestMapStore(unittest.TestCase):
    def setUp(self):
        self.test_path = testdata_path_prefix + str(uuid4())
        self.testdata_dir = Path(self.test_path)
        self.store = MapStore(path=self.test_path,
                              init_path=init_path, schema_path=schema_path)

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

    def test_get(self):
        map = self.store.create_map("secret-name", "test-map")
        got_map = self.store.get(map.map_file.name)
        self.assertEqual(map.map_file.name, got_map.map_file.name)

    def test_export(self):
        map = self.store.create_map("secret-name", "test-map")
        self.store.export(map, join(self.test_path, "./secret-name.dmap"))
        self.assertEqual(
            Path(join(self.test_path, "./secret-name.dmap")).exists(), True)

    def test_import(self):
        print([map.name for map in self.store.list()])
        map = self.store.create_map("secret-name", "test-map")
        Path(join(self.test_path, "./dummy/")).mkdir()
        file_path = join(self.test_path, "./dummy/secret-name.dmap")
        self.store.export(map, file_path)
        self.store.add(file_path)
        print([map.name for map in self.store.list()])
        self.assertEqual(len(self.store.list()), 2)

    def test_list_no_refresh(self):
        # Create will be detected, delete not (cache must refresh on create only)
        created_map = self.store.create_map("secret-name", "test-map")
        created_map.delete()
        list = self.store.list(no_refresh=True)
        self.assertEqual(len(list), 1)

    def test_delete(self):
        self.store.create_map("secret-name", "test-map")
        list = self.store.list()
        self.assertEqual(len(list), 1)
        list[0].delete()
        list = self.store.list()
        self.assertEqual(len(list), 0)
