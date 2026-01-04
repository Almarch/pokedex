from .ollama import typed_gen
from .config import config
from typing import Literal
from pydantic import BaseModel
from pandas import DataFrame

class Relevance(BaseModel):
    topicality: Literal[0, 1, 2, 3]
    specificity: Literal[0, 1, 2, 3]
    completeness: Literal[0, 1, 2, 3]
    usefulness: Literal[0, 1, 2, 3]
    clarity: Literal[0, 1, 2, 3]

def get_scores(
        query: str,
        documents: list[str],
    ) -> list[Relevance]:
    
    scores = []
    for doc in documents:

        prompt = f"""
### INSTRUCTIONS

You must assess the relevance of a document to address a given query.

For more stable scoring, rate the document according to 5 aspects:

1. Topicality:
   How well the document is about the same topic as the query.

2. Specificity:
   How specific, detailed, and concrete the information is.

3. Completeness:
   How well the document covers the key aspects required to answer
   the query.

4. Usefulness:
   How useful the information is to directly build a correct and
   informative answer to the query.

5. Clarity:
   How clear, explicit, and easy to understand the information is.

Output ONLY a JSON object with 3 scores (0-3) for these aspects, as:

{{
  "topicality": 0 | 1 | 2 | 3,
  "specificity": 0 | 1 | 2 | 3,
  "completeness": 0 | 1 | 2 | 3,
  "usefulness": 0 | 1 | 2 | 3,
  "clarity": 0 | 1 | 2 | 3
}}

Do not explain your answer. Output ONLY JSON.

### QUERY

{query}

### DOCUMENT

{doc}
"""     
        score = typed_gen(
            prompt,
            Relevance,
            model = config["ollama"]["reranking"],
        )
        scores.append(score)
    return scores

def combine_scores(
        scores: DataFrame,
        power: float = 1.5,
        weights: dict = {
            "topicality": 6,
            "completeness": 3,
            "usefulness": 3,
            "specificity": 2,
            "clarity": 1
        }
    ) -> list[float]:
    weights = [weights[k] for k in scores]
    score_max = sum([w * 3**power for w in weights])
    final_score = scores**power @ weights
    return final_score / score_max

def select_docs(
        docs: DataFrame,
        threshold: float = 0.7,
        n_target_docs: int = 5,
    ) -> DataFrame:
    
    docs = docs.copy()
    if (docs["rank"] > threshold).sum() >= n_target_docs:
        docs = docs[docs["rank"] > threshold]
    else:
        docs = docs.sort_values(by="rank", ascending=False)
        docs = docs.head(n_target_docs)
    return docs
