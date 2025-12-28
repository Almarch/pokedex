from .sorry import sorry
from .format_rag import format_rag
from .summarize import summarize
from .rag import name_search, vector_search

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

        out = summarize(self.body["messages"])
        summary, language, is_about_pokemon, mentioned_pokemons = out.model_dump().values()

        print("Summary:", summary)
        print("Language:", language)
        print("Is about Pokémon:", is_about_pokemon)
        print("Mentioned Pokémons:", mentioned_pokemons)

        keep_going = True
        rag = []

        if len(mentioned_pokemons) > 0:
            rag += name_search(mentioned_pokemons, language)

        if not is_about_pokemon:
            instructions = sorry("not_about_pokemon")
            keep_going = False
        
        if language == "other":
            instructions = sorry("other_language")
            keep_going = False

        if keep_going:
            rag += vector_search(summary, language)
            print("Retrieved context:", rag)
            instructions = format_rag(rag)

        self.set_instructions(instructions)
        return self.body


    
