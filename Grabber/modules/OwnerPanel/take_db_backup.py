import json
import os
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from pyrogram import Client, filters
from pyrogram.types import Message
from Grabber.modules import dev_filter, app
from Grabber.config import DB_BKP_CHANNEL_ID, DATABASE_NAME, MONGO_URL, OWNER_ID

# MongoDB connection
MONGO_URI = MONGO_URL
DB_NAME = DATABASE_NAME

@app.on_message(filters.command('take_db_backup') & (dev_filter | filters.user(OWNER_ID)))
async def take_db_backup(client: Client, message: Message):
    loading_message = await message.reply_text("Taking database backup... ⏳")

    try:
        # Connect to the database
        source_client = MongoClient(MONGO_URI)
        source_db = source_client[DB_NAME]

        backup_filename = f"db_backup_{DATABASE_NAME}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Custom JSON encoder for ObjectId and datetime
        class CustomJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, ObjectId):
                    return str(obj)
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)

        # Backup database to JSON
        backup_data = {}
        for collection_name in source_db.list_collection_names():
            collection = source_db[collection_name]
            documents = list(collection.find({}))
            backup_data[collection_name] = documents

        # Save to file
        with open(backup_filename, "w", encoding="utf-8") as backup_file:
            json.dump(backup_data, backup_file, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)

        # Send file to backup channel
        await client.send_document(DB_BKP_CHANNEL_ID, backup_filename, caption="📦 Database Backup Completed!")

        # Delete local backup file
        os.remove(backup_filename)
        
        await loading_message.delete()
        await message.reply_text("✅ Database backup completed and sent successfully!")
        
    except Exception as e:
        await loading_message.delete()
        await message.reply_text(f"❌ Backup failed: {str(e)}")