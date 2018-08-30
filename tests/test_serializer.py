import json
import unittest
from datetime import timedelta, datetime

from ajson.aserializer import ASerializer
from ajson.json_type_reports import JsonTypeReports, ISO_FORMAT


class TestSerialization(unittest.TestCase):
    def setUp(self):
        self.serializer = ASerializer()
        self.old_reports = JsonTypeReports().reports
        JsonTypeReports().clear()

    def tearDown(self):
        JsonTypeReports().reports = self.old_reports

    def test_basic_object_serialization(self):
        serialization = self.serializer.serialize(5)
        self.assertTrue(serialization == "5", "number serialization")
        serialization = self.serializer.serialize("hi")
        self.assertTrue(serialization == '"hi"', "str serialization")

    def test_simple_objects(self):
        class SSimpleObject(object):
            def __init__(self):
                self.a = 1
                self.b = "hi"
                self.c = None

        obj_dict = self.serializer.to_dict(SSimpleObject())
        self.assertTrue(obj_dict["a"] == 1)
        self.assertTrue(obj_dict["b"] == "hi")
        self.assertIsNone(obj_dict["c"])

    def test_complex_objects(self):
        class SComplexObject(object):
            def __init__(self):
                self.a = {"a": 10, 1: 15}
                self.b = [1, 2, "hello"]

        serialization = self.serializer.serialize(SComplexObject())
        ser_obj = json.loads(serialization)
        self.assertTrue(isinstance(ser_obj["a"], dict))
        self.assertTrue(ser_obj["a"]["a"] == 10)
        self.assertTrue(ser_obj["a"]["1"] == 15)
        self.assertTrue(len(ser_obj["b"]) == 3)

    def test_cycle_ref(self):
        class SCycleRefObject(object):
            def __init__(self):
                self.a = self

        serialization = self.serializer.serialize(SCycleRefObject())
        ser_obj = json.loads(serialization)
        checking_obj = ser_obj
        for i in range(self.serializer.max_depth):
            self.assertIn("a", checking_obj)
            checking_obj = checking_obj["a"]
        self.assertNotIn("a", checking_obj)

    def test_date_time_objects(self):
        date = datetime.now()
        date_dict = self.serializer.to_dict({"datetime": date})
        parsed_datetime = datetime.strptime(date_dict["datetime"], ISO_FORMAT)
        self.assertTrue(
            datetime.now() - parsed_datetime < timedelta(milliseconds=1000),
            datetime.now() - parsed_datetime
        )

    def test_handler_modify_specific_types(self):
        self.serializer.add_serialize_handler(datetime, lambda d, g, a: "test")
        date = datetime.now()
        date_dict = self.serializer.to_dict({"datetime": date})
        self.assertEqual(date_dict["datetime"], "test")

    # Unserialize

    def test_simple_unserialize_returns_dict(self):
        class SSimpleObject(object):
            def __init__(self):
                self.a = 5
                self.b = "hi"
                self.c = None

        obj_src = self.serializer.serialize(SSimpleObject())
        obj_dict = self.serializer.unserialize(obj_src)
        self.assertEqual(obj_dict["a"], 5)
        self.assertEqual(obj_dict["b"], "hi")
        self.assertIsNone(obj_dict["c"])

    def test_simple_unserialize_date_time_with_iso_format(self):
        date = datetime.now()
        date_src = self.serializer.serialize({"datetime": date})
        date_dict = self.serializer.unserialize(date_src)
        self.assertIsInstance(date_dict["datetime"], datetime)
