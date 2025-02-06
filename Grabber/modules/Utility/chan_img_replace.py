from Grabber.modules import app

channel_id = ''  # Replace with your channel ID

with app:
    messages = app.get_history(chat_id=channel_id, limit=100)  # Adjust limit as needed

    for msg in messages:
        if msg.photo and msg.caption:
            caption = msg.caption
            print("\nCaption Found:", caption)

            # Extract details using basic parsing
            lines = caption.split("\n")
            details = {line.split(":")[0].strip(): line.split(":")[1].strip() for line in lines if ":" in line}

            print(details)  # Dictionary of extracted data
