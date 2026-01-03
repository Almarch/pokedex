from .ollama import typed_gen
from pydantic import BaseModel
from typing import Literal

class Summary(BaseModel):
    summary: str
    elements: list[str]
    language: Literal["fr", "de", "es", "it", "en", "other"]
    is_about_pokemon: bool

def summarize(
    conversation,
):
    
    prompt = f"""
### INSTRUCTIONS

You are an assistant analyzing a conversation.
You must generate ONLY a valid JSON object with exactly the following fields:
- summary
- elements
- language
- is_about_pokemon

Output ONLY JSON. No explanations, no extra text.

The JSON format MUST be:

{{
  "summary": "...",
  "elements": ["...", "...", "..."],
  "language": "...",
  "is_about_pokemon": true | false
}}

### CRITICAL PRIORITY

The LAST user message is the PRIMARY source of information.

- All outputs must be based primarily on the LAST message.
- Earlier messages are provided ONLY to resolve ambiguity or references.
- If the topic changed in the last message, IGNORE previous topics entirely.

### TASKS

#### Task 1: Intent-focused summary

- Summarize ONLY the user's current intention expressed in the LAST message.
- Focus on what the user wants to know or achieve now.
- The summary must be short (at most a few sentences).
- Write the summary in the same language as the LAST user message.

#### Task 2: Elements for retrieval

Generate 3 to 5 short, explicit elements that:
- Decompose the user's intent into distinct information needs.
- Are suitable as standalone search queries.
- Are phrased as neutral questions or statements, not as questions.
- Help retrieve complementary documents from a knowledge base.

Guidelines:
- Each elements should target a different aspect (definition, property, etc).
- Avoid redundancy between elements.
- Write elements in the same language as the LAST user message.

#### Task 3: Language identification

Identify the language of the LAST user message:
- "fr" for French
- "de" for German
- "es" for Spanish
- "it" for Italian
- "en" for English
- "other" otherwise

#### Task 4: Pokémon topic detection

Determine whether the LAST user message is about Pokémon:
- Set "is_about_pokemon" to true ONLY if the last message is about Pokémon.
- If the user changed topic in the last message, set it to false.
- If unsure, output false.

### INPUT

{conversation}

### OUTPUT
"""
    return typed_gen(prompt, Summary)