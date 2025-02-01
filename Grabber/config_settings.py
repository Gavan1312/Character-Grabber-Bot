currency_symbols = {
    "xp": "Level ",        
    "balance": "Ƀ",   
    "gold": "𝒢",      
    "rubies": "Ⓡ"     
}

currency_names = {
    "xp": "Level ",        
    "balance": "Love Point",   
    "gold": "Gold",      
    "rubies": "Ruby"     
}

currency_names_plural = {
    "xp": "Level ",        
    "balance": "Love Points",   
    "gold": "Gold",     
    "rubies": "Rubies"    
}

currency_bag_title = {
    "xp": "Level ",        
    "balance": "💟 Love Stash",   
    "gold": "Gold",     
    "rubies": "Rubies"    
}

IN_DEV_MODE = False  # Default state

@app.on_message(filters.command("indevmode") & filters.user(OWNER_ID))
@block_dec
async def indev_mode_command(client, message):
    if(message.from_user.id != OWNER_ID):
        return
    global IN_DEV_MODE  # Ensure we're modifying the global variable

    args = message.command[1:]  # Get command arguments after /indevmode
    if len(args) == 2 and args[0].lower() == "owner":
        if args[1].lower() in ["true", "false"]:
            IN_DEV_MODE = args[1].lower() == "true"
            status = "enabled ✅" if IN_DEV_MODE else "disabled ❌"
            await message.reply_text(f"Developer mode is now {status}.")
        else:
            await message.reply_text("Invalid value! Use `/indevmode owner true` or `/indevmode owner false`.")
    else:
        await message.reply_text("Usage: `/indevmode owner true` or `/indevmode owner false`.")