from .instructions import sorry, format_rag
from .summarize import summarize
from .rag import name_search, vector_search, pokemon_synthese
from .regex import pokemon_match

class Agent():
    def __init__(self, body):
        self.body = body

    def set_instructions(self, instructions):
        system_message = {
            "role": "system",
            "content": instructions
        }
        self.body["messages"].insert(0, system_message)
    
    def process(self):

        keep_going = True
        messages = self.body["messages"]

        # Get the summary and language of the conversation
        out = summarize(messages)
        summary, language, is_about_pokemon = out.model_dump().values()

        print("Summary:", summary)
        print("Language:", language)

        if language == "other":
            instructions = sorry("other_language")
            keep_going = False

        # find explicitely named pokémons
        conv = "\n".join([msg["content"] for msg in messages])
        mentioned_pokemons = pokemon_match(conv, language)
        if len(mentioned_pokemons) > 0:
            is_about_pokemon = True

        print("Is about Pokémon:", is_about_pokemon)
        print("Mentioned Pokémons:", mentioned_pokemons)

        if not is_about_pokemon:
            instructions = sorry("not_about_pokemon")
            keep_going = False

        # RAG
        if keep_going:
            rag = []
            if len(mentioned_pokemons) > 0:
                rag += name_search(mentioned_pokemons, language)
            rag += vector_search(summary, language)

            rag = [pokemon_synthese(doc, language) for doc in rag]

            print("Retrieved context:", rag)
            instructions = format_rag(rag)

        self.set_instructions(instructions)
        return self.body


    