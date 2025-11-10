import json
import re
from .qdrant import qdrant
from .sorry import sorry
from .format_rag import format_rag
from .embed import embed
from .summarize import summarize

class Agent():
    def __init__(self, body):
        self.body = body
        self.qdrant = qdrant

    def set_instructions(self, instructions):
        system_message = {
            "role": "system",
            "content": instructions
        }
        self.body["messages"].insert(0, system_message)
    
    def process(self):

        if is_about_pokemon(self.body["messages"]):

            query = summarize(self.body["messages"])
            query = embed(query)

            rag = self.qdrant.query_points(
                collection_name="pokemons",
                query = query,
                limit = 5
            )
            rag = str([rag.points[i].payload for i in range(len(rag.points))])
            instructions = format_rag(rag)

        else :
            instructions = sorry()

        self.set_instructions(instructions)
        return self.body


    
