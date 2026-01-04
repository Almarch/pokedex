import unicodedata
import regex
from .qdrant import qdrant
from .config import Languages, default_language
from pydantic import create_model
from .ollama import typed_gen

def normalize(
        text: str
    ) -> str:
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = text.lower()
    return text

def fuzzy_match(
        pattern: str,
        text: str
    ) -> bool:
    max_error = 1 if len(pattern) <= 5 else 2
    pattern = normalize(pattern)
    pattern = f'^({regex.escape(pattern)}){{e<={max_error}}}$'

    text = normalize(text)
    text = regex.findall(r'\b\w+\b', text)
    for word in text:
        if regex.search(pattern, word):
            return True
    return False

def pokemon_match(
        text: str,
        language: Languages = default_language,
    ) -> list[str]:
    pkmn = qdrant.scroll(
        collection_name = "name_" + language,
        limit=10000,
        with_payload=True,
        with_vectors=False
    )[0]
    pkmn = [p for pk in pkmn if fuzzy_match(p := pk.payload["name"], text)]
    return pkmn

def double_check(
        words: list[str],
        text: str | list[dict]
    ) -> list[str]:

    text = str(text)

    fields = {}
    for word in words:
        fields[word] = (bool, ...)
    
    Confirmations = create_model(
        'Confirmations',
        **fields
    )

    prompt = f"""
### INSTRUCTIONS

You are an assistant that verifies whether certain
Pokémons names are mentioned in a given conversation.

You receive a list of Pokémons and a conversation between
a user and an assistant as input. For each Pokémon name,
check if it is mentioned in the conversation and return :

- True if it is mentioned.
- False otherwise.

Some Pokémons names may have typos or slight variations.
Use the context to make an informed decision.

You must generate only a valid JSON object with boolean fields,
and for the following Pokémon names to verify:

{{
  {',\n  '.join(f'"{word}": true | false' for word in words)}
}}

### INPUT

Conversation:

{text}

### OUTPUT
"""
    confirmations = typed_gen(
        prompt,
        Confirmations
    )
    return [
        word for word in words 
        if confirmations[word]
    ]
