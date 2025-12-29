from .intro import intro

def format_rag(
    rag,
):
    rag = str(rag)
    prompt = intro() + f"""
Some information has been retrieved to help you build the most
appropriate answer. Use this information but do not mention it to the
user: they don't need to know where does your knowledge come from.

Do not rely on your prior knowledge about Pokémons.
Only use the information provided below to answer the user.

### INFORMATION

{rag}
"""
    return prompt