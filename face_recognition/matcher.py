import numpy as np
from scipy.spatial.distance import euclidean, cosine

class Matcher:
    def __init__(self, cosine_min=0.6, l2_max=1.0):
        # We'll use these thresholds to validate matches
        self.cosine_min = cosine_min
        self.l2_max = l2_max

    def is_valid_match(self, score, metric='cosine'):
        """
        Validates match based on threshold.
        """
        if metric == 'cosine':
            return score >= self.cosine_min
        elif metric == 'l2':
            return score <= self.l2_max
        return False

    def find_best_match(self, query_embedding, database_faces):
        """
        Finds the best matching profile in the database.
        database_faces: list of dicts (the format of faces.json)
        Returns: (person_id, name, score) or (None, "Unknown", 0.0)
        """
        best_id = "None"
        best_name = "Unknown"
        max_similarity = -1.0
        
        # Ensure query embedding is ready for comparison
        q_emb = np.array(query_embedding).flatten()
        
        for person in database_faces:
            p_id = person.get("person_id")
            p_name = person.get("name")
            
            # Person can have multiple embeddings for robustness
            p_embs = person.get("embeddings", [])
            
            for emb_data in p_embs:
                p_emb = np.array(emb_data).flatten()
                
                # Use Cosine Similarity (1 - cosine distance)
                # Cosine distance ranges [0, 2], so 1 - dist ranges [-1, 1]
                sim = 1.0 - cosine(q_emb, p_emb)
                
                if sim > max_similarity:
                    max_similarity = sim
                    best_id = p_id
                    best_name = p_name
                    
        # Apply validation threshold
        if self.is_valid_match(max_similarity, metric='cosine'):
            return best_id, best_name, max_similarity
            
        return "None", "Unknown", max_similarity

# Instance helper for global access
def find_best_match(embedding, db):
    matcher = Matcher()
    return matcher.find_best_match(embedding, db)

def is_valid_match(score):
    return Matcher().is_valid_match(score)
