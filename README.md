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
from ajson import AJson
from ajson.aserializer import ASerializer

@AJson()
class Restaurant:
    def __init__(self):
        self.location = "Manhattan"  # @aj{"groups": ["public", "admin"]}
        self.tables = 30  # @aj{"groups": ["public", "admin"]}
        self.owner = "John Smith"  # @aj{"groups": ["admin"]}

restaurant = Restaurant()
print(ASerializer().serialize(restaurant, groups=["public"])) # {"location": "Manhattan", "tables": 30}
print(ASerializer().serialize(restaurant, groups=["admin"])) #  {"location": "Manhattan", "tables": 30, "owner": "John Smith"}
```

###### Rename Attributes With "Name"

```python
from ajson import AJson
from ajson.aserializer import ASerializer

@AJson()
class Customer:
    name: str  # @aj{"name": "firstName"}
    primary_email: str  # @aj{"name": "email"}
    last_name: str  # @aj{"name": "lastName"}
    def __init__(self):
        self.name = "John"
        self.last_name = "Smith"
        self.primary_email = "john.smith@something.com"

customer = Customer()
print(ASerializer().serialize(customer))
# {"firstName": "John", "lastName": "Smith", "email": "john.smith@something.com"}
```

###### Nested Objects With Groups And Names

```python
from ajson import AJson
from ajson.aserializer import ASerializer

@AJson()
class Customer:
    def __init__(self, name, primary_email):
        self.name = name  # @aj{"name": "firstName", "groups": ["public"]}
        self.primary_email = primary_email
        '''
        You can also add the annotation in a multiline docstr
        @aj{
            "name": "email",
            "groups": ["admin"]
        }
        '''

@AJson()
class Restaurant:
    def __init__(self):
        self.location = None  # @aj{"groups": ["public", "admin"]}
        self.owner = "John Smith"  # @aj{"groups": ["admin"]}
        self.customer_list = [ # @aj{"groups": ["with_customers"], "name": "customers"}
            Customer("Dani", "dani@something.com"),
            Customer("Mike", "maki@something.com")
        ]

restaurant = Restaurant()
print(ASerializer().serialize(restaurant, groups=["public"])) 
# {"location": null, "tables": 30}

# if you want to get the dictionary instead of a string, you can call `to_dict` instead of `serialize`
print(ASerializer().to_dict(restaurant, groups=["public", "with_customers"]))
'''
{
    "location": "Spain",
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
from ajson import AJson
from ajson.aserializer import ASerializer

@AJson()
class Customer:
    name: str  # @aj{"name": "firstName"}
    primary_email: str  # @aj{"name": "email"}
    last_name: str  # @aj{"name": "lastName"}

serialize_str = '{"firstName": "John", "lastName": "Smith", "email": "john.smith@something.com"}'
customer = ASerializer().unserialize(serialize_str, Customer)
print(customer.name)  # "John"
print(customer.last_name)  # "Smith"
print(customer.primary_email)  # "john.smith@something.com"
```

###### Nested Objects

```python
from typing import List
from ajson import AJson
from ajson.aserializer import ASerializer


@AJson()
class Customer:
    def __init__(self):
        self.name = None  # @aj{"name": "firstName"}
        self.primary_email = None  # @aj{"name": "email"}

@AJson()
class Restaurant:
    customer_list: List[Customer]  # if we want to have nested objects, we need to define the types with the annotations
    '''
        @aj{"name": "customers"}
        we can create the @aj annotation in the attribute  definition
    '''
    owner: str
    location: str

    def __init__(self):
        self.location = None
        self.owner = "John Smith"
        self.customer_list = []

restaurant_str = '''
{
    "location": "Spain",
    "customers": [
        {"firstName": "Dani", "email": "dani@something.com"},
        {"firstName": "Mike", "email": "maki@something.com"}
    ]
}
'''

restaurant = ASerializer().unserialize(restaurant_str, Restaurant)
print(restaurant.owner)  # "John Smith"
print(restaurant.customer_list[0].name)  # "Dani"
```

