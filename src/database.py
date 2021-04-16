"""
This module contains functions and classes that connect to the
    database.
"""
from psycopg2.extensions import cursor, connection
from psycopg2 import connect
from typing import Optional, Tuple, Callable, Any
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


def _cached_set_attr(set_attr: Callable):
    """
    Cached version of the set_attr method found in Python classes, this version
        decorates the __set_attr__ magic method of classes decorated with the
        bind_database decorator.

    :param object_: An object who is an instance of a class decorated
        with bind_database.
    :param set_attr: Set_attr method of the said object.
    :return a new set_attr method that caches the updated values.
    """
    def cached_set_attr(self, name, value):
        """
        When setting an attribute, cache it to a dictionary,
            this way, when the .update method is called,
            we can only alter the updated fields.

        :param self: reference to the calling object.
        :param name: Name of the field being updated.
        :param value: Value being updated.
        """
        self.changed_fields[name] = value  # Add it to a dictionary of updated names.
        set_attr(self, name, value)  # Call the original set_attr.
    return cached_set_attr


def _update(self: Any) -> None:
    """
    Update method for the classes decorated with the bind_database,
        updates the bound record of the class in the bound database.

    :param self: Reference to the object itself.
    """
    # Get the alterations made to the object since the last update.
    alterations: dict[str, Any] = self._changed_fields
    # Convert it into a tuple of row names and values.
    alteration_tuple = (_convert_case(row_name), _stringfy(value) for row_name, value in alterations.items())
    # Generate the set clause.
    set_clause = ' '.join(f"{row_name} = {value}" for row_name, value in alteration_tuple)
    # Update the object.
    global_query_handler.execute_query(f"UPDATE {self._table_name}"
                                       f"SET {set_clause}"
                                       f"WHERE {self.obj_id_row} = {getattr(self, self.obj_id_row)}")
    self._changed_fields.clear()  # Reset the changed fields.


def bind_database(dataclass_: type) -> Callable:
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

    :param dataclass_: Dataclass to decorate with.
    :return the wrapper function that mutates the dataclass.
    """
    if not is_dataclass(dataclass_):  # Decorated classes must be dataclasses.
        raise TypeError("Class decorated with bind_database is not a dataclass.")

    def wrapper(obj_id) -> None:
        """
        Set to the name of the object id.
        """
        dataclass_._table_name = dataclass_.__name__  # Construct the table_name.
        dataclass_.changed_fields = {}  # Create a dictionary record changed field values over object lifetime.
        dataclass_.update = _update  # Add the update method.
        dataclass_.obj_id_row = _convert_case(obj_id)  # Get the name of the object_id row.
        dataclass_.__setattr__ = _cached_set_attr(dataclass_.__setattr__)  # Decorate the __setattr__ magic method.
    return wrapper


