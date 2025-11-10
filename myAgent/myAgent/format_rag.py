from .intro import intro

def format_rag(
    self,
    rag,
):
    prompt = intro() + f"""
Some information has been retrieved to help you build the most
appropriate answer. Use this information but do not mention to the
user: they don't need to know where does your knowledge come from.

### INFORMATION

{rag}
"""
    return prompt