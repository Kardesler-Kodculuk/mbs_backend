"""
This module contains functions and classes that connect to the
    database.
"""
from psycopg2.extensions import cursor, connection
from psycopg2 import connect
from typing import Optional, Tuple, Callable, Any, Dict, List
from dataclasses import is_dataclass
from re import compile


class QueryHandler:
    """
    Class that encapsulates queries to the underlying
        DBMS.
    """
    def __init__(self) -> None:
        self.connection: connection = connect(host="localhost", database="test",
                                              user="test", password="test")
        self.cursor: cursor = self.connection.cursor()  # Get the cursor.

    def execute_query(self, query: str) -> Optional[tuple]:
        """
        Given a query to execute, execute to query, if
            the query is a SELECT query, fetch the results
            and return them.
        
        :param query: Query to execute.
        :return The results of the fetch statement,
            or None.
        """
        self.cursor.execute(query)
        if "select" in query.lower():  # If this is a select query.
            return self.cursor.fetchall()  # Fetch and return the results.
        else:
            self.connection.commit()  # Otherwise commit the results.
 

global_query_handler = QueryHandler()  # Declaring it in global will let flask threads handle this.



snake_case = compile(r"[[:<:]][a-z]|(?<=_)[a-z]")  # This pattern captures letters to convert into uppercase.


def _convert_case(field_name: str) -> str:
    """
    Given a field name, convert it from snake_case (PEP8 standard
        naming convention) into CamelCase (used in our database).

    :param field_name: field name in snake_case.
    :return the converted CamelCase row name.
    """
    #  Replace the lowercase letters that should be replaced, for reference,
    #   this usage of the sub can be seen in: https://stackoverflow.com/a/8934655/6663851
    row_name = snake_case.sub(lambda match: match.group(1).upper(), field_name)
    row_name = row_name.replace('_', '')  # Get rid of the _ character as well.
    return row_name


def _stringfy(value: Any) -> str:
    """
    Convert a given object to a string ready to
        be used in a set or values clause.

    :param value Any object.
    :return Stringified version of the object, for
        string values this is just ' added to the both
        sides, otherwise no change.
    """
    if isinstance(value, str):
        value = f"'{value}'"  # Add the appropriate quotes.
    return value


"""
Below is the main functions that deal with the connection between
    classes and their database bindings, upon reviewing this section
    one may have several questions, so I wanted to address them.
    
* Why decorators?
Since the original classes are dataclasses, binding them
    to a database using superclasses does not work, as the
    __init__ method of the superclass is simply not called
    in dataclasses, another approach might have been to use
    metaclasses, but those would be complex, and frankly
    my experience with them is close to nonexistent.

* How to use these?
When a dataclass is decorated with the @database_bind decorator,
    this dataclass and its instances act just like their normal
    counterparts, with three additional methods, more information
    can be found in the database_bind below.

Finally, I would like to mention that this approach is similar to:
    https://github.com/ambertide/datalite
"""


def _generate_inheritance_tree(class_: type) -> Dict[type, List[str]]:
    """
    Given a dataclass categorise its field names based on which superclass
        they belong to originally. (ie, a dictionary of classes and the
        field names that appear for the first time in that class.)

    :param class_: The dataclass to start untangling.
    :return a dictionary of classes and their unique fields.
    """
    parent_fields = []
    fields: Dict[type, List[str]] = {}
    ancestors = class_.mro()  # Get the ancestor types of the dataclass.
    ancestors.reverse()  # Reverse to the eldest-first.
    dataclass_ancestors = [ancestor for ancestor in ancestors if is_dataclass(ancestor)]
    for ancestor in dataclass_ancestors:
        # All the dataclass ancestors of the
        # descendant must also be database bound.
        fields_ = list(ancestor.__dataclass_fields__.keys())  # Get the names of the fields
        # Fields specific to a descendant class are fields that are not found in the parent class(es).
        fields[ancestor.__class__] = [field for field in fields_ if field not in parent_fields]
        parent_fields = fields_.copy()  # Save the original field list to the latest parent field list.
    return fields


