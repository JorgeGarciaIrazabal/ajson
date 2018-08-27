
Class Annotations
=================

In order to describe how to serialize or unserialize an object, you need to describe the class attributes with simple annotations

decorator
---------
Add the `@AJson` decorator to a class to tell the serializer that this class has to be parsed for future actions

.. code-block:: python

    from ajson import AJson

    @AJson()
    class Restaurant:
        pass


Annotations
-----------

Annotations are comments next to the class attributes with the format ```@aj({param1}={value1} {param2}={value2} ... )```

.. csv-table:: Frozen Delights!
    :header: "parameter", "description", "default value", "example"
    :widths: 10, 40, 20, 25

    "name", "key used to serialized to and unserialize from", "attribute's name", "name=my_attr"
    "groups", "list of names to define which attributes should be serialized", "None", "groups=[""admin"", ""include_dates""]"
    "required", "flag used to make sure a parameter is included in a json when unserializing", "Flase", "required"
    "d_format", "datetime format dates will be serialized to and unserialized from", "%Y-%m-%dT%H:%M:%S.%f (ISO FORMAT)", "d_format=%Y-%m-%d"

Example
^^^^^^^

.. code-block:: python

    @AJson()
    class Restaurant:
        location:str   # @aj(groups=['public'], name=address, required) using inline comment
        tables_num: int
        """
            you can also use multi line comment to include the @aj annotation like this:
            @aj(groups=['public'], name="number of tables")
        """
        opening_date: datetime
        '''
            @aj(
                d_format="%Y/%m/%d %I:%M%p"
                groups="[
                    'admin',
                    'include_dates'
                ]"
            )
            Note that if you want to use a multi word value for the value of a parameter, you have to wrap it with double quotes (d_format="%Y/%m/%d %I:%M%p")

            You can even use have multi-line values if you wrap them with double quotes too.
            `
                groups="[
                    'admin',
                    'include_dates'
                ]"
            `
        '''
