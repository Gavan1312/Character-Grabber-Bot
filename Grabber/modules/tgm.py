import requests
from pyrogram import filters
from . import app
from Grabber.modules.UploaderPanel.upload_catbox import upload_to_catbox
import os
import re
import mimetypes
import m3u8
from urllib.parse import urlparse, urljoin

@app.on_message(filters.command("tgm_dl_link"))
def ul(_, message):
    reply = message.reply_to_message
    if not reply or not reply.media:
        return message.reply("Please reply to an image or media to upload.")

    i = message.reply("**Downloading...**")
    path = reply.download()

    if not path:
        return i.edit("Failed to download the file.")

    try:
        file_url = upload_to_catbox(path)
        i.edit(f'Your Catbox [link]({file_url})', disable_web_page_preview=True)
    except Exception as e:
        i.edit(f"An error occurred: {str(e)}")
        
    
def get_filename_from_url(url: str, response: requests.Response) -> str:
    """
    Extract the filename from the URL.
    If the filename does not contain an extension, try to obtain it from headers.
    """
    # Extract the basename from the URL path
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    
    # If filename is empty, use a default name
    if not filename:
        filename = "downloaded_file"
    
    # Check if the filename has an extension
    name, ext = os.path.splitext(filename)
    if not ext:
        # Try to extract from Content-Disposition header
        content_disp = response.headers.get("content-disposition")
        if content_disp:
            fname_match = re.findall('filename="([^"]+)"', content_disp)
            if fname_match:
                filename = fname_match[0]
                name, ext = os.path.splitext(filename)
                
        # If still no extension, guess from Content-Type header
        if not ext:
            content_type = response.headers.get("content-type")
            if content_type:
                ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
                filename = f"{filename}{ext}" if ext else f"{filename}.bin"
            else:
                filename = f"{filename}.bin"
    return filename

@app.on_message(filters.command("download_from_url"))
def download_and_send(client, message):
    # Check if URL is provided
    if len(message.command) < 2:
        message.reply_text("Usage: /download_from_url <url>")
        return

    url = message.command[1]
    message.reply_text("Downloading file...")

    try:
        # Stream the file download
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raises an error for bad status codes
    except Exception as e:
        message.reply_text(f"Error downloading file: {e}")
        return

    # Get filename with preserved extension
    filename = get_filename_from_url(url, response)

    try:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)
    except Exception as e:
        message.reply_text(f"Error saving file: {e}")
        return

    try:
        # Send the downloaded file as a Telegram document
        message.reply_document(document=filename)
    except Exception as e:
        message.reply_text(f"Error sending file: {e}")
    finally:
        # Remove the downloaded file from disk
        if os.path.exists(filename):
            os.remove(filename)
            

def download_hls_video(playlist_url: str, output_filename: str) -> str:
    """
    Download an HLS video by fetching its m3u8 playlist,
    downloading each segment, and combining them into one file.
    """
    # Download the m3u8 playlist
    playlist_response = requests.get(playlist_url)
    playlist_response.raise_for_status()
    playlist = m3u8.loads(playlist_response.text)

    with open(output_filename, "wb") as f_out:
        for segment in playlist.segments:
            # Build the full URL for the segment (handle relative paths)
            segment_url = segment.uri
            if not segment_url.startswith("http"):
                segment_url = urljoin(playlist_url, segment_url)
            seg_response = requests.get(segment_url, stream=True)
            seg_response.raise_for_status()
            for chunk in seg_response.iter_content(chunk_size=8192):
                if chunk:
                    f_out.write(chunk)
    return output_filename

@app.on_message(filters.command("download_video_from_url"))
def download_video(client, message):
    """
    Download a segmented video (HLS/m3u8) from the given URL, merge the segments,
    and send it as a Telegram document.
    """
    if len(message.command) < 2:
        message.reply_text("Usage: /download_video_from_url <m3u8 url>")
        return

    playlist_url = message.command[1]
    # Use the last part of the playlist URL as a base filename, default to "downloaded_video"
    output_filename = os.path.basename(urlparse(playlist_url).path)
    if not output_filename:
        output_filename = "downloaded_video"
    # Force the extension to be .mp4 (or adjust as needed)
    name, ext = os.path.splitext(output_filename)
    output_filename = f"{name}.mp4"

    message.reply_text("Downloading video file...")

    try:
        download_hls_video(playlist_url, output_filename)
    except Exception as e:
        message.reply_text(f"Error downloading video: {e}")
        return

    try:
        message.reply_document(document=output_filename)
    except Exception as e:
        message.reply_text(f"Error sending video file: {e}")
    finally:
        if os.path.exists(output_filename):
            os.remove(output_filename)