from .instructions import sorry, format_docs
from .summarize import summarize
from .retrieve import name_search, vector_search, pokemon_synthese
from .regex import regex_search, double_check
from .rerank import get_scores, combine_scores, select_docs
import pandas as pd

class Agent():
    def __init__(
            self,
            body: dict
        ):
        self.body = body

    async def process(self):
        instructions = await self.get_instructions()
        system_message = {
            "role": "system",
            "content": instructions
        }
        self.body["messages"].insert(0, system_message)
        return self.body

    async def get_instructions(
            self
        ) -> str:

        messages = self.body["messages"]

        # Get the summary and language of the conversation
        (
            summary,
            elements,
            language,
            is_about_pokemon
        ) = await summarize(messages).values()

        print("Summary:", summary)
        print("Elements:", elements)
        print("Language:", language)

        if language == "other":
            return(sorry("other_language"))

        # find explicitely named pokémons
        conversation = "\n".join([
                msg["content"] for msg in messages
        ])
        mentioned_pokemons = regex_search(conversation, language)

        print("Pokémons identified with regex:", mentioned_pokemons)

        if len(mentioned_pokemons) > 0:
            mentioned_pokemons = await double_check(
                mentioned_pokemons,
                messages,
            )

        if len(mentioned_pokemons) > 0:
            is_about_pokemon = True

        print("Is about Pokémon:", is_about_pokemon)
        print("Truly mentioned Pokémons:", mentioned_pokemons)

        if not is_about_pokemon:
            return(sorry("not_about_pokemon"))
        
        # Retrieve relevant documents
        reps = []
        elements.extend([summary])
        for q in elements:
            reps.extend(await vector_search(q, language))
        dv = pd.DataFrame(reps)
        dv["source"] = "vector"

        # doc formationg
        if len(mentioned_pokemons) > 0:
            dn = pd.DataFrame(await name_search(mentioned_pokemons, language))
            dn["source"] = "regex"
            docs = pd.concat([dv, dn], ignore_index=True)
        else:
            docs = dv
        
        docs = docs.drop_duplicates(subset=["qdrant_id"])
        docs.reset_index(drop=True, inplace=True)
        print(docs.value_counts("name"))

        docs["synthese"] = [
            pokemon_synthese(
                row.to_dict(),
                language
            ) for _, row in docs.iterrows()
        ]

        # Rerank documents
        scores = await get_scores(summary, docs["synthese"])
        scores = pd.DataFrame(scores)
        scores["rank"] = combine_scores(scores)
        docs = pd.concat([docs,scores],axis=1)

        docs = select_docs(docs)
        docs = docs["synthese"].to_list()
        
        docs = "\n\n".join(f"- {doc}" for doc in docs)
        print(docs)

        return format_docs(docs)

    