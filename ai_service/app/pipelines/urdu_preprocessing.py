import re

# Character mappings for Urdu normalization
CHAR_MAP = {
    # Kaf normalization
    "\u0643": "\u06a9",  # Arabic Kaf -> Urdu Keheh
    # Yeh normalization
    "\u064a": "\u06cc",  # Arabic Yeh -> Urdu Yeh (Barree/Chotee Yeh standardization)
    "\u0649": "\u06cc",  # Arabic Alef Maksura -> Urdu Yeh
    # Heh normalization
    "\u0647": "\u06c1",  # Arabic Heh -> Urdu Heh Goal
    "\u0629": "\u06c1",  # Arabic Teh Marbuta -> Urdu Heh Goal
    # Digits normalization (Eastern Arabic-Indic digits to Urdu / Western)
    "\u06f0": "0", "\u0660": "0",
    "\u06f1": "1", "\u0661": "1",
    "\u06f2": "2", "\u0662": "2",
    "\u06f3": "3", "\u0663": "3",
    "\u06f4": "4", "\u0664": "4",
    "\u06f5": "5", "\u0665": "5",
    "\u06f6": "6", "\u0666": "6",
    "\u06f7": "7", "\u0667": "7",
    "\u06f8": "8", "\u0668": "8",
    "\u06f9": "9", "\u0669": "9",
}

def normalize_urdu_characters(text: str) -> str:
    """Replaces non-standard Arabic/Persian characters with standard Urdu equivalents."""
    normalized = []
    for char in text:
        normalized.append(CHAR_MAP.get(char, char))
    return "".join(normalized)

def remove_noise(text: str) -> str:
    """Removes URLs, social media mentions, hashtags, HTML tags, and excessive punctuation."""
    # Remove HTML Tags
    text = re.sub(r"<[^>]*>", "", text)
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    # Remove user mentions (@user)
    text = re.sub(r"@\w+", "", text)
    # Remove hashtags (keep the word, remove hash symbol)
    text = re.sub(r"#", "", text)
    # Remove emails
    text = re.sub(r"\S+@\S+", "", text)
    # Remove emojis & non-Urdu non-English characters
    # Keep Urdu Unicode block (0600-06FF, 0750-077F, FB50-FDFF, FE70-FEFF) and English letters/basic punctuation
    text = re.sub(r"[^\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z\s.,!?;?()\"\'\-]", "", text)
    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

def preprocess_text(text: str) -> str:
    """Full text processing pipeline for Urdu social media posts."""
    if not text or not isinstance(text, str):
        return ""
    text = remove_noise(text)
    text = normalize_urdu_characters(text)
    return text
