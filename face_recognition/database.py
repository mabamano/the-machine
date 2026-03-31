import os
import numpy as np
import pickle

class EmbeddingDatabase:
    def __init__(self, storage_path="embeddings.pkl"):
        self.storage_path = storage_path
        self.embeddings = {}

    def add_embedding(self, name, embedding):
        """
        Adds embedding to the database.
        Many-to-one mapping (name -> multiple embeddings).
        """
        if name not in self.embeddings:
            self.embeddings[name] = []
        self.embeddings[name].append(embedding)

    def load(self):
        """
        Loads embeddings from storage.
        """
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'rb') as f:
                self.embeddings = pickle.load(f)
            print(f"Loaded database with {len(self.embeddings)} entries.")
        else:
            print("No existing database found.")

    def save(self):
        """
        Saves current embeddings to storage.
        """
        with open(self.storage_path, 'wb') as f:
            pickle.dump(self.embeddings, f)
        print("Database saved successfully.")

    def get_all(self):
        """
        Returns the entire database.
        """
        return self.embeddings

if __name__ == "__main__":
    # Test DB
    db = EmbeddingDatabase("test_embeddings.pkl")
    e1 = np.array([1, 2, 3])
    e2 = np.array([4, 5, 6])
    
    db.add_embedding("Alice", e1)
    db.add_embedding("Bob", e2)
    db.save()
    
    db2 = EmbeddingDatabase("test_embeddings.pkl")
    db2.load()
    print(f"Loaded database: {db2.get_all()}")
    
    os.remove("test_embeddings.pkl")
