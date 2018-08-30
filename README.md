# AJson (Annotations Json Serializer)

AJson is a serializer based on annotations that gives a lot of flexibility and configuration for you serialization process.

[![Build Status](https://travis-ci.org/JorgeGarciaIrazabal/ajson.svg?branch=master)](https://travis-ci.org/JorgeGarciaIrazabal/ajson)
[![codecov](https://codecov.io/gh/JorgeGarciaIrazabal/ajson/branch/master/graph/badge.svg)](https://codecov.io/gh/JorgeGarciaIrazabal/ajson)


### Install: (python3.6 or greater)

`pip install ajson`

#### Motivation:

There are amazing serialization libraries like [jsonpickle](https://jsonpickle.github.io/), and even more when the serialized object is meant to be used in python too. 
But there are no libraries that let you filter the fields to serialize or modify the names of the attributes, which are features super useful, mainly for http APIs

This library allows you to have those features in a simple and intuitive way.

#### Serialize Examples

###### Simple Serialization With "Groups"
If you want to filter some sensible data in some scenarios, you can define `groups` per each attribute to control what is serialize and what is not

```python
from ajson import AJson, ASerializer

@AJson()
class Restaurant:
    location:str   # @aj(groups=["public","admin"])
    tables: int  # @aj(groups=["public","admin"])
    owner: str  # @aj(groups=["admin"])
    def __init__(self, location, tables, owner):
        self.location = location
        self.tables = tables
        self.owner = owner

serializer = ASerializer()
restaurant = Restaurant("Manhattan", 30, "John Smith")
print(serializer.serialize(restaurant, groups=["public"])) 
# {"location": "Manhattan", "tables": 30}
print(serializer.serialize(restaurant, groups=["admin"])) 
#  {"location": "Manhattan", "tables": 30, "owner": "John Smith"}
```

###### Rename Attributes With "Name"

```python
from ajson import AJson
from ajson.aserializer import ASerializer

@AJson()
class Customer:
    name: str  # @aj(name=firstName)
    primary_email: str  # @aj(name=email)
    last_name: str  # @aj(name=lastName)
    def __init__(self):
        self.name = "John"
        self.last_name = "Smith"
        self.primary_email = "john.smith@something.com"

serializer = ASerializer()
customer = Customer()
print(serializer.serialize(customer))
# {"firstName": "John", "lastName": "Smith", "email": "john.smith@something.com"}
```

###### Nested Objects With Groups And Names

```python
from typing import List
from ajson import AJson, ASerializer


@AJson()
class Customer:
    name: str  # @aj(name=firstName, groups=["public"])
    primary_email: str
    '''
    You can also add the annotation in a multiline docstr
    @aj(
        name=email,
        groups=["public"]
    )
    '''

    def __init__(self, name, primary_email):
        self.name = name
        self.primary_email = primary_email

@AJson()
class Restaurant:
    location: str  # @aj(groups=["public","admin"])
    owner: str  # @aj(groups=["admin"])
    customer_list: List[Customer]  # @aj(groups=["with_customers"] name=customers)

    def __init__(self):
        self.location = None
        self.owner = "John Smith"
        self.customer_list = [
            Customer("Dani", "dani@something.com"),
            Customer("Mike", "maki@something.com")
        ]

restaurant = Restaurant()
print(ASerializer().serialize(restaurant, groups=["public"]))
# '{"location": null}'

# if you want to get the dictionary instead of a string, you can call `to_dict` instead of `serialize`
print(ASerializer().to_dict(restaurant, groups=["public", "with_customers"]))
'''
{
    "location": None,
    "customers": [
        {"firstName": "Dani", "email": "dani@something.com"},
        {"firstName": "Mike", "email": "maki@something.com"}
    ]
}
'''
```

#### Unserialize Examples

###### UnSerialization With Custom Names
```python
from ajson import AJson, ASerializer

@AJson()
class Customer:
    name: str  # @aj(name=firstName)
    primary_email: str  # @aj(name=email)
    last_name: str  # @aj(name=lastName)

serializer = ASerializer()
serialize_str = '{"firstName": "John", "lastName": "Smith", "email": "john.smith@something.com"}'
customer = serializer.unserialize(serialize_str, Customer)
print(customer.name)  # "John"
print(customer.last_name)  # "Smith"
print(customer.primary_email)  # "john.smith@something.com"
```

###### Nested Objects

```python
from typing import List, Optional
from ajson import AJson, ASerializer


@AJson()
class Customer:
    def __init__(self):
        # we can also create the @aj annotation in the attribute's definition
        self.name = None  # @aj(name=firstName)
        self.primary_email = None  # @aj(name=email)

@AJson()
class Restaurant:
    customer_list: List[Customer]  # if we want to have nested objects, we need to define the types hints
    '''
        @aj(name=customers)
        we can create the @aj annotation in the attribute's definition
    '''
    owner: str = "John Smith"
    location: Optional[str] = None
        

restaurant_str = '''
{
    "location": "Spain",
    "customers": [
        {"firstName": "Dani", "email": "dani@something.com"},
        {"firstName": "Mike", "email": "maki@something.com"}
    ]
}
'''

serializer = ASerializer()
restaurant = serializer.unserialize(restaurant_str, Restaurant)
print(restaurant.owner)  # "John Smith"
print(restaurant.customer_list[0].name)  # "Dani"
```

###### Known Limitations

1. Unserialize a Dict with types (Dict[str:MyObject]) is not supported, it will just unserialize it as a dict.

2. Unserialize a Dict with key different than a string (Dict[int:str])

3. Properties serialization is not supported yet.
 
#### Documentation

Documentation and additional information is available [here](https://jorgegarciairazabal.github.io/ajson/)

#### Contributing

Any contribution, feature request, or bug report is always welcome.

Please, feel free to create any issues or PRs. 