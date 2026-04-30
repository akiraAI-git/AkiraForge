#!/usr/bin/env python3
"""
Database Connection Pooling
=============================

Implements connection pooling for MySQL to improve performance
and prevent connection exhaustion.

Features:
  - Connection pool management
  - Automatic reconnection on failure
  - Configurable pool size
  - Retry logic with exponential backoff
  - Thread-safe operations
"""

import os
import pymysql
import logging
from pathlib import Path
import threading
import time
from typing import Optional
from queue import Queue, Empty

logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    """Manages a pool of database connections."""
    
    def __init__(self, pool_size=5, max_retries=3, retry_delay=1):
        """
        Initialize connection pool.
        
        Args:
            pool_size: Maximum number of connections to maintain
            max_retries: Maximum number of retry attempts
            retry_delay: Initial retry delay in seconds (exponential backoff)
        """
        self.pool_size = pool_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self.connection_params = self._get_connection_params()
        
        # Validate configuration
        self._validate_configuration()
        
        # Initialize pool with connections
        self._initialize_pool()
        logger.info(f"Database connection pool initialized: {pool_size} connections, {max_retries} retries")
    
    def _validate_configuration(self):
        """Validate database configuration."""
        if not self.connection_params.get('host'):
            logger.error("DB_HOST not configured")
        if not self.connection_params.get('user'):
            logger.error("DB_USER not configured")
        if not self.connection_params.get('database'):
            logger.error("DB_NAME not configured")
        
        logger.debug(f"Database config: {self.connection_params['host']}@{self.connection_params['user']}")
    
    def _get_connection_params(self):
        """Get database connection parameters from environment."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'akiraforge'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'akiraforge'),
            'charset': 'utf8mb4',
            'autocommit': False
        }
    
    def _initialize_pool(self):
        """Initialize pool with fresh connections."""
        try:
            for i in range(self.pool_size):
                try:
                    conn = pymysql.connect(**self.connection_params)
                    self.pool.put(conn, block=False)
                except Exception as e:
                    logger.warning(f"Failed to initialize connection {i+1}/{self.pool_size}: {e}")
            
            available = self.pool.qsize()
            logger.info(f"Pool initialized with {available}/{self.pool_size} connections")
        except Exception as e:
            logger.error(f"Error initializing pool: {e}")
    
    def _create_connection(self):
        """Create a single database connection with retry logic."""
        delay = self.retry_delay
        
        for attempt in range(self.max_retries):
            try:
                conn = pymysql.connect(**self.connection_params)
                logger.debug(f"Connection created on attempt {attempt + 1}")
                return conn
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                    logger.debug(f"Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to connect after {self.max_retries} attempts: {e}")
                    raise
    
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Returns:
            Database connection
            
        Raises:
            Exception if unable to get connection
        """
        try:
            # Try to get existing connection from pool
            conn = self.pool.get(block=False)
            
            # Verify connection is still alive
            if not self._verify_connection(conn):
                conn.close()
                conn = self._create_connection()
            
            return conn
        
        except Empty:
            # Pool is empty, create new connection
            return self._create_connection()
    
    def _verify_connection(self, conn) -> bool:
        """Verify connection is still alive."""
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.debug(f"Connection verification failed: {e}")
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            return False
    
    def return_connection(self, conn):
        """
        Return a connection to the pool.
        
        Args:
            conn: Database connection to return
        """
        try:
            if self._verify_connection(conn):
                # Return to pool if it has space
                try:
                    self.pool.put(conn, block=False)
                except:
                    logger.debug("Pool full, closing connection")
                    conn.close()
            else:
                # Connection is bad, close it
                logger.debug("Bad connection closed")
                conn.close()
        except Exception as e:
            logger.error(f"Error returning connection: {e}")
    
    def close_all(self):
        """Close all connections in the pool."""
        logger.info("Closing all connections")
        while True:
            try:
                conn = self.pool.get(block=False)
                conn.close()
            except Empty:
                break
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
    
    def get_pool_stats(self) -> dict:
        """Get current pool statistics."""
        return {
            "available": self.pool.qsize(),
            "pool_size": self.pool_size,
            "max_retries": self.max_retries
        }
    
    def get_metrics(self) -> dict:
        """Get pool metrics."""
        return {
            "available_connections": self.pool.qsize(),
            "max_pool_size": self.pool_size,
            "utilization_percent": round(100 * (self.pool_size - self.pool.qsize()) / self.pool_size, 2)
        }
    
    def _get_connection_params(self):
        """Get database connection parameters from environment."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'akiraforge'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'akiraforge'),
            'charset': 'utf8mb4',
            'autocommit': False
        }
    
    def _initialize_pool(self):
        """Initialize pool with fresh connections."""
        try:
            for _ in range(self.pool_size):
                conn = pymysql.connect(**self.connection_params)
                self.pool.put(conn, block=False)
        except Exception as e:
            print(f"[DB_POOL] Warning: Could not fully initialize pool: {e}")
    
    def _create_connection(self):
        """Create a single database connection with retry logic."""
        delay = self.retry_delay
        
        for attempt in range(self.max_retries):
            try:
                conn = pymysql.connect(**self.connection_params)
                return conn
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"[DB_POOL] Connection attempt {attempt + 1} failed: {e}")
                    print(f"[DB_POOL] Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    print(f"[DB_POOL] Failed to connect after {self.max_retries} attempts")
                    raise
    
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Returns:
            Database connection
            
        Raises:
            Exception if unable to get connection
        """
        try:
            # Try to get existing connection from pool
            conn = self.pool.get(block=False)
            
            # Verify connection is still alive
            if not self._verify_connection(conn):
                conn = self._create_connection()
            
            return conn
        
        except Empty:
            # Pool is empty, create new connection
            return self._create_connection()
    
    def _verify_connection(self, conn):
        """Verify connection is still alive."""
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    def return_connection(self, conn):
        """
        Return a connection to the pool.
        
        Args:
            conn: Database connection to return
        """
        try:
            if self._verify_connection(conn):
                # Return to pool if it has space
                try:
                    self.pool.put(conn, block=False)
                except:
                    conn.close()
            else:
                # Connection is bad, close it
                conn.close()
        except Exception as e:
            print(f"[DB_POOL] Error returning connection: {e}")
    
    def close_all(self):
        """Close all connections in the pool."""
        while True:
            try:
                conn = self.pool.get(block=False)
                conn.close()
            except Empty:
                break
            except Exception as e:
                print(f"[DB_POOL] Error closing connection: {e}")
    
    def get_pool_stats(self):
        """Get current pool statistics."""
        return {
            "available": self.pool.qsize(),
            "pool_size": self.pool_size,
            "max_retries": self.max_retries
        }

# Global pool instance
_global_pool = None

def get_db_connection_pool(pool_size=5):
    """Get or create global connection pool."""
    global _global_pool
    if _global_pool is None:
        _global_pool = DatabaseConnectionPool(pool_size=pool_size)
    return _global_pool

def get_pooled_db_connection():
    """Get a connection from the pool."""
    pool = get_db_connection_pool()
    return pool.get_connection()

def return_pooled_db_connection(conn):
    """Return a connection to the pool."""
    pool = get_db_connection_pool()
    pool.return_connection(conn)
