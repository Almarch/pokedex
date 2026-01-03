from .ollama import typed_gen
from pydantic import BaseModel
from typing import Literal

class Summary(BaseModel):
    summary: str
    language: Literal["fr", "de", "es", "it", "en", "other"]
    is_about_pokemon: bool

def summarize(
    conversation,
):
    prompt = f"""
### INSTRUCTIONS

You are an assistant and your role is to process a conversation.
You generate a json with an output field, containing 3 subfields:
summary, language, is_about_pokemon.
Output only valid JSON. No extra text.

You have 4 tasks:

1. Summarize the last message of the conversation.
2. Identify the language of the conversation.
3. Identify if the conversation is about Pokémon.

Task 1: Conversation summary:
- The summary must capture the main points of the last message.
- Ther rest of the conversation is there to provide context and to
better understand the last message.
- The summary must be at maximum a few sentences long.
- The summary must be written in the same language as
the conversation, especially the last message from the user.

Task 2: Simply identify the language of the conversation.
- "fr" for French
- "de" for German
- "es" for Spanish
- "it" for Italian
- "en" for English
- "other" otherwise.

Task 3: Identify if the conversation is about Pokémon.
- If the conversation is about Pokémon, set "is_about_pokemon" to true.
- If the conversation is not about Pokémon, or if the user
changed the topic in their last message, set it to false.
- If unsure, output false.

### INPUT

{conversation}

### OUTPUT
    """

    return typed_gen(prompt, Summary)