from qdrant_client import AsyncQdrantClient
from .config import config, Languages, default_language
from .ollama import embed
from sklearn.metrics.pairwise import cosine_similarity
from qdrant_client.http import models
import uuid
import numpy as np
from pandas import DataFrame
import asyncio

qdrant = AsyncQdrantClient(url = config["qdrant"]["url"])

async def fill(
        names: DataFrame,
        flavors: DataFrame,
        language: Languages = default_language,
        threshold: float = .9, # cosinus similarity from which we consider 2 vectors as redondant
    ) -> None:
    collection_descriptions = f"description_{language}"
    collection_names = f"name_{language}"
    
    await qdrant.delete_collection(collection_name = collection_descriptions)
    await qdrant.delete_collection(collection_name = collection_names)
    lorem_ipsum = await embed("lorem ipsum")
    await qdrant.create_collection(
        collection_name = collection_descriptions,
        vectors_config=models.VectorParams(
            size= len(lorem_ipsum),
            distance=models.Distance.COSINE
        )
    )
    await qdrant.create_collection(
        collection_name = collection_names,
        vectors_config = models.VectorParams(
            size = 1,
            distance = models.Distance.COSINE
        )
    )

    for id in names["pokemon_species_id"].unique().tolist():
    
        # Collect the pokemon name & description
        name = names[names["pokemon_species_id"] == id]["name"].tolist()[0]
        genus = names[names["pokemon_species_id"] == id]["genus"].tolist()[0]
        flavor_list = flavors[flavors["species_id"] == id]["flavor_text"].tolist()
        flavor_list = [x.replace("\r", "").replace("\n", " ") for x in flavor_list]
        
        # embeddings
        vector_list = await asyncio.gather(
            *(embed(x) for x in flavor_list)
        )
        
        # remove redundant descriptions
        if len(vector_list) == 0:
            continue
            
        elif len(vector_list) == 1:
            keep = [True]
            
        elif len(vector_list) > 1:
            
            ## step 1: compute all cosines
            X = np.asarray(vector_list, dtype=float)
            C = cosine_similarity(X)
            
            ## step 2: remove pairs above the threshold
            n = C.shape[0]
            keep = [True] * n
            for i in range(n):
                for j in range(i):
                    if C[i, j] > threshold:
                        keep[i] = False
                        break

        # update flavors and vectors
        flavor_list = [x for i,x in enumerate(flavor_list) if keep[i]]
        vector_list = [x for i,x in enumerate(vector_list) if keep[i]]
    
        # prepare upsert
        points = [
            models.PointStruct(
                id = uuid.uuid4().int >> 64,
                vector = vector_list[i],
                payload={
                    "id": int(id),
                    "name": name,
                    "type": genus,
                    "description": flavor_list[i],
                }
            )
            for i in range(sum(keep))
        ]
    
        # upsert
        await qdrant.upsert(
            collection_name = collection_descriptions,
            points = points
        )

        # also keep the pokemon name
        await qdrant.upsert(
            collection_name = collection_names,
            points=[models.PointStruct(
                id=id,
                vector=[0.0],
                payload={"name": name}
            )]
        )
