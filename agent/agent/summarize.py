from .ollama import typed_gen
from pydantic import BaseModel
from typing import Literal, List

class Output(BaseModel):
    summary: str
    language: Literal["fr", "en", "other"]
    is_about_pokemon: bool
    mentioned_pokemon: List[str]

class Format(BaseModel):
    output: Output

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
4. Identify if specific Pokémons are mentioned.

Task 1: Conversation summary:
- The summary must capture the main points of the last message.
- Ther rest of the conversation is there to provide context and to
better understand the last message.
- The summary must be at maximum a few sentences long.
- The summary must be written in the same language as
the conversation, especially the last message from the user.

Task 2: Simply identify the language of the conversation.
- "fr" for French
- "en" for English
- "other" otherwise.

Task 3: Identify if the conversation is about Pokémon.
- If the conversation is about Pokémon, set "is_about_pokemon" to true.
- If the conversation is not about Pokémon, or if the user
changed the topic in their last message, set it to false.
- If unsure, output false.

Task 4: Identify Pokémons mentioned in the last message.
- Identify if the last message explicitely mention specific Pokémons.
- The rest of the conversation is there to provide context and to
better understand the last message. The last message could mention a Pokémon
specifically named in a previous message.
- If you have a doubt, consider that weird or uncommon names could be Pokémons.
- Output them as as a list.

### INPUT

{conversation}

### OUTPUT
    """

    return typed_gen(prompt, Format)