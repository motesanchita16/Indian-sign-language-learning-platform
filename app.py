from flask import Flask, render_template, Response, request, jsonify, redirect, url_for, flash, session
import os, random, string, cv2, atexit
from datetime import datetime
from database import db, User, UserProgress, count_users, count_active_users
from models.sign_model import SignLanguageModel

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = "secret123"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "progress.db")

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ---------------- CAMERA & MODEL ----------------
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

model = SignLanguageModel()
latest_label = ""

# ---------------- CLEANUP ----------------
@atexit.register
def cleanup():
    if camera.isOpened():
        camera.release()

# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html", today_letter=random.choice(string.ascii_uppercase))

# ---------------- AUTH ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            user = User(
                username=request.form["username"],
                email=request.form["email"],
                password=request.form["password"]
            )
            db.session.add(user)
            db.session.commit()
            flash("Registered successfully")
            return redirect(url_for("login"))
        except:
            flash("User already exists")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"]
        ).first()
        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("index"))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- PAGES ----------------
@app.route("/learn")
def learn():
    return render_template("learn.html", letters=list(string.ascii_uppercase))

@app.route("/recognize")
def recognize():
    return render_template("recognize.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

# ---------------- QUIZ API ----------------
@app.route("/quiz_question")
def quiz_question():
    return jsonify({"letter": random.choice(string.ascii_uppercase)})

@app.route("/get_label")
def get_label():
    return latest_label or ""

@app.route("/check_answer", methods=["POST"])
def check_answer():
    data = request.get_json()
    return jsonify({
        "correct": data.get("expected", "").upper() == (latest_label or "").upper(),
        "detected": latest_label
    })

@app.route("/save_score", methods=["POST"])
def save_score():
    entry = UserProgress(
        username=request.form.get("username", "Anonymous"),
        score=int(request.form.get("score", 0)),
        date=datetime.now()
    )
    db.session.add(entry)
    db.session.commit()
    return ("", 204)

# ---------------- PROGRESS ----------------
@app.route("/progress")
def progress():
    data = UserProgress.query.all()
    return render_template("progress.html", data=data)

# ---------------- ADMIN ----------------
@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template(
        "admin_dashboard.html",
        total_users=count_users(),
        active_users=count_active_users()
    )

# ---------------- VIDEO STREAM ----------------
def gen_frames():
    global latest_label

    while True:
        success, frame = camera.read()
        if not success:
            continue

        frame, label = model.process_frame(frame)
        if label:
            latest_label = label

        _, buffer = cv2.imencode(".jpg", frame)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame")

# ---------------- START ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, threaded=True)
