from Grabber import app

async def get_user_full_name(user_id):
    user = await app.get_users(user_id)
    full_name = user.first_name + " " + (user.last_name if user.last_name else "") 
    # print(f"User's full name: {full_name}")
    if full_name:
        return str(full_name)
    return "Unknown"

async def get_latest_user_details_by_id(user_id):
    user = await app.get_users(user_id)
    return user

async def get_mention_of_user_by_id(user_id):
    user = await get_latest_user_details_by_id(user_id)
    latest_name = user.first_name + (" " + user.last_name if user.last_name else "")
    mention_of_user = f"[{latest_name}](tg://user?id={user_id})"
    return mention_of_user