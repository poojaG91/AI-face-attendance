import cv2
import face_recognition
import numpy as np
import pymysql
import pickle
import time
from datetime import datetime

def db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Pooja@91",
        database="face_attendance"
    )

cap = cv2.VideoCapture(0)
time.sleep(3)
ret, frame = cap.read()
cap.release()

rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
faces = face_recognition.face_encodings(rgb)

if not faces:
    print("No face detected")
    exit()

current_face = faces[0]

conn = db()
cur = conn.cursor()

cur.execute("SELECT name, face_encoding FROM users")
users = cur.fetchall()

matched_name = None

for name, encoding_blob in users:
    stored_encoding = pickle.loads(encoding_blob)
    match = face_recognition.compare_faces(
        [stored_encoding], current_face, tolerance=0.45
    )
    if match[0]:
        matched_name = name
        break

if matched_name:
    now = datetime.now()
    cur.execute(
        "INSERT INTO attendance(name, date, time) VALUES(%s,%s,%s)",
        (matched_name, now.date(), now.time())
    )
    conn.commit()
    print("Attendance marked for", matched_name)
else:
    print("Face not recognized")

conn.close()
