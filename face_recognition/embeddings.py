import torch
from facenet_pytorch import InceptionResnetV1, MTCNN
import cv2
import numpy as np

class FaceNetModel:
    def __init__(self, device='cpu'):
        self.device = torch.device(device)
        self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        self.mtcnn = MTCNN(device=self.device)

    def get_embedding(self, face_image):
        """
        Generates face embedding for individual cropped face image.
        Expects a single face image in RGB.
        """
        # Convert BGR (OpenCV) to RGB for MTCNN/FaceNet
        face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        
        # MTCNN can resize and normalize for FaceNet
        try:
            face_tensor = self.mtcnn(face_rgb)
        except Exception:
            # MTCNN internally crashes on some images where no candidates are found
            return None
        
        if face_tensor is None:
            return None
            
        # Add batch dimension and transfer to device
        face_tensor = face_tensor.unsqueeze(0).to(self.device)
        
        # Disable gradient and generate embedding
        with torch.no_grad():
            embedding = self.model(face_tensor)
            
        return embedding.cpu().numpy().flatten()

if __name__ == "__main__":
    # Simple embedding extraction test
    model = FaceNetModel()
    # Dummy black image as test
    img = np.zeros((160, 160, 3), dtype=np.uint8)
    embedding = model.get_embedding(img)
    if embedding is not None:
        print(f"Generated embedding of size: {embedding.shape}")
    else:
        print("No face detected for embedding generation.")
