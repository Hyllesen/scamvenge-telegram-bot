"""
Unit tests for the bot module configuration and test mode.
"""
import unittest
import os
from unittest.mock import patch, MagicMock
from src.bot import TelegramBot


class TestBotConfiguration(unittest.TestCase):
    """Test bot configuration and test mode."""
    
    @patch.dict(os.environ, {
        'API_ID': '12345',
        'API_HASH': 'test_hash',
        'PHONE_NUMBER': '+1234567890',
        'TEST_MODE': 'false'
    })
    @patch('src.bot.TelegramClient')
    @patch('src.bot.StoreDatabase')
    def test_test_mode_disabled_by_default(self, mock_db, mock_client):
        """Test that test mode is disabled by default."""
        bot = TelegramBot()
        self.assertFalse(bot.test_mode)
    
    @patch.dict(os.environ, {
        'API_ID': '12345',
        'API_HASH': 'test_hash',
        'PHONE_NUMBER': '+1234567890',
        'TEST_MODE': 'true'
    })
    @patch('src.bot.TelegramClient')
    @patch('src.bot.StoreDatabase')
    def test_test_mode_enabled_with_true(self, mock_db, mock_client):
        """Test that test mode can be enabled with 'true'."""
        bot = TelegramBot()
        self.assertTrue(bot.test_mode)
    
    @patch.dict(os.environ, {
        'API_ID': '12345',
        'API_HASH': 'test_hash',
        'PHONE_NUMBER': '+1234567890',
        'TEST_MODE': '1'
    })
    @patch('src.bot.TelegramClient')
    @patch('src.bot.StoreDatabase')
    def test_test_mode_enabled_with_one(self, mock_db, mock_client):
        """Test that test mode can be enabled with '1'."""
        bot = TelegramBot()
        self.assertTrue(bot.test_mode)
    
    @patch.dict(os.environ, {
        'API_ID': '12345',
        'API_HASH': 'test_hash',
        'PHONE_NUMBER': '+1234567890',
        'TEST_MODE': 'yes'
    })
    @patch('src.bot.TelegramClient')
    @patch('src.bot.StoreDatabase')
    def test_test_mode_enabled_with_yes(self, mock_db, mock_client):
        """Test that test mode can be enabled with 'yes'."""
        bot = TelegramBot()
        self.assertTrue(bot.test_mode)
    
    @patch.dict(os.environ, {
        'API_ID': '12345',
        'API_HASH': 'test_hash',
        'PHONE_NUMBER': '+1234567890',
        'TEST_MODE': 'TRUE'
    })
    @patch('src.bot.TelegramClient')
    @patch('src.bot.StoreDatabase')
    def test_test_mode_case_insensitive(self, mock_db, mock_client):
        """Test that test mode is case-insensitive."""
        bot = TelegramBot()
        self.assertTrue(bot.test_mode)
    
    @patch.dict(os.environ, {
        'API_ID': '12345',
        'API_HASH': 'test_hash',
        'PHONE_NUMBER': '+1234567890',
        'TEST_MODE': 'false'
    })
    @patch('src.bot.TelegramClient')
    @patch('src.bot.StoreDatabase')
    def test_test_mode_disabled_with_false(self, mock_db, mock_client):
        """Test that test mode is disabled with 'false'."""
        bot = TelegramBot()
        self.assertFalse(bot.test_mode)
    
    @patch.dict(os.environ, {
        'API_ID': '12345',
        'API_HASH': 'test_hash',
        'PHONE_NUMBER': '+1234567890',
        'TEST_MODE': '0'
    })
    @patch('src.bot.TelegramClient')
    @patch('src.bot.StoreDatabase')
    def test_test_mode_disabled_with_zero(self, mock_db, mock_client):
        """Test that test mode is disabled with '0'."""
        bot = TelegramBot()
        self.assertFalse(bot.test_mode)
    
    @patch.dict(os.environ, {
        'API_ID': '12345',
        'API_HASH': 'test_hash',
        'PHONE_NUMBER': '+1234567890',
        'SOURCE_GROUP': 'TestGroup',
        'TARGET_USER': 'TestUser',
        'DATABASE_PATH': './test.db'
    })
    @patch('src.bot.TelegramClient')
    @patch('src.bot.StoreDatabase')
    def test_configuration_loading(self, mock_db, mock_client):
        """Test that configuration is loaded correctly."""
        bot = TelegramBot()
        self.assertEqual(bot.source_group, 'TestGroup')
        self.assertEqual(bot.target_user, 'TestUser')
        self.assertEqual(bot.db_path, './test.db')
    
    @patch.dict(os.environ, {
        'API_ID': '12345',
        'API_HASH': 'test_hash',
        'PHONE_NUMBER': '+1234567890'
    })
    @patch('src.bot.TelegramClient')
    @patch('src.bot.StoreDatabase')
    def test_default_configuration(self, mock_db, mock_client):
        """Test default configuration values."""
        bot = TelegramBot()
        self.assertEqual(bot.source_group, 'Alloy')
        self.assertEqual(bot.target_user, 'Imelda')
        self.assertEqual(bot.db_path, './data/stores.db')
        self.assertFalse(bot.test_mode)
    
    @patch.dict(os.environ, {
        'API_HASH': 'test_hash',
        'PHONE_NUMBER': '+1234567890'
    })
    def test_missing_api_id_raises_error(self):
        """Test that missing API_ID raises ValueError."""
        with self.assertRaises(ValueError) as context:
            TelegramBot()
        self.assertIn('API_ID', str(context.exception))
    
    @patch.dict(os.environ, {
        'API_ID': '12345',
        'PHONE_NUMBER': '+1234567890'
    })
    def test_missing_api_hash_raises_error(self):
        """Test that missing API_HASH raises ValueError."""
        with self.assertRaises(ValueError) as context:
            TelegramBot()
        self.assertIn('API_HASH', str(context.exception))


if __name__ == '__main__':
    unittest.main()
