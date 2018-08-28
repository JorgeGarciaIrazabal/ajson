
Serialize Examples
==================

Simple Serialization With "Groups"
----------------------------------
If you want to filter some sensible data in some scenarios, you can define `groups` per each attribute to control what is serialize and what is not

.. code-block:: python

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


Rename Attributes With "Name"
-----------------------------

.. code-block:: python

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


Nested Objects With Groups And Names
------------------------------------
.. code-block:: python

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

Unserialize Examples
====================

Unserialization With Custom Names
---------------------------------

.. code-block:: python

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

Nested Objects
--------------

.. code-block:: python

    from typing import List
    from ajson import AJson, ASerializer

    @AJson()
    class Customer:
        def __init__(self):
            # we can also create the @aj annotation in the attribute's definition
            self.name = None  # @aj(name=firstName)
            self.primary_email = None  # @aj(name=email)

    @AJson()
    class Restaurant:
        customer_list: List[Customer]  # if we want to have nested objects, we need to define the types with the annotations
        '''
            @aj(name=customers)
            we can create the @aj annotation in the attribute's definition
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

    serializer = ASerializer()
    restaurant = serializer.unserialize(restaurant_str, Restaurant)
    print(restaurant.owner)  # "John Smith"
    print(restaurant.customer_list[0].name)  # "Dani"


Validate Json
-------------

.. code-block:: python

    from ajson import AJson, ASerializer

    @AJson()
    class Customer:
        name: str  # @aj(name=firstName required)
        primary_email: str  # @aj(name=email required)
        last_name: str  # @aj(name=lastName)

    serializer = ASerializer()
    serialize_str = '{"firstName": "John", "lastName": "Smith", "email": "john.smith@something.com"}'
    customer = serializer.unserialize(serialize_str, Customer)
    # it si successfully constructed as all the required attributes are provided
    serialize_str = '{"lastName": "Smith", "email": "john.smith@something.com"}'
    customer = serializer.unserialize(serialize_str, Customer)
    # AJsonEmptyRequiredAttributeError is raised as `firstName` is not provided
    serialize_str = '{"firstName": "John", "lastName": "Smith", "email": null}'
    customer = serializer.unserialize(serialize_str, Customer)
    # AJsonEmptyRequiredAttributeError is raised even in the value of the required attribute is null