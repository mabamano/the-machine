import json
import os
import time
import numpy as np

# We'll need a way to serialize/deserialize numpy arrays for JSON
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class Database:
    def __init__(self, storage_path=None):
        if storage_path is None:
            # Default path following user's requirement
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            self.storage_path = os.path.join(data_dir, "faces.json")
        else:
            self.storage_path = storage_path
            
        self.faces = []
        self.load_faces()

    def load_faces(self):
        """
        Loads faces from JSON storage.
        """
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    self.faces = json.load(f)
                # Convert list embeddings back to numpy for processing if needed 
                # (usually done at processing time to keep JSON clean)
                print(f"Loaded database with {len(self.faces)} identities.")
            except Exception as e:
                print(f"Error loading database: {e}")
                self.faces = []
        else:
            print("No existing face database found. Initializing empty.")
            self.faces = []
        return self.faces

    def save_faces(self, data=None):
        """
        Saves current or provided face data to JSON storage.
        """
        if data is not None:
            self.faces = data
            
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.faces, f, cls=NumpyEncoder, indent=2)
            print(f"Database saved to {self.storage_path}")
        except Exception as e:
            print(f"Error saving database: {e}")

    def add_new_person(self, name, embedding):
        """
        Adds a new person with a unique ID and their first embedding.
        """
        # Generate new ID
        if not self.faces:
            new_id = "person_001"
        else:
            # Simple incremental ID
            last_id = self.faces[-1]["person_id"]
            num = int(last_id.split("_")[1]) + 1
            new_id = f"person_{num:03d}"
            
        new_person = {
            "person_id": new_id,
            "name": name,
            "embeddings": [embedding if isinstance(embedding, list) else embedding.tolist()],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.faces.append(new_person)
        self.save_faces()
        return new_person

    def update_person_embedding(self, person_id, embedding):
        """
        Appends a new embedding to an existing person for robustness.
        """
        for person in self.faces:
            if person["person_id"] == person_id:
                emb_list = embedding if isinstance(embedding, list) else embedding.tolist()
                # Avoid duplicates roughly by checking if similar enough? 
                # For now just append to improve robustness as requested.
                person["embeddings"].append(emb_list)
                self.save_faces()
                return True
        return False

    def get_all(self):
        return self.faces

# Exported functions for global use as requested
_db_instance = None

def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance

def load_faces():
    return get_db().load_faces()

def save_faces(data):
    get_db().save_faces(data)

def add_new_person(name, embedding):
    return get_db().add_new_person(name, embedding)

def update_person_embedding(person_id, embedding):
    return get_db().update_person_embedding(person_id, embedding)
