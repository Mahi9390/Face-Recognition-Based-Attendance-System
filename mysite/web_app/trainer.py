# web_app/trainer.py

import cv2
import os
import numpy as np
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "Data")
TRAINER_DIR = os.path.join(BASE_DIR, "trainer")
os.makedirs(TRAINER_DIR, exist_ok=True)

# Use OpenCV's built-in cascade (more reliable)
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

def train():
    # Load face detector
    face_detector = cv2.CascadeClassifier(CASCADE_PATH)
    if face_detector.empty():
        raise RuntimeError("Failed to load face detector (Haar cascade)")

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"No dataset found at {DATASET_PATH}. Register students first.")

    if not os.listdir(DATASET_PATH):
        raise ValueError("Dataset folder is empty. Capture face images for students first.")

    faces = []
    ids = []

    print("Starting training...")

    for filename in os.listdir(DATASET_PATH):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        path = os.path.join(DATASET_PATH, filename)
        try:
            # Open as grayscale
            pil_image = Image.open(path).convert('L')
            img_numpy = np.array(pil_image, 'uint8')

            # Extract roll from filename: Roll.S001.1.jpg → S001
            parts = filename.split('.')
            if len(parts) < 3:
                print(f"Skipping invalid filename: {filename}")
                continue
            roll_str = parts[1]  # S001
            roll_id = int(''.join(filter(str.isdigit, roll_str)))

            # Detect faces in the image
            detected_faces = face_detector.detectMultiScale(
                img_numpy,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )

            if len(detected_faces) == 0:
                print(f"No face detected in {filename} - skipping")
                continue

            for (x, y, w, h) in detected_faces:
                face_crop = img_numpy[y:y+h, x:x+w]
                faces.append(face_crop)
                ids.append(roll_id)
                print(f"Added face from {filename} (Roll: {roll_id})")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue

    if len(faces) == 0:
        raise ValueError("No valid faces found for training. Check image quality and lighting.")

    print(f"Training on {len(faces)} face samples from {len(set(ids))} students...")

    recognizer.train(faces, np.array(ids))
    trainer_path = os.path.join(TRAINER_DIR, "trainer.yml")
    recognizer.save(trainer_path)

    print(f"Training completed! Model saved to {trainer_path}")