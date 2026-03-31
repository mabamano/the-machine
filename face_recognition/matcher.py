import numpy as np
from scipy.spatial.distance import euclidean, cosine

class Matcher:
    def __init__(self, threshold=0.8, distance_metric='euclidean'):
        """
        threshold: distance threshold for matching. 
                   Below this value (for distance) or above (for similarity) is a match.
        distance_metric: 'euclidean' or 'cosine'
        """
        self.threshold = threshold
        self.distance_metric = distance_metric

    def compare(self, embedding1, embedding2):
        """
        Compares two embeddings using the selected metric.
        Returns distance.
        """
        if self.distance_metric == 'euclidean':
            return euclidean(embedding1, embedding2)
        elif self.distance_metric == 'cosine':
            return cosine(embedding1, embedding2)
        else:
            raise ValueError(f"Unknown distance metric: {self.distance_metric}")

    def find_best_match(self, query_embedding, database_embeddings):
        """
        Finds the best match from a database.
        database_embeddings: {name: [embedding1, embedding2, ...]}
        """
        best_match = "Unknown"
        min_dist = float('inf')
        
        for name, embeddings in database_embeddings.items():
            for known_emb in embeddings:
                dist = self.compare(query_embedding, known_emb)
                if dist < min_dist:
                    min_dist = dist
                    best_match = name
                    
        if min_dist <= self.threshold:
            # Confidence calculation for Euclidean (normalized roughly)
            confidence = max(0, 100 * (1 - min_dist / self.threshold))
            return best_match, confidence
        
        return "Unknown", 0.0

if __name__ == "__main__":
    # Test Matcher
    matcher = Matcher(threshold=0.8, distance_metric='euclidean')
    
    # Dummy data
    e1 = np.ones(512)
    e2 = np.ones(512) + 0.1
    e3 = np.random.rand(512)
    
    db = {"Alice": [e1], "Bob": [e2]}
    
    res, conf = matcher.find_best_match(e1, db)
    print(f"Match: {res}, Confidence: {conf:.2f}%")
    
    # Alice and Bob's distances to Alice's embedding
    print(f"Distance to Alice: {matcher.compare(e1, e1)}")
    print(f"Distance to Bob (e2): {matcher.compare(e1, e2)}")
