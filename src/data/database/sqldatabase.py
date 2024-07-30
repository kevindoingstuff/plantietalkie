import sqlite3
import pandas as pd

class PlantReader:
    def __init__(self, db_path):
        """
        Initialize the SQLiteReader with the path to the SQLite database file.
        
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Connect to the SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(f"Connected to database at {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
    
    def execute_query(self, query):
        """
        Execute a SQL query and return the results.
        
        :param query: SQL query to execute.
        :return: List of tuples containing the query results.
        """
        if not self.connection:
            print("No database connection. Please call connect() first.")
            return
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            print(f"Error executing query: {query}, Error: {e}")
            return []
        finally:
            cursor.close()
    
    def read_table_as_dataframe(self, table_name):
        """
        Read a table from the database into a pandas DataFrame.
        
        :param table_name: Name of the table to read.
        :return: DataFrame containing the table data.
        """
        if not self.connection:
            print("No database connection. Please call connect() first.")
            return
        
        try:
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            print(f"Error reading table {table_name} into DataFrame: {e}")
            return pd.DataFrame()
    
    def list_tables(self):
        """
        List all tables in the SQLite database.
        
        :return: List of table names.
        """
        
        if not self.connection:
            print("No database connection. Please call connect() first.")
            return []
        
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            tables = cursor.fetchall()
            return [table[0] for table in tables]
        except sqlite3.Error as e:
            print(f"Error listing tables: {e}")
            return []
        finally:
            cursor.close()

    def query_all_tables(self):
        """
        Query all tables in the database and return a dictionary of DataFrames.
        
        :return: Dictionary with table names as keys and DataFrames as values.
        """
        if not self.connection:
            print("No database connection. Please call connect() first.")
            return {}
        
        tables = self.list_tables()
        data = {}
        for table in tables:
            data[table] = self.read_table_as_dataframe(table)
        return data
