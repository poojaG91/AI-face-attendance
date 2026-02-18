from flask import Flask, render_template, request, jsonify
import cv2
import face_recognition
import pymysql
import pickle
from datetime import datetime

app = Flask(__name__)

def db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Pooja@91",
        database="face_attendance"
    )

def capture_face():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_locations(rgb)

    if len(faces) != 1:
        return None

    return face_recognition.face_encodings(rgb, faces)[0]


@app.route("/")
def index():
    return render_template("index.html")


# ---------------- REGISTER FACE ----------------

@app.route("/register", methods=["POST"])
def register():
    name = request.json["name"]
    encoding = capture_face()

    if encoding is None:
        return jsonify({"msg": "Face not detected properly"})

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (name, face_encoding) VALUES (%s, %s)",
        (name, pickle.dumps(encoding))
    )

    conn.commit()
    conn.close()

    return jsonify({"msg": "Face registered successfully ✅"})


# ---------------- MARK ATTENDANCE ----------------

@app.route("/attendance", methods=["POST"])
def mark_attendance():

    new_face = capture_face()
    if new_face is None:
        return jsonify({"msg": "Face not detected"})

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT user_id, face_encoding FROM users")
    users = cur.fetchall()

    for user_id, enc in users:
        saved_face = pickle.loads(enc)

        match = face_recognition.compare_faces(
            [saved_face], new_face, tolerance=0.45
        )

        if match[0]:
            now = datetime.now()
            today = now.date()
            time_now = now.strftime("%H:%M:%S")

            # prevent duplicate same day
            cur.execute(
                "SELECT * FROM attendance WHERE user_id=%s AND date=%s",
                (user_id, today)
            )

            if cur.fetchone():
                conn.close()
                return jsonify({"msg": "Attendance already marked today ✅"})

            cur.execute(
                "INSERT INTO attendance (user_id, date, in_time, status) VALUES (%s,%s,%s,%s)",
                (user_id, today, time_now, "Present")
            )

            conn.commit()
            conn.close()

            return jsonify({"msg": "Attendance marked successfully ✅"})

    conn.close()
    return jsonify({"msg": "Face not recognized ❌"})


if __name__ == "__main__":
    app.run(debug=True)
