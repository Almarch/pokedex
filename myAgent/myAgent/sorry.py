from .intro import intro

def sorry(reason):
     
    prompt = intro()

    if reason == "not_about_pokemon":
        prompt += f"""
However, you have received an input question which is not related to
Pokémons. Explain the user you can't help them for this reason.
"""
    elif reason == "other_language":
        prompt += f"""
However, you have received an input question which is not in a language
you can handle (English or French). Explain the user you can't help them
for this reason.
"""

    return prompt