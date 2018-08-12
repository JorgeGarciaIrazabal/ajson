import datetime
from datetime import timedelta
import json
import unittest

from _class_decorator import AJson
from _json_class_reports import JsonClassReports
from serializer import Serializer


class TestSerialization(unittest.TestCase):
    # Test with AJson decoration
    def setUp(self):
        self.serializer = Serializer()
        JsonClassReports().clear()

    def test_basic_object_serialization(self):
        serialization = self.serializer.serialize(5)
        self.assertTrue(serialization == '5', 'number serialization')
        serialization = self.serializer.serialize("hi")
        self.assertTrue(serialization == '"hi"', 'str serialization')

    def test_simple_objects(self):
        class SSimpleObject(object):
            def __init__(self):
                self.a = 1
                self.b = "hi"

        serialization = self.serializer.serialize(SSimpleObject())
        self.assertTrue(json.loads(serialization)["a"] == 1)
        self.assertTrue(json.loads(serialization)["b"] == "hi")

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
            self.assertIn('a', checking_obj)
            checking_obj = checking_obj['a']
        self.assertNotIn('a', checking_obj)

    def test_date_time_objects(self):
        date = datetime.datetime.now()
        serialization = self.serializer.serialize({"datetime": date})
        self.assertIn(Serializer.DATE_TAME_KEY, serialization)
        datetime_obj = self.serializer.unserialize(serialization)
        self.assertIsInstance(datetime_obj['datetime'], datetime.datetime)
        print(datetime.datetime.now() - datetime_obj['datetime'])
        self.assertTrue(datetime.datetime.now() - datetime_obj['datetime'] < timedelta(milliseconds=25))

    # Test with AJson decoration todo: consider creating a different TestCase for this
    def test_empty_object_with_ajson_returns_empty_object(self):
        @AJson
        class SEmptyObjectAJson(object):
            def __init__(self):
                self.a = 1

        serialization = self.serializer.serialize(SEmptyObjectAJson())
        self.assertEqual(len(json.loads(serialization).keys()), 0)

    def test_object_with_ajson_returns_only_as_attributes(self):
        @AJson
        class SSimpleObjectAJson(object):
            def __init__(self):
                self.a = 1  # @as{}
                self.b = 1

        serialization = self.serializer.serialize(SSimpleObjectAJson())
        self.assertEqual(len(json.loads(serialization).keys()), 1)
        self.assertEqual(json.loads(serialization)["a"], 1)

    def test_object_with_ajson_returns_only_attributes_in_group(self):
        @AJson
        class SSimpleObjectAJsonWithGroups(object):
            def __init__(self):
                self.a = 1  # @as{"groups": ["admin"]}
                self.b = 2  # @as{"groups": ["public"]}

        serialization = self.serializer.serialize(SSimpleObjectAJsonWithGroups(), groups=["admin"])
        self.assertEqual(len(json.loads(serialization).keys()), 1)
        self.assertEqual(json.loads(serialization)["a"], 1)

        serialization = self.serializer.serialize(SSimpleObjectAJsonWithGroups(), groups=["public"])
        self.assertEqual(len(json.loads(serialization).keys()), 1)
        self.assertEqual(json.loads(serialization)["b"], 2)

    def test_object_with_ajson_returns_only_attributes_in_group_with_nested_references(self):
        @AJson
        class SSimpleObjectAJsonNested1(object):
            def __init__(self):
                self.a = 1  # @as{"groups": ["admin"]}
                self.b = 2  # @as{"groups": ["public"]}

        @AJson
        class SSimpleObjectAJsonNested2(object):
            def __init__(self):
                self.nested1 = SSimpleObjectAJsonNested1()  # @as{"groups": ["admin"]}
                self.nested2 = SSimpleObjectAJsonNested1()  # @as{"groups": ["public"]}

        dict_obj = self.serializer.to_dict(SSimpleObjectAJsonNested2(), groups=["admin"])
        self.assertEqual(len(dict_obj.keys()), 1)
        self.assertEqual(dict_obj["nested1"], {"a": 1})

        dict_obj = self.serializer.to_dict(SSimpleObjectAJsonNested2(), groups=["admin", "public"])
        self.assertEqual(len(dict_obj.keys()), 2)
        self.assertEqual(dict_obj["nested1"], {"a": 1, "b": 2})
        self.assertEqual(dict_obj["nested2"], {"a": 1, "b": 2})
