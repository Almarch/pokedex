from .instructions import sorry, format_docs
from .summarize import summarize
from .retrieve import name_search, vector_search, pokemon_synthese
from .regex import pokemon_match
from .rerank import get_scores, combine_scores, select_docs
import pandas as pd

class Agent():
    def __init__(self, body):
        self.body = body

    def process(self):
        instructions = self.get_instructions()
        system_message = {
            "role": "system",
            "content": instructions
        }
        self.body["messages"].insert(0, system_message)
        return self.body

    def get_instructions(self):

        messages = self.body["messages"]

        # Get the summary and language of the conversation
        (
            summary,
            language,
            is_about_pokemon
        ) = summarize(messages).values()

        print("Summary:", summary)
        print("Language:", language)

        if language == "other":
            return(sorry("other_language"))

        # find explicitely named pokémons
        conv = "\n".join([
                msg["content"] for msg in messages
        ])
        mentioned_pokemons = pokemon_match(conv, language)
        if len(mentioned_pokemons) > 0:
            is_about_pokemon = True

        print("Is about Pokémon:", is_about_pokemon)
        print("Mentioned Pokémons:", mentioned_pokemons)

        if not is_about_pokemon:
            return(sorry("not_about_pokemon"))

        dv = pd.DataFrame(vector_search(summary, language))
        dv["source"] = "vector"
        if len(mentioned_pokemons) > 0:
            dn = pd.DataFrame(name_search(mentioned_pokemons, language))
            dn["source"] = "regex"
            docs = pd.concat([dv, dn], ignore_index=True)
            docs = docs.drop_duplicates(subset=["qdrant_id"])
        else:
            docs = dv
        print(docs.value_counts("name"))

        docs["synthese"] = [
            pokemon_synthese(
                row.to_dict(),
                language
            ) for _, row in docs.iterrows()
        ]

        scores = get_scores(summary, docs["synthese"])
        scores = pd.DataFrame(scores)
        scores["rank"] = combine_scores(scores)
        docs = pd.concat([docs,scores],axis=1)

        docs = select_docs(docs)
        docs = docs["synthese"].to_list()
        
        docs = "\n\n".join(f"- {doc}" for doc in docs)
        print(docs)

        return format_docs(docs)

    