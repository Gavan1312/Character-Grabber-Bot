from Grabber import app

async def get_user_full_name(user_id):
    user = await app.get_users(user_id)
    full_name = user.first_name + " " + (user.last_name if user.last_name else "") 
    # print(f"User's full name: {full_name}")
    if full_name:
        return str(full_name)
    return "Unknown"