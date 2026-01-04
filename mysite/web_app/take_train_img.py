# web_app/take_train_img.py
import cv2
import os
import time

def create_dataset(roll):
    NUM_IMAGES = 50
    count = 1

    # Use OpenCV's built-in cascade
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_detector = cv2.CascadeClassifier(cascade_path)
    if face_detector.empty():
        raise RuntimeError("Failed to load face detector")

    # Create Data folder
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(BASE_DIR, "Data")
    os.makedirs(data_dir, exist_ok=True)

    # Use standard VideoCapture (more reliable in Django)
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(2.0)

    if not cam.isOpened():
        raise RuntimeError("Cannot access camera")

    print(f"Capturing {NUM_IMAGES} images for Roll {roll}. Look at camera. Press 'Q' to cancel.")

    while count <= NUM_IMAGES:
        ret, frame = cam.read()
        if not ret:
            print("Failed to capture frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5, minSize=(100, 100))

        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            img_path = os.path.join(data_dir, f"Roll.{roll}.{count}.jpg")
            cv2.imwrite(img_path, face_img)

            # Show feedback
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.putText(frame, f"Captured: {count}/{NUM_IMAGES}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            count += 1

        cv2.imshow("Face Capture - Press Q to stop", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    captured = count - 1
    if captured < 10:
        raise RuntimeError(f"Only captured {captured} images. Need more for good accuracy.")

    print(f"Success! Captured {captured} images for Roll {roll}")
    return True