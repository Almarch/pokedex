from .llm import llm, tokenizer
from .config import config
from vllm import SamplingParams
import numpy as np

# get "yes" and "no" first tokens
token_yes_id = tokenizer.encode("yes", add_special_tokens=False)[0]
token_no_id = tokenizer.encode("no", add_special_tokens=False)[0]

sampling_params = SamplingParams(
    temperature=0.0,
    max_tokens=1,
    logprobs=100,
)

batch_size = config["rerank"]["batch_size"]

def format_instruction(query: str, document: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "Determine if a document is relevant to answer the user query. Only respond yes or no."
        },
        {
            "role": "user",
            "content": f"Query: {query}\n\nDocument: {document}\n\nIs this document relevant to answer the query?"
        }
    ]
    
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    return prompt

def compute_logits(prompts: list[str]) -> list[float]:

    outputs = llm.generate(prompts, sampling_params, use_tqdm=False)
    
    scores = []
    for output in outputs:
        first_token_logprobs = output.outputs[0].logprobs[0]
        logprobs = np.array([
            first_token_logprobs.get(token_yes_id, float('-inf')),
            first_token_logprobs.get(token_no_id, float('-inf'))
        ])
        probs = np.exp(logprobs)

        # prob_i = exp(z_i) / sum(exp(z))
        # prob_yes / (prob_yes + prob_no)
        #     = [exp(z_yes) / sum(exp(z))] / [exp(z_yes) / sum(exp(z))] + exp(z_no) / sum(exp(z))]]
        #     = exp(z_yes) / [exp(z_yes) + exp(z_no)]]
        
        score = probs[0] / np.sum(probs)
        scores.append(float(score))
    
    return scores

def rerank(data) -> np.ndarray:

    all_prompts = [format_instruction(data.query, doc) for doc in data.documents]
    all_scores = []

    for i in range(0, len(all_prompts), batch_size):
        batch_prompts = all_prompts[i:i + batch_size]
        batch_scores = compute_logits(batch_prompts)
        all_scores.extend(batch_scores)
    
    return np.array(all_scores)