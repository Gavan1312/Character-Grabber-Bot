import re
from Grabber import app
from pyrogram import Client
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton,InlineQueryResultPhoto

from Grabber.modules import user_collection, collection, application, db, capsify
from Grabber.modules.Settings.rarityMap import *

@app.on_inline_query()
async def inlinequery(client: Client, query: InlineQuery):
    # print(f"[DEBUG] Inline Query Triggered: '{query.query.strip()}'") 
    search_query = query.query.strip()
    offset = int(query.offset) if query.offset else 0
    results_per_page = 15
    start_index = offset
    end_index = offset + results_per_page

    # print(f"[DEBUG] Inline Query Received: '{search_query}' (Offset: {offset})")  # Debug

    try:
        if search_query.isdigit():
            filter_query = {'id': {"$in": [int(search_query), search_query]}}
        else:
            regex = re.compile(search_query, re.IGNORECASE)
            filter_query = {"$or": [{"name": regex}, {"anime": regex}]}

        all_characters = await collection.find(
            filter_query,
            {'name': 1, 'anime': 1, 'img_url': 1, 'id': 1, 'rarity': 1, 'price': 1}
        ).skip(start_index).limit(results_per_page).to_list(length=None)

        # print(f"[DEBUG] Characters Found: {len(all_characters)}")  # Debug

        # You can pass the chat_id manually if you are triggering this from a group chat
        chat_id = query.from_user.id  # This is the user's id, not the chat's id

        results = [
            InlineQueryResultPhoto(
                id=str(character['id']),
                photo_url=character['img_url'],  # URL of the character image (thumbnail)
                thumb_url=character['img_url'],  # Small image for the thumbnail (could be a lower resolution version)
                title=character['name'],
                description=f"Anime: {character['anime']} | Rarity: {character.get('rarity', '')}",
                input_message_content=InputTextMessageContent(
                    f"Click below to view {character['name']}."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "View Character 😍", 
                            callback_data=f"view_{character['id']}_{query.from_user.id}"  # Pass chat_id here
                        )
                    ]
                ])
            ) for character in all_characters
        ]

        next_offset = str(end_index) if len(results) == results_per_page else ""
        await query.answer(results, next_offset=next_offset, cache_time=5)

        # print(f"[DEBUG] Inline Query Answered Successfully.")  # Debug
    except Exception as e:
        print(f"[ERROR] Inline Query Failed: {e}")  # Debug

@app.on_callback_query()
async def button_click(client, callback_query):
    data = callback_query.data
    # print(f"[DEBUG] Callback Query Received: {data}")  # Debug

    if data.startswith("view_"):
        try:
            # Split callback data to get the character ID and chat_id
            parts = data.split("_")
            char_id = str(parts[1])
            chat_id = int(parts[2])  # Extract chat_id passed in callback_data

            # print(f"[DEBUG] Fetching Character ID: {char_id} for Chat ID: {chat_id}")  # Debug
            
            character = await collection.find_one({'id': char_id})
            
            if character:
                # print(f"[DEBUG] Character Found: {character['name']}")  # Debug
                
                reply_to_message_id = callback_query.message.id if callback_query.message else None

                # Send the character details to the same group chat (using chat_id from callback_data)
                await client.send_photo(
                    chat_id=chat_id,  # Send message to the group chat
                    reply_to_message_id=reply_to_message_id,  # Replies to the original message
                    photo=character['img_url'],
                    caption=f"**Name:** {character['name']}\n"
                            f"**Anime:** {character['anime']}\n"
                            f"**Rarity:** {character.get('rarity', '')}\n"
                            f"**Id:** {character.get('id', '')}",
                    protect_content=True  # 🔒 Protecting Content
                )
                # print(f"[DEBUG] Image Sent to Group Chat ID: {chat_id}.")  # Debug
            # else:
                # print(f"[WARNING] Character Not Found for ID: {char_id}")  # Debug

            await callback_query.answer()

        except Exception as e:
            print(f"[ERROR] Inline Callback Query Failed: {e}")  # Debug
