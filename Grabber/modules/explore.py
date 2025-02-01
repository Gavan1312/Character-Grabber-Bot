from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime, timedelta
from Grabber import application, user_collection
import random
from . import app, user_collection, collection, add, deduct, show, capsify
from .xp import add_xp, deduct_xp
from Grabber.config_settings import *

COOLDOWN_DURATION = 60
COMMAND_BAN_DURATION = 600

last_command_time = {}
user_cooldowns = {}

async def random_daily_reward(client, message):
    if message.chat.type == "private":
        await message.reply_text(capsify("This command can only be used in group chats."))
        return

    user_id = message.from_user.id

    if message.reply_to_message:
        await message.reply_text(capsify(f"Fuck Explore a orc den and got 10000 {currency_names_plural['balance']}.⚡"))
        return

    if user_id in user_cooldowns and (datetime.utcnow() - user_cooldowns[user_id]) < timedelta(seconds=COOLDOWN_DURATION):
        remaining_time = COOLDOWN_DURATION - (datetime.utcnow() - user_cooldowns[user_id]).total_seconds()
        await message.reply_text(capsify(f"You must wait {int(remaining_time)} seconds before using explore again."))
        return

    user_balance = await show(user_id)
    crime_fee = 300

    if user_balance < crime_fee:
        await message.reply_text(capsify(f"Bc You need at least 500 {currency_names_plural['balance']} to use explore."))
        return

    await deduct(user_id, crime_fee)

    random_reward = random.randint(6000, 30000)

    explore_messages = [
    "went on an adventure with your waifu and discovered a hidden shrine",
    "explored a mystical anime world and found a rare treasure",
    "traveled to another dimension and met an otherworldly waifu",
    "visited a secret sakura garden and found an ancient artifact",
    "joined a guild and explored a monster-infested dungeon",
    "found a lost waifu in the forest who gifted you some gold",
    "fell into an isekai world and received a divine blessing",
    "trained in a samurai dojo and earned a rare scroll",
    "discovered a waifu village hidden deep in the mountains",
    "helped a kitsune spirit and received a lucky charm",
    "stumbled upon a tsundere princess who rewarded you for saving her",
    "accidentally activated a magic circle and got teleported to a treasure hoard",
    "met an idol waifu who gave you a signed photo (worth a lot of money)",
    "bumped into a catgirl maid café and got free cake (and some coins)",
    "fought a demon lord and looted his castle",
    "raided an abandoned anime convention and found limited-edition merch",
    "followed a suspicious-looking map and discovered a legendary waifu shrine",
    "found a portal leading to an anime world full of riches",
    "joined an intergalactic waifu space crew and got paid in rare gems",
    "helped a shy librarian waifu sort books and found a hidden stash of gold"
    ]

    random_message = random.choice(explore_messages)

    await add(user_id, random_reward)
    await add_xp(user_id, 2)
    last_command_time[user_id] = datetime.utcnow()
    user_cooldowns[user_id] = datetime.utcnow()

    await message.reply_text(capsify(f"You {random_message} and got {random_reward} {currency_names_plural['balance']}.🤫"))

@app.on_message(filters.command("explore") & filters.group)
async def explore_command(client, message):
    await random_daily_reward(client, message)


CRIME_COOLDOWN_DURATION = 60
CRIME_COMMAND_BAN_DURATION = 600

crime_last_command_time = {}
crime_user_cooldowns = {}

async def random_daily_reward_crime(client, message):
    if message.chat.type == "private":
        await message.reply_text(capsify("This command can only be used in group chats."))
        return

    user_id = message.from_user.id

    if message.reply_to_message:
        await message.reply_text(capsify(f"Fuck Looted a orc den and got 10000 {currency_names_plural['balance']}.⚡"))
        return

    if user_id in crime_user_cooldowns and (datetime.utcnow() - crime_user_cooldowns[user_id]) < timedelta(seconds=CRIME_COOLDOWN_DURATION):
        remaining_time = CRIME_COOLDOWN_DURATION - (datetime.utcnow() - crime_user_cooldowns[user_id]).total_seconds()
        await message.reply_text(capsify(f"You must wait {int(remaining_time)} seconds before using crime again."))
        return

    user_balance = await show(user_id)
    crime_fee = 300

    if user_balance < crime_fee:
        await message.reply_text(capsify(f"Bc You need at least 500 {currency_names_plural['balance']} to use crime."))
        return

    await deduct(user_id, crime_fee)

    random_reward = random.randint(6000, 30000)

    crime_messages = [
    "stole a rare dakimakura from an anime store",
    "hijacked a mech and sold it on the black market",
    "scammed a rich otaku into buying a fake waifu figurine",
    "hacked into a gacha game and took all the premium currency",
    "looted a yandere’s house and barely escaped with your life",
    "pickpocketed a magical girl’s transformation wand and sold it",
    "stole a famous idol’s microphone and auctioned it online",
    "bribed an anime convention staff member to sneak into VIP",
    "snuck into a waifu café and took all the free snacks",
    "sold bootleg anime merch and made a fortune",
    "hacked into an anime streaming service and sold premium accounts",
    "tricked a chuunibyou into giving you their ‘legendary’ treasure",
    "robbed a tsundere’s secret love letter collection and sold them as fanfiction",
    "scammed a shounen protagonist by selling him ‘rare training manuals’",
    "hacked into an isekai summoning system and stole some rewards",
    "pretended to be a harem protagonist and borrowed money from all the waifus",
    "stole a vampire waifu’s coffin and sold it as an antique",
    "pickpocketed a ninja waifu but got caught and barely escaped",
    "tricked a loli mage into giving you a ‘good luck’ spell and sold it to a gambler",
    "sold a fake ‘legendary katana’ to a samurai waifu for a fortune"
    ]
    
    random_message = random.choice(crime_messages)

    await add(user_id, random_reward)
    await add_xp(user_id, 2)
    crime_last_command_time[user_id] = datetime.utcnow()
    crime_user_cooldowns[user_id] = datetime.utcnow()

    await message.reply_text(capsify(f"You {random_message} and got {random_reward} {currency_names_plural['balance']}.🤫"))

@app.on_message(filters.command("crime") & filters.group)
async def crime_command(client, message):
    await random_daily_reward_crime(client, message)