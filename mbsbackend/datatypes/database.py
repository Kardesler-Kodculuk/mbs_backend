"""
This module contains functions and classes that connect to the
    database.
"""
from abc import abstractmethod, ABC
from os import getenv, remove
from os.path import exists
import sqlite3
from typing import Optional, Any, Dict, List, Union
from dataclasses import is_dataclass
from threading import Lock


class QueryHandler(ABC):
    """
    Class that encapsulates queries to the underlying
        DBMS.
    """
    def __init__(self, conn: Union[sqlite3.Connection], cur: Union[sqlite3.Cursor], lock_for_access):
        """
        If lock_for_access is set to True, lock the database before making
            any changes.
        """
        self.connection = conn
        self.cursor = cur
        self.should_lock = lock_for_access
        self.lock = Lock()

    def execute_query(self, query: str) -> Optional[list]:
        """
        Given a query to execute, execute to query, if
            the query is a SELECT query, fetch the results
            and return them.

        :param query: Query to execute.
        :return The results of the fetch statement,
            or None.
        """
        return_value = None
        if self.should_lock:
            self.lock.acquire()
        try:
            self.cursor.execute(query)
            if "select" in query.lower():  # If this is a select query.
                return_value = self.cursor.fetchall()  # Fetch and return the results.
            self.connection.commit()  # Otherwise commit the results.
        finally:
            if self.should_lock:
                self.lock.release()
        return return_value

    @property
    @abstractmethod
    def last_inserted_row_id(self) -> int:
        """
        Get the ID of the last inserted row.

        :return ID of the last inserted row.
        """
        pass


class TestQueryHandler(QueryHandler):
    """
    Class that handles queries in the testing environment.
    """
    def __init__(self, db_name) -> None:
        self.db_name = db_name
        is_init = exists(db_name)  # Check if the database was initialised.
        conn: sqlite3.Connection = sqlite3.connect(db_name, check_same_thread=False)
        cur: sqlite3.Cursor = conn.cursor()
        if not is_init:  # If the database was not previously initalised.
            with open("init_test_database.sql") as script_f:  # Initialise the database.
                cur.executescript(script_f.read())
        super().__init__(conn, cur, True)  # Locks are necessary for SQLite databases.

    def reset_database(self) -> None:
        """
        Reset the database to its original state.
        """
        self.lock.acquire()
        self.connection.close()
        remove(self.db_name)  # Remove the file.
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)  # Reconnect.
        self.cursor = self.connection.cursor()
        with open('init_test_database.sql') as script_f:
            self.cursor.executescript(script_f.read())  # Reinitialise the database.
        self.lock.release()  # Release the lock.

    def last_inserted_row_id(self) -> int:
        return self.cursor.lastrowid


global_query_handler = TestQueryHandler(getenv('FLASK_DB_NAME', 'mbs.db'))  # Declaring it in global will let flask threads handle this.


def _stringfy(value: Any) -> str:
    """
    Convert a given object to a string ready to
        be used in a set or values clause.

    :param value Any object.
    :return Stringified version of the object, for
        string values this is just ' added to the both
        sides, otherwise no change.
    """
    if value is None:
        return "NULL"
    elif isinstance(value, str):
        value = f"'{value}'"  # Add the appropriate quotes.
    return str(value)

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


def _generate_unique_fields(class_: type, inheritance_tree: Dict[type, List[str]]) -> List[str]:
    """
    Generate a list of fields unique to this class that it did not inherit
        from its parent dataclasses.

    :param class_: Class to calculate this information for.
    :param inheritance_tree: Inheritance table generated for this class.
    :return the list of fields unique to this class.
    """
    assert is_dataclass(class_)
    fields = class_.__dataclass_fields__.keys()  # Get the fields, unique ones and ones that are inherited.
    super_fields = []
    for super_fields_ in inheritance_tree.values():  # Get all the fields in the superclasses.
        super_fields.extend(super_fields_)  # And consolidate them into a single list.
    fields = [*filter(lambda field: field not in super_fields, fields)]  # Then compare them against our fields.
    return fields  # Remaining ones are the unique fields.


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
    dataclass_ancestors = [ancestor for ancestor in ancestors if is_dataclass(ancestor) and hasattr(ancestor, "_table_name") and ancestor.__name__ != class_.__name__]
    for ancestor in dataclass_ancestors:
        # All the dataclass ancestors of the
        # descendant must also be database bound.
        fields_ = list(ancestor.__dataclass_fields__.keys())  # Get the names of the fields
        # Fields specific to a descendant class are fields that are not found in the parent class(es).
        fields[ancestor] = [field for field in fields_ if field not in parent_fields]
        parent_fields = fields_.copy()  # Save the original field list to the latest parent field list.
    return fields


