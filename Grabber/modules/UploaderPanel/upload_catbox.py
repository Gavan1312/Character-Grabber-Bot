import requests 

def upload_to_catbox(photo_path):
    url = "https://catbox.moe/user/api.php"
    with open(photo_path, 'rb') as photo:
        response = requests.post(
            url,
            data={'reqtype': 'fileupload'},
            files={'fileToUpload': photo}
        )
    if response.status_code == 200 and response.text.startswith("https://"):
        return response.text.strip()
    else:
        raise Exception(f"Catbox upload failed: {response.text}")