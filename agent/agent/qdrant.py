from qdrant_client import QdrantClient
from .config import config
from .encoding import embed
from sklearn.metrics.pairwise import cosine_similarity
from qdrant_client.http import models
import uuid
import numpy as np

qdrant = QdrantClient(url = config["qdrant"]["url"])

def fill(
        names,
        flavors,
        lang = "en",
        threshold = .9, # cosinus similarity from which we consider 2 vectors as redondant
    ):
    collection_descriptions = f"description_{lang}"
    collection_names = f"name_{lang}"
    
    qdrant.delete_collection(collection_name = collection_descriptions)
    qdrant.delete_collection(collection_name = collection_names)
    qdrant.create_collection(
        collection_name = collection_descriptions,
        vectors_config=models.VectorParams(
            size= len(embed(["lorem ipsum"], type = "document")[0]),
            distance=models.Distance.COSINE
        )
    )
    qdrant.create_collection(
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
        vector_list = embed(flavor_list, type = "document")
        
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
        qdrant.upsert(
            collection_name = collection_descriptions,
            points = points
        )

        # also keep the pokemon name
        qdrant.upsert(
            collection_name = collection_names,
            points=[models.PointStruct(
                id=id,
                vector=[0.0],
                payload={"name": name}
            )]
        )
