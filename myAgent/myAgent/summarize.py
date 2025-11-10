from .ollama import generate, encoder_window

def summarize(
    conversation,
):
    prompt = f"""
### INSTRUCTIONS

You are an assistant specialized in summarizing conversations.
You receive a conversation as input, and summarize it with
respect to its original language.

The summary must make a special emphasize on the last message.
The goal of the rest of the conversation is to add as much
context as needed to well interpret the last message.

The summary must be at maximum {encoder_window} tokens long.

### CONVERSATION

{conversation}

### SUMMARY

    """

    return generate(prompt)