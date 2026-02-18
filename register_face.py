import cv2
import face_recognition
import numpy as np
import pymysql
import pickle
import time
import sys

def db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Pooja@91",
        database="face_attendance"
    )

name = input("Enter your name: ").strip()

cap = cv2.VideoCapture(0)

print("📷 Camera opening... face will capture in 3 seconds")

time.sleep(3)

ret, frame = cap.read()
cap.release()
cv2.destroyAllWindows()

if not ret:
    print("❌ Camera capture failed")
    exit()

frame = np.ascontiguousarray(frame, dtype=np.uint8)
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

faces = face_recognition.face_locations(rgb)

if len(faces) != 1:
    print("❌ Make sure only ONE face is visible")
    exit()

encoding = face_recognition.face_encodings(rgb, faces)[0]

conn = db()
cur = conn.cursor()

cur.execute(
    "INSERT INTO users (name, face_encoding) VALUES (%s, %s)",
    (name, pickle.dumps(encoding))
)

conn.commit()
conn.close()

print("✅ Face captured and stored in MySQL successfully!")
