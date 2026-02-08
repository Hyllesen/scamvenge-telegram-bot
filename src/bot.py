"""
Telegram bot module for monitoring groups and forwarding messages.
"""
import os
import logging
import asyncio
from pathlib import Path
from typing import Optional
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from telethon.tl.types import User, Channel, Chat
from dotenv import load_dotenv

from .processor import ImageProcessor
from .database import StoreDatabase
from .exceptions import InvalidImageError, OCRError, DatabaseError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Main bot class for Telegram integration."""
    
    def __init__(self):
        """Initialize bot with configuration from environment."""
        load_dotenv()
        
        # Load configuration
        self.api_id = os.getenv('API_ID')
        self.api_hash = os.getenv('API_HASH')
        self.phone_number = os.getenv('PHONE_NUMBER')
        self.source_group = os.getenv('SOURCE_GROUP', 'Alloy')
        self.target_user = os.getenv('TARGET_USER', 'Imelda')
        self.db_path = os.getenv('DATABASE_PATH', './data/stores.db')
        
        # Test mode configuration
        self.test_mode = os.getenv('TEST_MODE', 'false').lower() in ('true', '1', 'yes')
        
        # Set log level from environment
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        logger.setLevel(getattr(logging, log_level))
        
        # Validate configuration BEFORE creating Telegram client
        if not all([self.api_id, self.api_hash, self.phone_number]):
            raise ValueError("Missing required environment variables: API_ID, API_HASH, PHONE_NUMBER")
        
        # Create data directory if it doesn't exist
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.client = TelegramClient('bot_session', int(self.api_id), self.api_hash)
        self.processor = None  # Initialize after client starts (to check GPU availability)
        self.database = StoreDatabase(self.db_path)
        
        # Temp directory for downloads
        self.temp_dir = Path('./temp')
        self.temp_dir.mkdir(exist_ok=True)
        
        logger.info("Bot initialized successfully")
    
    async def start(self):
        """Start the bot and authenticate."""
        try:
            logger.info("Starting Telegram client...")
            await self.client.start(phone=self.phone_number)
            
            # Initialize processor after client starts
            logger.info("Initializing OCR processor...")
            self.processor = ImageProcessor(languages=['en'], gpu=False)
            
            # Get and log current user info
            me = await self.client.get_me()
            logger.info(f"Logged in as: {me.first_name} ({me.phone})")
            
            # Log test mode status
            if self.test_mode:
                logger.warning("="*60)
                logger.warning("🧪 TEST MODE ENABLED - Messages will NOT be forwarded")
                logger.warning("   Database will NOT be modified")
                logger.warning("="*60)
            
            # Verify source group and target user exist
            await self._verify_entities()
            
            # Register event handlers
            self._register_handlers()
            
            logger.info("Bot started successfully. Monitoring for messages...")
            
            # Run until disconnected
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise
        finally:
            self.cleanup()
    
    async def _verify_entities(self):
        """Verify that source group and target user exist."""
        try:
            # Try to get source group
            source_entity = await self.client.get_entity(self.source_group)
            logger.info(f"Source group found: {self._get_entity_name(source_entity)}")
            
            # Try to get target user
            target_entity = await self.client.get_entity(self.target_user)
            logger.info(f"Target user found: {self._get_entity_name(target_entity)}")
            
        except Exception as e:
            logger.error(f"Failed to verify entities: {e}")
            logger.error("Make sure SOURCE_GROUP and TARGET_USER are correct")
            raise
    
    @staticmethod
    def _get_entity_name(entity) -> str:
        """Get a readable name for a Telegram entity."""
        if isinstance(entity, User):
            return entity.first_name or entity.username or str(entity.id)
        elif isinstance(entity, (Channel, Chat)):
            return entity.title or str(entity.id)
        return str(entity.id)
    
    def _register_handlers(self):
        """Register event handlers for incoming messages."""
        
        @self.client.on(events.NewMessage(chats=self.source_group))
        async def handle_new_message(event):
            """Handle new messages in the source group."""
            try:
                # Only process messages with photos
                if not event.message.photo:
                    return
                
                logger.info(f"New photo message received (ID: {event.message.id})")
                
                # Download photo
                photo_path = await self._download_photo(event.message)
                
                if photo_path:
                    await self._process_photo(event.message, photo_path)
                    
            except FloodWaitError as e:
                logger.warning(f"Rate limited. Waiting {e.seconds} seconds...")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.error(f"Error handling message: {e}", exc_info=True)
    
    async def _download_photo(self, message) -> Optional[Path]:
        """
        Download photo from message.
        
        Args:
            message: Telegram message object
            
        Returns:
            Path to downloaded photo, or None if failed
        """
        try:
            # Generate unique filename
            photo_path = self.temp_dir / f"photo_{message.id}.jpg"
            
            # Download
            await self.client.download_media(message.photo, photo_path)
            logger.debug(f"Photo downloaded: {photo_path}")
            
            return photo_path
            
        except Exception as e:
            logger.error(f"Failed to download photo: {e}")
            return None
    
    async def _process_photo(self, message, photo_path: Path):
        """
        Process downloaded photo: OCR, validate, check duplicates, forward.
        
        Args:
            message: Original Telegram message
            photo_path: Path to downloaded photo
        """
        try:
            # Run OCR and extract store name
            logger.info("Running OCR on image...")
            store_name = self.processor.process_image(str(photo_path))
            logger.info(f"Extracted store name: '{store_name}'")
            
            # Check for duplicates
            is_dup, matched_name = self.database.is_duplicate(store_name)
            
            if is_dup:
                logger.info(f"Duplicate detected: '{store_name}' matches existing '{matched_name}'")
                if self.test_mode:
                    logger.info(f"🧪 TEST MODE: Would have skipped duplicate (no action taken)")
                return
            
            # Handle based on mode
            if self.test_mode:
                # Test mode: Log what would happen, don't actually do it
                logger.info("="*60)
                logger.info(f"🧪 TEST MODE: Would forward to '{self.target_user}'")
                logger.info(f"   Store Name: '{store_name}'")
                logger.info(f"   Original Message ID: {message.id}")
                logger.info(f"   Would save to database: {self.db_path}")
                logger.info("   ✅ UNIQUE - Would be forwarded in production mode")
                logger.info("="*60)
            else:
                # Production mode: Actually forward and save
                logger.info(f"Forwarding new store '{store_name}' to {self.target_user}...")
                forwarded_msg = await self._forward_message(message)
                
                if forwarded_msg:
                    # Save to database
                    self.database.add_store(
                        store_name=store_name,
                        original_message_id=message.id,
                        forwarded_message_id=forwarded_msg.id
                    )
                    logger.info(f"Successfully processed and saved: '{store_name}'")
                    
                    # Log stats
                    stats = self.database.get_stats()
                    logger.info(f"Total unique stores: {stats['total_stores']}")
            
        except InvalidImageError as e:
            logger.warning(f"Invalid image (no keywords): {e}")
        except OCRError as e:
            logger.error(f"OCR failed: {e}")
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing photo: {e}", exc_info=True)
        finally:
            # Cleanup downloaded file
            if photo_path and photo_path.exists():
                photo_path.unlink()
                logger.debug(f"Cleaned up: {photo_path}")
    
    async def _forward_message(self, message):
        """
        Forward message to target user.
        
        Args:
            message: Message to forward
            
        Returns:
            Forwarded message object, or None if failed
        """
        try:
            target_entity = await self.client.get_entity(self.target_user)
            forwarded = await self.client.forward_messages(target_entity, message)
            logger.debug(f"Message forwarded (ID: {forwarded.id})")
            return forwarded
            
        except Exception as e:
            logger.error(f"Failed to forward message: {e}")
            return None
    
    def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up...")
        
        # Close database
        if self.database:
            self.database.close()
        
        # Clean temp directory
        if self.temp_dir.exists():
            for file in self.temp_dir.glob('*'):
                try:
                    file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete {file}: {e}")
        
        logger.info("Cleanup complete")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
