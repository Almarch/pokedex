from .intro import intro

def sorry():
    prompt = intro() + f"""
However, you have received an input question which is not related to
Pokémons. Explain the user you can't help them for this reason.
"""
    return prompt