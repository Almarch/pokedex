import unicodedata
import regex
from .qdrant import qdrant

def normalize(text):
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = text.lower()
    return text

def fuzzy_match(pattern, text):
    max_error = 1 if len(pattern) <= 5 else 2
    pattern = normalize(pattern)
    pattern = f'^({regex.escape(pattern)}){{e<={max_error}}}$'

    text = normalize(text)
    text = regex.findall(r'\b\w+\b', text)
    for word in text:
        if regex.search(pattern, word):
            return True
    return False

def pokemon_match(text, language):
    pkmn = qdrant.scroll(
        collection_name = "name_" + language,
        limit=10000,
        with_payload=True,
        with_vectors=False
    )[0]
    pkmn = [p for pk in pkmn if fuzzy_match(p := pk.payload["name"], text)]
    return pkmn