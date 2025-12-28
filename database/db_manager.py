"""
Database manager for handling MySQL connections and queries.
"""
import logging
import mysql.connector
from mysql.connector import Error, pooling
from typing import Optional, List, Dict, Any, Tuple
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database connections, queries, and transactions for the application.
    Uses connection pooling for efficient database access.
    """
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the database manager."""
        if self._pool is None:
            self._create_pool()
    
    def _create_pool(self):
        """
        Create a connection pool for database connections.
        """
        try:
            db_config = Config.get_db_config()
            self._pool = pooling.MySQLConnectionPool(
                pool_name="pim_pool",
                pool_size=5,
                pool_reset_session=True,
                **db_config
            )
            logger.info("Database connection pool created successfully")
        except Error as e:
            logger.error(f"Error creating connection pool: {e}")
            raise
    
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Returns:
            mysql.connector.connection.MySQLConnection: Database connection
        
        Raises:
            Error: If unable to get connection from pool
        """
        try:
            return self._pool.get_connection()
        except Error as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[Tuple] = None, fetch: bool = False) -> Optional[List[Dict[str, Any]]]:
        """
        Execute a SQL query with parameters (prevents SQL injection).
        
        Args:
            query: SQL query string with %s placeholders for parameters
            params: Tuple of parameters to substitute in query
            fetch: Whether to fetch and return results
        
        Returns:
            List of dictionaries representing rows if fetch=True, None otherwise
        
        Raises:
            Error: If query execution fails
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                results = cursor.fetchall()
                return results
            else:
                connection.commit()
                return None
                
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_insert(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Execute an INSERT query and return the last inserted ID.
        
        Args:
            query: SQL INSERT query
            params: Query parameters
        
        Returns:
            int: Last inserted row ID
        
        Raises:
            Error: If insert fails
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            connection.commit()
            return cursor.lastrowid
            
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error executing insert: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute a query multiple times with different parameters (bulk insert/update).
        
        Args:
            query: SQL query
            params_list: List of parameter tuples
        
        Returns:
            int: Number of affected rows
        
        Raises:
            Error: If execution fails
        """
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.executemany(query, params_list)
            connection.commit()
            return cursor.rowcount
            
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Error executing many: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def begin_transaction(self):
        """
        Start a new transaction.
        
        Returns:
            mysql.connector.connection.MySQLConnection: Connection with transaction started
        """
        connection = self.get_connection()
        connection.start_transaction()
        return connection
    
    def commit_transaction(self, connection):
        """
        Commit a transaction.
        
        Args:
            connection: Database connection with active transaction
        """
        try:
            connection.commit()
        except Error as e:
            logger.error(f"Error committing transaction: {e}")
            raise
        finally:
            connection.close()
    
    def rollback_transaction(self, connection):
        """
        Rollback a transaction.
        
        Args:
            connection: Database connection with active transaction
        """
        try:
            connection.rollback()
        except Error as e:
            logger.error(f"Error rolling back transaction: {e}")
        finally:
            connection.close()
    
    def test_connection(self) -> bool:
        """
        Test the database connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            connection.close()
            logger.info("Database connection test successful")
            return True
        except Error as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def close_pool(self):
        """Close all connections in the pool."""
        if self._pool:
            # Note: mysql.connector.pooling doesn't have a close_all method
            # Connections will be closed when they're garbage collected
            self._pool = None
            logger.info("Database connection pool closed")
