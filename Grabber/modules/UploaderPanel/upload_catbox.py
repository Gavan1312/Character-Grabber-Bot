import requests 

def upload_to_catbox(photo_path):
    url = "https://catbox.moe/user/api.php"
    try:
        with open(photo_path, 'rb') as photo:
            response = requests.post(
                url,
                data={'reqtype': 'fileupload'},
                files={'fileToUpload': photo}
            )
        response.raise_for_status()  # Raise error for HTTP errors
        if response.text.startswith("https://"):
            return response.text.strip()
        else:
            raise Exception(f"Invalid response: {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Catbox request failed: {e}")