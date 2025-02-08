import re
import unicodedata

def clean_text(text):
    # Normalize text to remove special Unicode variations
    # text = unicodedata.normalize("NFKC", text)
    # # Remove any Markdown-breaking characters like `*`, `_`, and ``
    # text = re.sub(r'[*_`]', '', text)
    text = text.replace("`", "")
    return text