def bind_database(obj_id_row: str):
    """
    When decorating a dataclass, this decorator mutates the behaviour of the dataclass
        in the following ways:

        1) Adds the get method to the dataclass, this static factory method queries
            the database and returns the object with the given id.
        2) Adds the update method, which automatically updates the contents of the
            bound database object.
        3) Adds the create method, which creates an object with the given id and
            row information.

    In order to bind the dataclass to the database, the database defined in the
        QueryHandler must already be instantiated and its schemas must be set up,
        furthermore the names of the dataclass fields must be equal to the names
        in the database *except* their naming convention which must be snake case,
        as per PEP8.

    :param obj_id_row: The name of the field that holds
            the object id in the database.
    :return the wrapper function that mutates the dataclass.
    """
    def wrapper(dataclass_: type) -> type:
        """
        Wrapper function to get the decorator
            arguments.

        :param dataclass_: Dataclass to decorate with.
        """
        if not is_dataclass(dataclass_):  # Decorated classes must be dataclasses.
            raise TypeError("Class decorated with bind_database is not a dataclass.")

        class DatabaseBound(dataclass_):
            """
            Represents a class that is bound dynamically to a database
                record, this database is determined by the global_query_handler.
            """
            _table_inheritance = _generate_inheritance_tree(dataclass_.__class__)  # Generate the inheritance tree.
            _changed_fields = {}  # Create a dictionary record changed field values over object lifetime.
            _table_name = dataclass_.__class__.__name__  # Construct the table_name.
            _obj_id_row = _convert_case(obj_id_row)  # The first field is also the ID.

            def _partition_changed_fields(self: "DatabaseBound") -> Dict["DatabaseBound", Dict["DatabaseBound", Any]]:
                """
                Given an instance of a database bound dataclass, categorise its
                    updated variables cache into subdictionaries corresponding
                    to ancestor classes that own the field (for the first time).
                For instance, if class B with fields a, b extends class A with
                    field a such that B's a comes from A, and if A and B are
                    database bound dataclasses, an instance of A whose a and b
                    values are changed will return this dictionary:
                    {A: {'a': 'new_value'}, B: {'b': 'new_value'}} when
                    given as an input to this function.

                :param self: An instance of a database bound dataclass.
                :return a dictionary of types to update dictionaries that partition
                    the update cache based on parents owning the fields.
                """
                changed_fields: Dict[str, Any] = self._changed_fields
                partitioned_changed_fields = {
                    type_: {key: value for key, value in changed_fields if key in self._table_inheritance[type_]}
                    for type_ in self._table_inheritance.keys()
                }  # Partition the fields according to which parent they appear in.
                return partitioned_changed_fields

            def __setattr__(self, key, value):
                """
                Cache the attributes being set before setting them.
                """
                self.__dict__["changed_fields"][key] = value  # Add it to a dictionary of updated names.
                self.__dict__[key] = value

            def update(self) -> None:
                """
                Update method for the classes decorated with the bind_database,
                    updates the bound record of the class in the bound database.

                :param self: Reference to the object itself.
                """
                # Get the alterations made to the object since the last update.
                # Convert it into a tuple of row names and values.
                alterations_per_type = self._partition_changed_fields()
                for type_ in alterations_per_type:  # For each alteration per table
                    alterations = alterations_per_type[type_]  # Get the alterations dictionary for this table.
                    alteration_tuple = tuple((_convert_case(row_name), _stringfy(value))
                                             for row_name, value in alterations.items()) # Generate a tuple of pairs
                    # that denote changes in the fields with their new values.
                    # Generate the set clause.
                    set_clause = ' '.join(f"{row_name} = {value}" for row_name, value in alteration_tuple)
                    # Update the object.
                    global_query_handler.execute_query(f"UPDATE {type_._table_name}"
                                                       f"SET {set_clause}"
                                                       f"WHERE {type_.obj_id_row} = {self.__getattribute__(obj_id_row)}")
                self._changed_fields.clear()  # Reset the changed fields.

            @classmethod
            def fetch(cls, object_id: int) -> "DatabaseBound":
                """
                Get a member of this class with the given object_id.

                :param object_id Unique identifier of the record
                    in the database.
                :return the object whose data is drawn from the
                    record with the given object_id.
                """
                values = []  # Values that will be used to initialise the object.
                for type_ in cls._table_inheritance:  # For each antecedent dataclass type, query the database for values.
                    where_clause = f"{type_._obj_id_row} = {object_id}"
                    values.extend(*global_query_handler.execute_query(f"SELECT * FROM {type_._table_name}"
                                                                      f" WHERE {where_clause}"))
                return cls.__init__(*values)  # Initialise an object with these args.

            def create(self) -> None:
                """
                Insert this object to the bound database.
                """
                for type_ in self._table_inheritance:  # For each antecendent dataclass type,
                    rows = self._table_inheritance[type_]  # Get the row names.
                    field_values = [_stringfy(self.__getattribute__(_convert_case(row))) for row in rows]  # Get the values
                    row_clause = ', '.join(rows)
                    values_clause = ', '.join(field_values)
                    global_query_handler.execute_query(f"INSERT INTO {type_._table_name}({row_clause})"
                                                       f" WHERE VALUES({values_clause})")
                    # And insert the record one by one starting from the most antecedent parent.
        return DatabaseBound
    return wrapper


