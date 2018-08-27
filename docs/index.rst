.. AJson documentation master file, created by
   sphinx-quickstart on Sun Aug 26 19:22:11 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to AJson's documentation!
=================================

`AJson <https://github.com/JorgeGarciaIrazabal/ajson>`_ is a json serializer based on annotations, so you can easily control which and how class attributes should be serialized.

.. code-block:: python

    from ajson import AJson
    from ajson.aserializer import ASerializer

    @AJson()
    class Restaurant:
        location:str   # @aj(groups=["public", "admin"])
        tables: int  # @aj(groups=["public", "admin"])
        owner: str  # @aj(groups=["admin"], name=owner_name)
        def __init__(self, location, tables, owner):
            self.location = location
            self.tables = tables
            self.owner = owner

    serializer = ASerializer()
    restaurant = Restaurant("Manhattan", 30, "John Smith")
    print(serializer.serialize(restaurant, groups=["public"]))
    # {"location": "Manhattan", "tables": 30}
    print(serializer.serialize(restaurant, groups=["admin"]))
    #  {"location": "Manhattan", "tables": 30, "owner_name": "John Smith"}

Or unserialize.

.. code-block:: python

    from ajson import AJson
    from ajson.aserializer import ASerializer

    @AJson()
    class Customer:
        name: str  # @aj(name=firstName, required)
        last_name: str  # @aj(name=lastName)

    serializer = ASerializer()
    serialize_str = '{"firstName": "John", "lastName": "Smith"}'
    customer = ASerializer().unserialize(serialize_str, Customer)
    print(customer.name)  # "John"
    print(customer.last_name)  # "Smith"

    # Validate jsons
    # Not passing the required attribute "name
    serialize_str = '{"lastName": "Smith"}'
    customer = ASerializer().unserialize(serialize_str, Customer)
    # this will raise a `AJsonEmptyRequiredAttributeError` Exception




.. code-block:: bash

    $ pip install ajson


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   class_annotations
   aserializer




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
