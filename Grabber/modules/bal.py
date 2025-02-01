from pyrogram import Client, filters
from pyrogram.types import Message
from . import Grabberu as app, user_collection, show, sbank, capsify, BOT_USERNAME,sfirstname
from datetime import datetime
from .block import block_dec, temp_block
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM
from .cleantext import clean_text
from Grabber.utils.realuserdetails import *

@app.on_message(filters.command("bal"))
@block_dec
async def balance(client: Client, message: Message):
    if not message.from_user:
        await message.reply_text(capsify("COULDN'T RETRIEVE USER INFORMATION."))
        return

    user_id = message.from_user.id
    replied_user_id = None
    
    if message.reply_to_message:
        replied_user_id = message.reply_to_message.from_user.id
    
    if replied_user_id:
        user_id = replied_user_id

    if temp_block(user_id):
        return
    user_data = await user_collection.find_one(
        {'id': user_id}, 
        projection={'balance': 1, 'saved_amount': 1, 'loan_amount': 1}
    )

    if user_data:
        ub = await show(user_id)
        balance_amount = int(ub)
        bb = await sbank(user_id)
        saved_amount = int(bb)
        loan_amount = user_data.get('loan_amount', 0)
        fn = await sfirstname(user_id)
        # first_name = clean_text(str(fn))
        first_name = str(fn).replace("’", "'").replace("‘", "'")
        safe_first_name = first_name.replace("'", "\u200B'")  # Add zero-width space before apostrophe

        ''' 💕 Love Stash        
         💘 Building a treasure of passion!
         💞 Love Points:
         💌 Hidden Affection:
         💦 Simp Debt: 0  '''

        '''formatted_balance = f"🔹{first_name}'s COINS: `{balance_amount:,.0f}`\n"
        formatted_saved = f"🔸 AMOUNT SAVED: `{saved_amount:,.0f}`\n"
        formatted_loan = f"🔻 LOAN AMOUNT: `{loan_amount:,.0f}`\n"'''
        safe_first_name = clean_text(first_name)  # Keep fancy fonts intact

        formatted_title = f"**💕{safe_first_name}'s** ʟᴏᴠᴇ sᴛᴀsʜ 💕\n\n"
        # formatted_title = f"💕{first_name}'s Love Stash 💕\n\n"
        # formatted_title = "**💕{}'s** Love Stash 💕\n\n".format(safe_first_name)
        formatted_balance = f"**💞 Love Points :** `{balance_amount:,.0f}`\n"
        formatted_saved = f"**💌 Hidden Affection :** `{saved_amount:,.0f}`\n"
        formatted_loan = f"**💔 Simp Debt :** `{loan_amount:,.0f}`\n"
        formatted_description = f"\n💘 A treasure of passion!\n"

        balance_message = formatted_title + formatted_balance + formatted_saved + formatted_loan + formatted_description;
        balance_message = capsify(balance_message)

        await message.reply_text(balance_message)
    else:
        # balance_message = "please start the bot in dm to register"
        # balance_message = capsify(balance_message)
        # await message.reply_text(balance_message)
        return await message.reply_text(
            capsify(f"🚀 {get_user_full_name(user_id)}, You haven't started your journey yet, You need to start the bot first in DM. click the button below to Set on a new journey 🎊"),
            reply_markup=IKM([
                [IKB(capsify("Start in DM"), url=f"https://t.me/{BOT_USERNAME}?start=start")]
            ])
        )
        