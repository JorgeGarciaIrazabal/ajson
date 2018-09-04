from datetime import datetime
from typing import List, Optional, Union

from ajson import AJson


@AJson()
class SEmptyObjectAJson(object):
    def __init__(self):
        self.a = 1


@AJson()
class SSimpleObjectAJson(object):
    def __init__(self):
        self.a = 1  # @aj()
        self.b = 1


@AJson()
class SSimpleObjectAJsonWithGroups(object):
    def __init__(self):
        self.a = 1  # @aj(groups=["admin"])
        self.b = 2  # @aj(groups=["public"])


@AJson()
class SObjectWithGroupsAndNoGroups(object):
    def __init__(self):
        self.a = 1  # @aj(groups=["admin"])
        self.b = 2  # @aj(groups=["public"])
        self.c = 8  # @aj()
        self.d = 9


@AJson()
class SObjectWithProperties(object):
    def __init__(self):
        self._a = 1
        self._b = 2

    @property
    def a(self):
        """ @aj() """
        return self._a

    @property
    def b(self):
        """ @aj(groups='["g1"]') """
        return self._b


@AJson()
class SSimpleObjectAJsonNested1(object):
    def __init__(self):
        self.a = 1  # @aj(groups=["admin"])
        self.b = 2  # @aj(groups=["public"])


@AJson()
class SSimpleObjectAJsonNested2(object):
    def __init__(self):
        self.nested1 = SSimpleObjectAJsonNested1()  # @aj(groups=["admin"])
        self.nested2 = SSimpleObjectAJsonNested1()  # @aj(groups=["public"])


@AJson()
class SSimpleObjectWithDate(object):
    def __init__(self):
        self.time1 = datetime(2000, 2, 1, 5, 30)  # @aj(d_format="%Y/%m/%d")
        self.time2 = datetime(2010, 5, 10, 2, 40)  # @aj(d_format="%Y--%H%M")


@AJson()
class USSimpleObjectAJson(object):
    def __init__(self):
        self.a = 1


@AJson()
class USNameAndDateObjectAJson(object):
    a = 1  # @aj(name="my_mane")
    date = None  # @aj(d_format="%Y--%H%M")


@AJson()
class USNameAndDateObjectAJson2(object):
    a = 1  # @aj(name="my_mane")
    date: datetime = None  # @aj(d_format="%Y/%m/%d")


@AJson()
class USNestedObject0(object):
    a: int  # @aj(name="my_mane")
    date: datetime  # @aj(d_format="%Y/%m/%d")

    def __init__(self):
        self.a = 1
        self.date: datetime = None


@AJson()
class USNestedObject1(object):
    nested: USNestedObject0 = USNestedObject0()  # @aj()


@AJson()
class USNestedListObject(object):
    nested_list: List[USNestedObject0] = [USNestedObject0()]  # @aj()


@AJson()
class USRequiredObject(object):
    a: int  # @aj(required)
    b: int  # @aj()


@AJson()
class USWithoutAnnotationsObject(object):
    a: int
    b: int


@AJson()
class USWithHintsObject(object):
    a: int
    b: str


@AJson()
class USWithOptionalHintsObject(object):
    a: Optional[int]
    b: str


@AJson()
class USWithMultiTypeHintsObject(object):
    a: Union[int, str]


@AJson()
class USWithProperties(object):
    def __init__(self):
        self._a = 1
        self._b = 2

    @property
    def a(self) -> int:
        """ @aj() """
        return self._a

    @property
    def b(self):
        """ @aj(name=new_b) """
        return self._b

    @a.setter
    def a(self, a):
        self._a = a

    @b.setter
    def b(self, b):
        self._b = b

    def this_is_a_func(self) -> str:
        return "testing"


def div(a: int, b: int) -> float:
    """Divide a by b"""
    return a / b
