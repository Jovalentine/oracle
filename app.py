import os, uuid, mimetypes
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash,
    send_file, abort
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from core.pipeline import Pipeline
from core.video_pipeline import VideoPipeline
from core.db import MongoDB
from core.pdf_report import generate_forensic_pdf
# ✅ NEW IMPORT
from core.video_pdf_report import generate_video_pdf

# -----------------------------------
#           INIT
# -----------------------------------

load_dotenv()
app = Flask(__name__)

# Upload limits
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200MB (video-safe)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

SECRET = os.getenv("SECRET_KEY")
if not SECRET:
    raise RuntimeError("SECRET_KEY not set")
app.secret_key = SECRET

# Directories
UPLOAD_DIR = os.getenv("STORAGE_DIR", "data/uploads")
OUTPUT_DIR = "data/outputs"
REPORT_DIR = "data/reports"
VIDEO_DIR = "data/videos"

# Allowed formats
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

for d in (UPLOAD_DIR, OUTPUT_DIR, REPORT_DIR, VIDEO_DIR):
    os.makedirs(d, exist_ok=True)

# Core services
pipeline = Pipeline(
    os.getenv("YOLO_WEIGHTS"),
    os.getenv("CAPTION_MODEL"),
    OUTPUT_DIR
)

video_pipeline = VideoPipeline(pipeline, OUTPUT_DIR)

db = MongoDB()

# -----------------------------------
#           HELPERS
# -----------------------------------

def allowed_image(filename):
    return os.path.splitext(filename.lower())[1] in IMAGE_EXTENSIONS

def allowed_video(filename):
    return os.path.splitext(filename.lower())[1] in VIDEO_EXTENSIONS

# -----------------------------------
#           AUTH
# -----------------------------------

@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")

        if db.get_user(u, p):
            session["user"] = u
            return redirect(url_for("dashboard"))

        flash("Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -----------------------------------
#           DASHBOARD
# -----------------------------------

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    cases = db.get_cases_by_user(session["user"])
    return render_template("dashboard.html", cases=cases)

# -----------------------------------
#        IMAGE INVESTIGATION
# -----------------------------------

@app.route("/new", methods=["GET", "POST"])
def new_case():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        f = request.files.get("image")

        if not f or f.filename == "":
            flash("No image uploaded")
            return redirect(url_for("new_case"))

        if not allowed_image(f.filename):
            flash("Only JPG / PNG images allowed")
            return redirect(url_for("new_case"))

        filename = f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
        upload_path = os.path.join(UPLOAD_DIR, filename)
        f.save(upload_path)

        # AI Pipeline
        result = pipeline.run(upload_path)
        annotated_path = result["evidence"]["annotated_image"]
        result["evidence"]["image_filename"] = os.path.basename(annotated_path)

        db.save_case({
            "case_id": result["case"]["case_id"],
            "user": session["user"],
            "type": "image",
            **result
        })

        return redirect(url_for("view_case", case_id=result["case"]["case_id"]))

    return render_template("new_case.html")

# -----------------------------------
#        VIDEO INVESTIGATION
# -----------------------------------

@app.route("/new-video", methods=["GET", "POST"])
def new_video_case():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        v = request.files.get("video")

        if not v or v.filename == "":
            flash("No video uploaded")
            return redirect(url_for("new_video_case"))

        if not allowed_video(v.filename):
            flash("Unsupported video format")
            return redirect(url_for("new_video_case"))

        filename = f"{uuid.uuid4().hex}_{secure_filename(v.filename)}"
        video_path = os.path.join(VIDEO_DIR, filename)
        v.save(video_path)

        # Video Pipeline
        result = video_pipeline.run(video_path)

        result["video"] = {
            "filename": filename,
            "path": video_path
        }
        result["type"] = "video"
        result["user"] = session["user"]

        db.save_case({
            "case_id": result["case"]["case_id"],
            "user": session["user"],
            **result
        })

        return redirect(url_for("view_video_case", case_id=result["case"]["case_id"]))

    return render_template("new_video_case.html")

# -----------------------------------
#           VIEW REPORTS
# -----------------------------------

@app.route("/case/<case_id>")
def view_case(case_id):
    if "user" not in session:
        return redirect(url_for("login"))

    case = db.get_case(case_id, session["user"])
    if not case:
        flash("Case not found")
        return redirect(url_for("dashboard"))

    return render_template("report.html", result=case)

@app.route("/case/<case_id>/video")
def view_video_case(case_id):
    if "user" not in session:
        return redirect(url_for("login"))

    case = db.get_case(case_id, session["user"])
    if not case or case.get("type") != "video":
        flash("Video case not found")
        return redirect(url_for("dashboard"))

    return render_template("video_report.html", result=case)

# -----------------------------------
#        VIEW ASSETS (SECURE)
# -----------------------------------

@app.route("/view/<filename>")
def view_image(filename):
    safe_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(safe_path):
        abort(404)
    mime, _ = mimetypes.guess_type(safe_path)
    return send_file(safe_path, mimetype=mime or "image/jpeg")

@app.route("/video/<filename>")
def view_video(filename):
    safe_path = os.path.join(VIDEO_DIR, filename)
    if not os.path.exists(safe_path):
        abort(404)
    mime, _ = mimetypes.guess_type(safe_path)
    return send_file(safe_path, mimetype=mime or "video/mp4")

@app.route("/video/frame/<case_id>/<filename>")
def view_video_frame(case_id, filename):
    if "user" not in session:
        abort(403)

    case = db.get_case(case_id, session["user"])
    if not case or case.get("type") != "video":
        abort(404)

    # Use the frames_dir path stored in the DB to locate the frame
    frames_dir = case["evidence"]["frames_dir"]
    frame_path = os.path.join(frames_dir, filename)

    if not os.path.exists(frame_path):
        abort(404)

    return send_file(frame_path, mimetype="image/jpeg")

# -----------------------------------
#           UTILS
# -----------------------------------

@app.post("/delete/<case_id>")
def delete_case(case_id):
    if "user" in session:
        db.delete_case(case_id, session["user"])
        flash("Case deleted")
    return redirect(url_for("dashboard"))

# ✅ UPDATED: PDF ROUTE (Supports Video & Image)
@app.route("/case/<case_id>/pdf")
def download_pdf(case_id):
    if "user" not in session:
        return redirect(url_for("login"))

    case = db.get_case(case_id, session["user"])
    if not case:
        flash("Case not found")
        return redirect(url_for("dashboard"))

    pdf_path = os.path.join(REPORT_DIR, f"{case_id}.pdf")

    # Hook: Check type and call correct generator
    if case.get("type") == "video":
        generate_video_pdf(case, pdf_path)
    else:
        generate_forensic_pdf(case, pdf_path)

    return send_file(pdf_path, as_attachment=True)

@app.route("/health")
def health():
    return {"status": "Oracle Forensic System running"}

if __name__ == "__main__":
    app.run(port=5001, debug=True)