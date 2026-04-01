from ultralytics import YOLO
import os

def download():
    model_name = "yolov8n-pose.pt"
    print(f"Checking for {model_name}...")
    # Initialize YOLO with the model name. 
    # Ultralytics will automatically download it to the current directory if it's missing.
    model = YOLO(model_name)
    if os.path.exists(model_name):
        print(f"Successfully downloaded and verified {model_name} in current directory.")
    else:
        print(f"Failed to locate {model_name} in the current directory.")

if __name__ == "__main__":
    download()
