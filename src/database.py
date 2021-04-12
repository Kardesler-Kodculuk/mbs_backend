"""
This module contains functions and classes that connect to the
    database.
"""
from psycopg2 import connect, cursor, connection



global_query_handler = QueryHandler()  # Declaring it in global will let flask threads handle this.


class QueryHandler:
    def __init__(self):
        self.connection: connection = connect(host="localhost", database="test",
                                              user="test", password="test")
        self.cursor: cursor = self.connection.cursor()  # Get the cursor.


class DatabaseObject:
    def __init__(self, *args, **kwargs):
        
        

