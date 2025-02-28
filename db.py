import mysql.connector
from mysql.connector import Error
import logging

class Database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                self.logger.info("Successfully connected to database")
                return True
        except Error as e:
            self.logger.error(f"Error connecting to MySQL: {e}")
            return False
        
    def fetch_one(self, query, params):
        """Execute a query and return a single result."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            logging.error(f"Error executing query: {e}")
            return None

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("Database connection closed")

    def execute_query(self, query, params=None):
        """Execute a SQL query"""
        cursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor
        except Error as e:
            self.logger.error(f"Error executing query: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

if __name__ == "__main__":
    # Test database connection and table creation
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    db = Database(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
