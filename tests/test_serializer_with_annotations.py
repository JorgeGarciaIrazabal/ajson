from datetime import timedelta, datetime
import json
import unittest
from typing import List

from ajson.class_decorator import AJson
from ajson.json_class_reports import JsonClassReports, ISO_FORMAT
from ajson.aserializer import ASerializer


class TestSerializationWithAnnotations(unittest.TestCase):
    # Test with AJson decoration
    def setUp(self):
        self.serializer = ASerializer()
        JsonClassReports().clear()

    def test_empty_object_with_ajson_returns_empty_object(self):
        @AJson()
        class SEmptyObjectAJson(object):
            def __init__(self):
                self.a = 1

        serialization = self.serializer.serialize(SEmptyObjectAJson())
        self.assertEqual(len(json.loads(serialization).keys()), 0)

    def test_object_with_ajson_returns_only_as_attributes(self):
        @AJson()
        class SSimpleObjectAJson(object):
            def __init__(self):
                self.a = 1  # @aj{}
                self.b = 1

        serialization = self.serializer.serialize(SSimpleObjectAJson())
        self.assertEqual(len(json.loads(serialization).keys()), 1)
        self.assertEqual(json.loads(serialization)["a"], 1)

    def test_object_with_ajson_returns_only_attributes_in_group(self):
        @AJson()
        class SSimpleObjectAJsonWithGroups(object):
            def __init__(self):
                self.a = 1  # @aj{"groups": ["admin"]}
                self.b = 2  # @aj{"groups": ["public"]}

        serialization = self.serializer.serialize(SSimpleObjectAJsonWithGroups(), groups=["admin"])
        self.assertEqual(len(json.loads(serialization).keys()), 1)
        self.assertEqual(json.loads(serialization)["a"], 1)

        serialization = self.serializer.serialize(SSimpleObjectAJsonWithGroups(), groups=["public"])
        self.assertEqual(len(json.loads(serialization).keys()), 1)
        self.assertEqual(json.loads(serialization)["b"], 2)

    def test_object_with_ajson_returns_only_attributes_in_group_with_nested_references(self):
        @AJson()
        class SSimpleObjectAJsonNested1(object):
            def __init__(self):
                self.a = 1  # @aj{"groups": ["admin"]}
                self.b = 2  # @aj{"groups": ["public"]}

        @AJson()
        class SSimpleObjectAJsonNested2(object):
            def __init__(self):
                self.nested1 = SSimpleObjectAJsonNested1()  # @aj{"groups": ["admin"]}
                self.nested2 = SSimpleObjectAJsonNested1()  # @aj{"groups": ["public"]}

        dict_obj = self.serializer.to_dict(SSimpleObjectAJsonNested2(), groups=["admin"])
        self.assertEqual(len(dict_obj.keys()), 1)
        self.assertEqual(dict_obj["nested1"], {"a": 1})

        dict_obj = self.serializer.to_dict(SSimpleObjectAJsonNested2(), groups=["admin", "public"])
        self.assertEqual(len(dict_obj.keys()), 2)
        self.assertEqual(dict_obj["nested1"], {"a": 1, "b": 2})
        self.assertEqual(dict_obj["nested2"], {"a": 1, "b": 2})

    def test_object_with_ajson_and_date_format_returns_the_right_date_format(self):
        @AJson()
        class SSimpleObjectWithDate(object):
            def __init__(self):
                self.time1 = datetime(2000, 2, 1, 5, 30)  # @aj{"d_format": "%Y/%m/%d"}
                self.time2 = datetime(2010, 5, 10, 2, 40)  # @aj{"d_format": "%Y--%H%M"}

        dict_obj = self.serializer.to_dict(SSimpleObjectWithDate())
        self.assertEqual(len(dict_obj.keys()), 2)
        self.assertEqual(dict_obj["time1"], "2000/02/01")
        self.assertEqual(dict_obj["time2"], "2010--0240")

    # Unserialize
    def test_simple_entity_is_unserialize_from_dict(self):
        @AJson()
        class USSimpleObjectAJson(object):
            def __init__(self):
                self.a = 1

        dict_obj = {
            "a": 10
        }

        obj: USSimpleObjectAJson = self.serializer.from_dict(dict_obj, USSimpleObjectAJson)
        self.assertEqual(obj.a, 10)

    # Unserialize
    def test_unserialize_with_different_name_nade_date_time_format(self):
        @AJson()
        class USNameAndDateObjectAJson(object):
            def __init__(self):
                self.a = 1  # @aj{"name": "my_mane"}
                self.date = None  # @aj{"d_format": "%Y--%H%M"}

        dict_obj = {
            "a": 10,  # this should be ignored
            "my_mane": 20,
            "date": "2010--0240",
        }

        obj: USNameAndDateObjectAJson = self.serializer.from_dict(dict_obj, USNameAndDateObjectAJson)
        self.assertEqual(obj.a, 20)
        self.assertIsInstance(obj.date, datetime)

    # Unserialize
    def test_unserialize_list_returns_list_of_objects(self):
        @AJson()
        class USNameAndDateObjectAJson2(object):
            def __init__(self):
                self.a = 1  # @aj{"name": "my_mane"}
                self.date: datetime = None  # @aj{"d_format": "%Y/%m/%d"}

        list_dict = [
            {
                "my_mane": 1,
                "date": "2000/01/01",
            },
            {
                "my_mane": 2,
                "date": "2000/02/01",
            },
            {
                "my_mane": 3,
                "date": "2000/03/01",
            },
        ]

        list_obj: List[USNameAndDateObjectAJson2] = self.serializer.from_dict(list_dict, USNameAndDateObjectAJson2)
        self.assertEqual(len(list_obj), 3)
        self.assertEqual(list_obj[0].a, 1)
        self.assertEqual(list_obj[0].date.month, 1)
        self.assertEqual(list_obj[1].date.month, 2)
        self.assertEqual(list_obj[2].date.month, 3)

    # Unserialize
    def test_unserialize_nested_objects(self):
        @AJson(class_name="o1")
        class USNestedObject0(object):
            def __init__(self):
                self.a = 1  # @aj{"name": "my_mane"}
                self.date: datetime = None  # @aj{"d_format": "%Y/%m/%d"}

        @AJson(class_name="o2")
        class USNestedObject1(object):
            def __init__(self):
                self.nested = USNestedObject0()  # @aj{"type": "o1"}

        obj_dict = {
            "nested": {
                "my_mane": 3,
                "date": "2003/01/01",
            },
        }

        obj: USNestedObject1 = self.serializer.from_dict(obj_dict, USNestedObject1)
        self.assertEqual(obj.nested.a, 3)
        self.assertIsInstance(obj.nested.date, datetime)
        self.assertEqual(obj.nested.date.year, 2003)
