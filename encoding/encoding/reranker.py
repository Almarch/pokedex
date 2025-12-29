import torch
from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM
from .config import config

tokenizer = AutoTokenizer.from_pretrained(
    config["reranker"]["model"],
    padding_side=config["reranker"]["padding_side"],
    cache_dir=config["cache"]
)
model = AutoModelForCausalLM.from_pretrained(
    config["reranker"]["model"],
    cache_dir=config["cache"],
    device_map='cpu'
).eval()

prefix = config["reranker"]["prefix"]
suffix = config["reranker"]["suffix"]
max_length = config["reranker"]["max_length"]

token_false_id = tokenizer.convert_tokens_to_ids("no")
token_true_id = tokenizer.convert_tokens_to_ids("yes")
prefix_tokens = tokenizer.encode(prefix, add_special_tokens=False)
suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)

instruction = 'Given a search query, retrieve relevant documents that answer the query'

def format_instruction(query, doc):
    output = "<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc}".format(instruction=instruction,query=query, doc=doc)
    return output

def process_inputs(pairs):
    inputs = tokenizer(
        pairs, padding=False, truncation='longest_first',
        return_attention_mask=False, max_length=max_length - len(prefix_tokens) - len(suffix_tokens)
    )
    for i, ele in enumerate(inputs['input_ids']):
        inputs['input_ids'][i] = prefix_tokens + ele + suffix_tokens
    inputs = tokenizer.pad(inputs, padding=True, return_tensors="pt", max_length=max_length)
    for key in inputs:
        inputs[key] = inputs[key].to(model.device)
    return inputs

@torch.no_grad()
def compute_logits(inputs, **kwargs):
    batch_scores = model(**inputs).logits[:, -1, :]
    true_vector = batch_scores[:, token_true_id]
    false_vector = batch_scores[:, token_false_id]
    batch_scores = torch.stack([false_vector, true_vector], dim=1)
    batch_scores = torch.nn.functional.log_softmax(batch_scores, dim=1)
    scores = batch_scores[:, 1].exp().tolist()
    return scores