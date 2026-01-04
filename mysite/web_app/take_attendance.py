# web_app/take_attendance.py
import cv2
import os
import pandas as pd
from datetime import datetime
import time
# At the very top of take_attendance.py, add these lines:
from django.contrib.auth.models import User
from .models import StudentData

def attendance_taker():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    trainer_path = os.path.join(BASE_DIR, "trainer", "trainer.yml")
    attendance_dir = os.path.join(BASE_DIR, "attendance")
    os.makedirs(attendance_dir, exist_ok=True)
    if not os.path.exists(trainer_path):
        raise FileNotFoundError("Model not trained yet! Go to 'Train Model' first.")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(trainer_path)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    if face_cascade.empty():
        raise RuntimeError("Face detector failed to load")

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(3, 640)
    cam.set(4, 480)
    time.sleep(1.0)

    if not cam.isOpened():
        raise RuntimeError("Camera not accessible")

    roll_present = set()
    start_time = time.time()
    timeout = 60  # seconds

    print("Attendance in progress... Show your face clearly. Auto-stop in 60s.")

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 6, minSize=(100, 100))

        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]
            try:
                roll_id, confidence = recognizer.predict(roi)
                if confidence < 80:  # Good match
                    roll_present.add(int(roll_id))
                    text = f"Roll: {roll_id}"
                    color = (0, 255, 0)
                else:
                    text = "Unknown"
                    color = (0, 0, 255)

                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
                cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            except:
                pass

        # Timer display
        remaining = int(timeout - (time.time() - start_time))
        cv2.putText(frame, f"Time left: {max(0, remaining)}s (Press Q to stop)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

        cv2.imshow("Smart Attendance System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or remaining <= 0:
            break

    cam.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    if not roll_present:
        print("No students recognized.")
        return []

    # Save CSV
    today = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(attendance_dir, f"Attendance Sheet {today}.csv")
    records = []
    for roll in sorted(roll_present):
        try:
            student = StudentData.objects.get(roll=roll)
            records.append({
                "Roll": roll,
                "Name": student.name,
                "Email": student.email or "",  # if you add email field
                "Date": today,
                "Time": datetime.now().strftime("%H:%M:%S"),
                "Status": "Present"
            })
        except StudentData.DoesNotExist:
            records.append({
                "Roll": roll,
                "Name": "Unknown",
                "Email": "",
                "Date": today,
                "Time": datetime.now().strftime("%H:%M:%S"),
                "Status": "Present"
            })

    pd.DataFrame(records).to_csv(file_path, index=False)
    print(f"Attendance completed: {len(roll_present)} students present")
    return list(sorted(roll_present))