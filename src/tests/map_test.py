from map_store.store import MapStore
from pathlib import Path
import shutil
import unittest
from uuid import uuid4

testdata_path_prefix = "./src/tests/testdata-"
schema_path = "./src/map_store/schema.sql"
init_path = "./src/map_store/init.sql"


class TestMap(unittest.TestCase):
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

    def test_get_elements(self):
        map = self.store.create_map("secret-name", "test-map")
        element_dict = {
            "name": "Test tile",
            "x": 0,
            "y": 0,
            "width": 1,
            "height": 1,
            "background_image": None,
            "rotation": 22,
            "background_color": None
        }
        self.assertEqual(len(map.get_elements()), 0)
        map.create_element(element_dict)
        elements = map.get_elements()
        self.assertEqual(len(elements), 1)

    def test_add_element_properties(self):
        map = self.store.create_map("secret-name", "test-map")
        image_data = Path("./src/tests/sample_image.jpg").read_bytes()
        element_dict = {
            "name": "Test tile",
            "x": 0,
            "y": 0,
            "width": 1,
            "height": 1,
            "background_image": {
                "name": "test",
                "data": list(image_data)
            },
            "rotation": 21,
            "background_color": None
        }
        element = map.create_element(element_dict)
        elements = map.get_elements()
        self.assertEqual(len(elements), 1)
        element_dict["id"] = element.id
        element_dict["background_image"]["id"] = element.background_image.id
        self.assertDictEqual(elements[0].to_dict(), element_dict)

    def test_remove_element(self):
        map = self.store.create_map("secret-name", "test-map")
        element_dict = {
            "name": "Test tile",
            "x": 0,
            "y": 0,
            "width": 1,
            "height": 1,
            "rotation": 0,
            "background_color": None,
            "background_image": None
        }
        element = map.create_element(element_dict)
        map.remove_element(element.id)
        elements = map.get_elements()
        self.assertEqual(len(elements), 0)

    def test_edit_tile(self):
        map = self.store.create_map("secret-name", "test-map")
        element_dict = {
            "name": "Test tile",
            "x": 0,
            "y": 0,
            "width": 1,
            "height": 1,
            "rotation": 0,
            "background_color": None,
            "background_image": None
        }
        element = map.create_element(element_dict)
        image_data = Path("./src/tests/sample_image.jpg").read_bytes()
        edited_element_dict = {
            "id": element.id,
            "name": "Edited Test tile",
            "x": 1,
            "y": 1,
            "width": 2,
            "height": 1,
            "background_image": {
                "name": "test2",
                "data": list(image_data)
            },
            "rotation": 11,
            "background_color": "#000"
        }
        edited_element = map.edit_element(element.id, edited_element_dict)
        elements = map.get_elements()
        self.assertEqual(len(elements), 1)
        edited_element_dict["background_image"]["id"] = edited_element.background_image.id
        self.assertDictEqual(elements[0].to_dict(), edited_element_dict)

    def test_add_text_properties(self):
        map = self.store.create_map("secret-name", "test-map")
        text_name = "test-text"
        text_value = "foo bar"
        text_obj = map.create_text(text_name, text_value, 1, 1)
        text_list = map.get_text_list()
        self.assertEqual(text_list[0].id, text_obj.id)
        self.assertEqual(text_list[0].name, text_obj.name)
        self.assertEqual(text_list[0].value, text_obj.value)
        self.assertEqual(text_list[0].x, text_list[0].y)
        self.assertEqual(text_list[0].x, 1)
        self.assertEqual(len(text_list), 1)

    def test_remove_text(self):
        map = self.store.create_map("secret-name", "test-map")
        text_name = "test-text"
        text_value = "foo bar"
        text_obj = map.create_text(text_name, text_value, 1, 1)
        map.remove_text(text_obj.id)
        text_list = map.get_text_list()
        self.assertEqual(len(text_list), 0)
