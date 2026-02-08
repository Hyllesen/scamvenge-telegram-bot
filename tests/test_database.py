"""
Unit tests for the database module.
"""
import unittest
import tempfile
import os
from pathlib import Path
from src.database import StoreDatabase
from src.exceptions import DatabaseError


class TestStoreDatabase(unittest.TestCase):
    """Test the StoreDatabase class."""
    
    def setUp(self):
        """Set up test database (in-memory for speed)."""
        # Use temporary file for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = StoreDatabase(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test that database initializes correctly."""
        self.assertIsNotNone(self.db.conn)
        
        # Check that table exists
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='processed_stores'
        """)
        table = cursor.fetchone()
        self.assertIsNotNone(table)
    
    def test_normalize_for_db(self):
        """Test text normalization for database."""
        # Basic normalization
        self.assertEqual(
            StoreDatabase.normalize_for_db("Nike Store"),
            "nike store"
        )
        
        # Remove special characters
        self.assertEqual(
            StoreDatabase.normalize_for_db("Nike's Store!"),
            "nikes store"
        )
        
        # Collapse spaces
        self.assertEqual(
            StoreDatabase.normalize_for_db("The    Big   Store"),
            "the big store"
        )
        
        # Strip whitespace
        self.assertEqual(
            StoreDatabase.normalize_for_db("  Store ABC  "),
            "store abc"
        )
    
    def test_add_store(self):
        """Test adding a new store."""
        row_id = self.db.add_store(
            store_name="Nike Store",
            original_message_id=12345,
            forwarded_message_id=67890
        )
        
        self.assertIsNotNone(row_id)
        self.assertGreater(row_id, 0)
        
        # Verify it was added
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM processed_stores WHERE id = ?", (row_id,))
        row = cursor.fetchone()
        
        self.assertEqual(row['store_name'], "Nike Store")
        self.assertEqual(row['normalized_name'], "nike store")
        self.assertEqual(row['original_message_id'], 12345)
        self.assertEqual(row['forwarded_message_id'], 67890)
    
    def test_is_duplicate_exact_match(self):
        """Test duplicate detection with exact match."""
        # Add a store
        self.db.add_store("Nike Store")
        
        # Check for duplicate (exact match, case-insensitive)
        is_dup, matched = self.db.is_duplicate("Nike Store")
        self.assertTrue(is_dup)
        self.assertEqual(matched, "Nike Store")
        
        # Different case
        is_dup, matched = self.db.is_duplicate("NIKE STORE")
        self.assertTrue(is_dup)
    
    def test_is_duplicate_fuzzy_match(self):
        """Test duplicate detection with fuzzy matching."""
        # Add a store
        self.db.add_store("Nike Store")
        
        # Minor typo (should match with fuzzy)
        is_dup, matched = self.db.is_duplicate("Nike Stor")  # Missing 'e'
        self.assertTrue(is_dup)
        
        # Spacing difference (should match)
        is_dup, matched = self.db.is_duplicate("NikeStore")  # No space
        self.assertTrue(is_dup)
    
    def test_is_duplicate_no_match(self):
        """Test duplicate detection when no match exists."""
        # Add a store
        self.db.add_store("Nike Store")
        
        # Completely different store (should not match)
        is_dup, matched = self.db.is_duplicate("Adidas Shop")
        self.assertFalse(is_dup)
        self.assertIsNone(matched)
    
    def test_is_duplicate_threshold(self):
        """Test that fuzzy matching respects threshold."""
        # Add a store
        self.db.add_store("Nike Store")
        
        # Very different (below 90% threshold, should not match)
        is_dup, matched = self.db.is_duplicate("Completely Different Store Name")
        self.assertFalse(is_dup)
    
    def test_is_duplicate_empty_database(self):
        """Test duplicate check on empty database."""
        is_dup, matched = self.db.is_duplicate("Nike Store")
        self.assertFalse(is_dup)
        self.assertIsNone(matched)
    
    def test_multiple_stores(self):
        """Test adding and checking multiple stores."""
        stores = ["Nike Store", "Adidas Shop", "Puma Outlet", "The Store"]
        
        # Add all stores
        for store in stores:
            self.db.add_store(store)
        
        # Verify all are unique
        for store in stores:
            is_dup, matched = self.db.is_duplicate(store)
            self.assertTrue(is_dup)
            self.assertEqual(matched, store)
        
        # Verify new store is not duplicate
        is_dup, matched = self.db.is_duplicate("New Store")
        self.assertFalse(is_dup)
    
    def test_get_stats(self):
        """Test getting database statistics."""
        # Initially empty
        stats = self.db.get_stats()
        self.assertEqual(stats['total_stores'], 0)
        
        # Add stores
        self.db.add_store("Store 1")
        self.db.add_store("Store 2")
        self.db.add_store("Store 3")
        
        # Check stats
        stats = self.db.get_stats()
        self.assertEqual(stats['total_stores'], 3)
    
    def test_context_manager(self):
        """Test database as context manager."""
        with StoreDatabase(self.temp_db.name) as db:
            db.add_store("Test Store")
            stats = db.get_stats()
            self.assertEqual(stats['total_stores'], 1)
        
        # Connection should be closed after context
        # (can't directly test this, but no errors should occur)
    
    def test_fuzzy_match_similar_stores(self):
        """Test fuzzy matching with similar store names."""
        # Add original
        self.db.add_store("The Big Store")
        
        # Variations that should match
        variations = [
            "The Big Store",      # Exact
            "the big store",      # Case
            "TheBigStore",        # No spaces
            "The  Big  Store",    # Extra spaces
            "The Big Stor",       # Minor typo
        ]
        
        for variation in variations:
            is_dup, matched = self.db.is_duplicate(variation)
            self.assertTrue(is_dup, f"'{variation}' should match 'The Big Store'")
    
    def test_fuzzy_match_different_stores(self):
        """Test that different stores don't match."""
        # Add original
        self.db.add_store("Nike")
        
        # These should NOT match
        different_stores = [
            "Adidas",
            "Puma",
            "Reebok",
            "Under Armour",
        ]
        
        for store in different_stores:
            is_dup, matched = self.db.is_duplicate(store)
            self.assertFalse(is_dup, f"'{store}' should not match 'Nike'")


if __name__ == '__main__':
    unittest.main()