def bind_database(obj_id_row: str):
    """
    When decorating a dataclass, this decorator mutates the behaviour of the dataclass
        in the following ways:

        1) Adds the fetch (class) method to the dataclass, this static factory method queries
            the database and returns the object with the given id. This also has a fetch_where
            variant.
        2) Adds the has (class) method to the dataclass, which can be used to check if a specific
            entity exists. This also has a has_where variant.
        3) Adds the update method, which automatically updates the contents of the
            bound database object.
        4) Adds the create method, which creates an object with the given id and
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
        inheritance_ = _generate_inheritance_tree(dataclass_)
        unique_ = _generate_unique_fields(dataclass_, inheritance_)
        tab_name = dataclass_.__name__

        class DatabaseBound(dataclass_):
            """
            Represents a class that is bound dynamically to a database
                record, this database is determined by the global_query_handler.
            """
            _table_inheritance = inheritance_  # Generate the inheritance tree.
            _unique_fields = unique_  # Fields unique to this class.
            _table_name = tab_name  # Construct the table_name.
            _obj_id_row = obj_id_row  # The first field is also the ID.

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
                    type_: {key: value for key, value in changed_fields.items() if key in self._table_inheritance[type_]}
                    for type_ in self._table_inheritance.keys()
                }  # Partition the fields according to which parent they appear in.
                partitioned_changed_fields[self.__class__] = {key: value for key, value in changed_fields.items() if key in self._unique_fields}
                # We also added the fields unique to this class.
                return partitioned_changed_fields

            def __setattr__(self, key, value):
                """
                Cache the attributes being set before setting them.
                """
                if "_changed_fields" not in self.__dict__:
                    self.__dict__["_changed_fields"] = {}
                self.__dict__["_changed_fields"][key] = value  # Add it to a dictionary of updated names.
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
                    alteration_tuple = tuple((row_name, _stringfy(value))
                                             for row_name, value in alterations.items()) # Generate a tuple of pairs
                    # that denote changes in the fields with their new values.
                    # Generate the set clause.
                    set_clause = ', '.join(f"{row_name} = {value}" for row_name, value in alteration_tuple)
                    # Update the object.
                    global_query_handler.execute_query(f"UPDATE {type_._table_name}"
                                                       f" SET {set_clause}"
                                                       f" WHERE {type_._obj_id_row} = {self.__getattribute__(self._obj_id_row)}")
                self._changed_fields.clear()  # Reset the changed fields.

            @classmethod
            def has(cls, object_id: int) -> bool:
                """
                Check if the bound table of this dataclass has a record
                    with the given object id.

                :param object_id: Object Identifer to check.
                :return True if such a record exists, otherwise False.
                """
                where_clause = f"{cls._obj_id_row} = {object_id}"
                query = f"SELECT * FROM {cls._table_name} WHERE {where_clause}"
                if len(global_query_handler.execute_query(query)) > 0:
                    return True
                return False

            @classmethod
            def has_where(cls, criteria: str, value: Any) -> bool:
                """
                Check if the bound table of this dataclass has a record
                    with the given search criteria

                :param criteria: Criteria to check, the name of the column.
                :param value: Value of the column that should be matched.
                :return True if there is such a record, or False otherwise,
                    (including when criteria column does not exist at all.)
                """
                where_clause = f"{criteria} = {value}"
                query = f"SELECT * FROM {cls._table_name} WHERE {where_clause}"
                try:
                    if len(cls.fetch_where(criteria, value)) > 0:
                        return True
                    return False
                except TypeError:
                    return False

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
                where_clause = f"{cls._obj_id_row} = {object_id}"
                query = f"SELECT * FROM {cls._table_name} WHERE {where_clause}"
                values.extend(*global_query_handler.execute_query(query))
                for type_ in cls._table_inheritance:  # For each antecedent dataclass type, query the database for values.
                    where_clause = f"{type_._obj_id_row} = {object_id}"
                    values = [*global_query_handler.execute_query(f"SELECT * FROM {type_._table_name} WHERE {where_clause}")[0]] + values  # Add the superclass attributes to the end.
                return cls(*values)  # Initialise an object with these args.

            @classmethod
            def fetch_where(cls, criteria: str, value: Any) -> List["DatabaseBound"]:
                """
                Get members of this class (if any) according to the given
                    criteria.

                :param criteria: Column name by whose value to results will
                    be filtered.
                :param value: Value of the column name.
                :return A list of database bound class instances, possibly
                    empty, that fit the criteria given.
                """
                object_ids: List[int] = []  # This is where ids of the objects will go.
                if criteria in cls._unique_fields:
                    query = f"SELECT {cls._obj_id_row} FROM {cls._table_name}" \
                            f" WHERE {criteria} = " + _stringfy(value)
                    matches = global_query_handler.execute_query(query)
                    if matches:  # Check if there are any matches with the given criteria.
                        object_ids.extend([match[0] for match in matches])   # Extend the object_ids if there are any matches.
                    return [cls.fetch(object_id) for object_id in object_ids]  # Return all objects that fit this category.

                for type_ in cls._table_inheritance: # It is probable that the criteria is not within this
                    # Class directly but in one of its parent classes, we need to check them all.
                    if criteria in cls._table_inheritance[type_]:  # If the criteria is in this table.
                        # If criteria appears at last in this parent type, query this parent type.
                        matches = global_query_handler.execute_query(f"SELECT {type_._obj_id_row}"
                                                                     f" FROM {type_._table_name}"
                                                                     f" WHERE {criteria} = {_stringfy(value)}")
                        object_ids.extend([match[0] for match in matches])
                        break  # And exit loop.
                return [cls.fetch(object_id) for object_id in object_ids if cls.has(object_id)]  # Return all objects that fit this category that intersect with our child class.

            def create(self) -> None:
                """
                Insert this object to the bound database. This method only works
                    on DataBound objects that have no superclasses in the database.
                    Superclasses should be created separately.
                """
                fields = unique_.copy()
                fields.remove(self._obj_id_row)  # This is generated automatically.
                values = [_stringfy(getattr(self, field)) for field in fields]  # Get the values in the same order.
                rows_clause = '(' + ', '.join(fields) + ')'
                values_clause = '(' + ', '.join(values) + ')'
                global_query_handler.execute_query(f"INSERT INTO {self._table_name}"
                                                   f" {rows_clause} VALUES {values_clause}")
                setattr(self, self._obj_id_row, global_query_handler.last_inserted_row_id())  # Set the id correctly.

            @classmethod
            def create_unique(cls, values: list) -> "DatabaseBound":
                """
                Create a class given all the info including the ID row. Where ID row is the first member.
                """
                fields = unique_.copy()
                rows_clause = '(' + ', '.join(fields) + ')'
                values_clause = '(' + ', '.join(_stringfy(value) for value in values) + ')'
                global_query_handler.execute_query(f"INSERT INTO {cls._table_name}"
                                                   f" {rows_clause} VALUES {values_clause}")
                return cls.fetch(values[0])

            def delete(self) -> None:
                """
                Delete this object from the bound database. This only works
                    on DataBound objects that have no superclasses in the
                    database.
                """
                global_query_handler.execute_query(f"DELETE FROM {self._table_name} WHERE {self._obj_id_row} = {getattr(self, self._obj_id_row)}")
        return DatabaseBound
    return wrapper


