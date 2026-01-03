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

You are an assistant and your role is to analyze a conversation.
You must generate ONLY a valid JSON object with exactly the following fields:
- summary
- language
- is_about_pokemon

Output ONLY JSON. Do not add explanations, comments, or extra text.

The JSON format MUST be:

{{
  "summary": "...",
  "language": "...",
  "is_about_pokemon": true | false
}}

### CRITICAL PRIORITY

The LAST message of the conversation is the PRIMARY source of information.

- Your summary MUST reflect the user's current intention expressed in the LAST message.
- Earlier messages are provided ONLY to disambiguate or contextualize the last message.
- Do NOT summarize the whole conversation.
- Do NOT average multiple topics.
- If the topic changed in the last message, IGNORE previous topics.

### TASKS

#### Task 1: Intent-focused summary of the last message

- Summarize ONLY the last user message.
- Focus on what the user is asking, requesting, or trying to achieve now.
- Use the rest of the conversation ONLY if needed to clarify references or implicit context.
- The summary must be short (at most a few sentences).
- The summary MUST be written in the same language as the last user message.

#### Task 2: Language identification

Identify the language of the LAST user message:
- "fr" for French
- "de" for German
- "es" for Spanish
- "it" for Italian
- "en" for English
- "other" otherwise

#### Task 3: Pokémon topic detection

Determine whether the LAST user message is about Pokémon:
- Set "is_about_pokemon" to true ONLY if the last message is about Pokémon.
- If the user changed topic in the last message, set it to false, even if previous messages were about Pokémon.
- If unsure, output false.

### INPUT

{conversation}

### OUTPUT
"""
    return typed_gen(prompt, Summary)