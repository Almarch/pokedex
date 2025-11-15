from .sorry import sorry
from .format_rag import format_rag
from .is_about_pokemon import is_about_pokemon
from .summarize import summarize
from .get_rag import get_rag

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

        if is_about_pokemon(self.body["messages"]):

            query = summarize(self.body["messages"])
            rag = get_rag(query)
            instructions = format_rag(rag)

        else :
            instructions = sorry()

        self.set_instructions(instructions)
        return self.body


    
