# Smart Surveillance System

A modular, AI-based smart surveillance platform featuring person detection, tracking, face recognition, and behavior analysis.

## Features
- **Modular Architecture**: Independent modules for detection, face recognition, behavior analysis, and dashboard.
- **AI-Powered**:
  - Person Detection & Tracking: YOLOv8 (Ultralytics).
  - Face Recognition: FaceNet (VGGFace2).
  - Face Detection: MTCNN.
- **Behavior Analysis**: Detects loitering and predefined zone violations.
- **Modern Dashboard**: PySide6-based dark UI with real-time alerting.

## Installation
1. Ensure Python 3.x is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
### Running the Full System
To launch the integrated system:
```bash
python main.py
```

### Module Testing (Standalone)
Each module can be tested independently for debugging:
- **Detection**: `python -m detection.main`
- **Face Recognition**: `python -m face_recognition.main`
- **Behavior Analysis**: `python -m behavior.main`
- **Dashboard**: `python -m dashboard.main`

### Rebuilding the Face Database
If you add new images to the `known_faces/` folder, run the following to update the embeddings:
```bash
python -m face_recognition.rebuild_db
```

## 📜 Project Rules
This project follows a strict set of AI development rules to ensure modularity and integration safety. Please refer to [PROJECT_RULES.md](PROJECT_RULES.md) for more details.

## Project Structure
- `detection/`: YOLOv8 tracking and annotation logic.
- `face_recognition/`: Face detection and recognition using FaceNet.
- `behavior/`: Logic for suspicious activity detection (loitering/zone).
- `dashboard/`: PySide6 GUI and event logging.
- `main.py`: Central integration point.
