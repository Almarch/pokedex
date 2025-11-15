from .ollama import typed_gen
from pydantic import BaseModel

class Format(BaseModel):
    output: bool

def is_about_pokemon(
    self,
    conversation,
):
    prompt = f"""
### INSTRUCTIONS

You are an assistant specialized in detecting Pokémon topics.
You receive a conversation as input.
You must decide if the latest message from the user is about Pokémon,
considering the context of the conversation.

Return the result **only** as JSON, with a single field:

{{
  "output": true
}}

Rules:
1. If the conversation is about Pokémon, set "output" to true.
2. If the conversation is not about Pokémon, or if the user changed the topic in their last message, set it to false.
3. If unsure, output false.
4. Output nothing else—no explanations, no extra text, only the JSON.

### INPUT

{conversation}

### OUTPUT

"""
    return typed_gen(prompt, Format)