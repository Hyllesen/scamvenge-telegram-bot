"""
Database module for managing processed stores with fuzzy duplicate detection.
"""
import sqlite3
import re
from datetime import datetime
from typing import Optional, Tuple
from rapidfuzz import fuzz
from .exceptions import DatabaseError


class StoreDatabase:
    """Manages SQLite database for tracking processed stores."""
    
    FUZZY_THRESHOLD = 90  # 90% similarity for fuzzy matching
    
    def __init__(self, db_path: str):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            raise DatabaseError(f"Failed to connect to database: {e}")
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_stores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_name TEXT NOT NULL,
                    normalized_name TEXT NOT NULL,
                    original_message_id INTEGER,
                    forwarded_message_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_normalized_name 
                ON processed_stores(normalized_name)
            """)
            
            self.conn.commit()
        except Exception as e:
            raise DatabaseError(f"Failed to create tables: {e}")
    
    @staticmethod
    def normalize_for_db(text: str) -> str:
        """
        Normalize text for database storage and comparison.
        
        Args:
            text: Raw store name
            
        Returns:
            Normalized string (lowercase, no special chars)
        """
        # Convert to lowercase
        text = text.lower()
        # Remove special characters except spaces
        text = re.sub(r'[^a-z0-9\s]', '', text)
        # Collapse multiple spaces to single space
        text = re.sub(r'\s+', ' ', text)
        # Strip
        text = text.strip()
        return text
    
    def is_duplicate(self, store_name: str) -> Tuple[bool, Optional[str]]:
        """
        Check if store name is a duplicate using fuzzy matching.
        
        Args:
            store_name: Store name to check
            
        Returns:
            Tuple of (is_duplicate, matched_name)
            - is_duplicate: True if duplicate found
            - matched_name: The existing store name that matched (or None)
        """
        try:
            normalized_input = self.normalize_for_db(store_name)
            
            cursor = self.conn.cursor()
            cursor.execute("SELECT store_name, normalized_name FROM processed_stores")
            
            for row in cursor.fetchall():
                existing_normalized = row['normalized_name']
                
                # Calculate fuzzy match ratio
                similarity = fuzz.ratio(normalized_input, existing_normalized)
                
                if similarity >= self.FUZZY_THRESHOLD:
                    return True, row['store_name']
            
            return False, None
            
        except Exception as e:
            raise DatabaseError(f"Duplicate check failed: {e}")
    
    def add_store(
        self, 
        store_name: str, 
        original_message_id: Optional[int] = None,
        forwarded_message_id: Optional[int] = None
    ) -> int:
        """
        Add a new store to the database.
        
        Args:
            store_name: Store name to add
            original_message_id: ID of original Telegram message
            forwarded_message_id: ID of forwarded Telegram message
            
        Returns:
            Row ID of inserted record
            
        Raises:
            DatabaseError: If insertion fails
        """
        try:
            normalized_name = self.normalize_for_db(store_name)
            
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO processed_stores 
                (store_name, normalized_name, original_message_id, forwarded_message_id)
                VALUES (?, ?, ?, ?)
            """, (store_name, normalized_name, original_message_id, forwarded_message_id))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"Failed to add store: {e}")
    
    def get_stats(self) -> dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with stats (total_stores, etc.)
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM processed_stores")
            count = cursor.fetchone()['count']
            
            return {
                'total_stores': count
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get stats: {e}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
