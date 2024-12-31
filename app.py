from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from sqlalchemy import func
from flask_socketio import SocketIO, emit
from datetime import datetime
import os
import json
import subprocess
import time
import threading
import cv2
from database.models import db, Trainer, Session, Student, Attendance, EngagementReport
from utils.report_generator import generate_report
from models.FaceAnalyzer import FaceAnalyzer
from models.engagement import calculate_engagement
from models.llm import analyze_classroom
import pandas as pd

# Flask App Initialization
app = Flask(__name__)
app.secret_key = "your_secret_key"
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'database.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
socketio = SocketIO(app, cors_allowed_origins="*")
db.init_app(app)

# File Paths
ENGAGEMENT_SCORES_FILE = "static/engagement_scores.json"
PHOTO_UPLOAD_DIR = "uploads/photos"
FACE_ANALYZER_SCRIPT = "FaceAnalyzer.py"
ENGAGEMENT_SCRIPT = "engagement.py"
last_photo_path = "output/annotated_image_1.jpg"
output_folder = "./output"

# Ensure directories exist
os.makedirs(PHOTO_UPLOAD_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)

# Utility Functions
def start_session_if_scheduled():
        while True:
            current_time = datetime.now().strftime("%H:%M")  # Get current time in HH:MM format
            with app.app_context():
            # Find the next scheduled session based on time
                session_to_start = Session.query.filter(func.strftime("%H:%M", Session.start_time) == current_time).first()
                
                if session_to_start:
                    # Start the session logic here
                    start_session(session_to_start.id)
                    break
                

        # # Sleep for 60 seconds before checking again
        # time.sleep(60)

# Background thread to monitor the session timings
def monitor_sessions():
    session_thread = threading.Thread(target=start_session_if_scheduled)
    session_thread.daemon = True
    session_thread.start()

@app.before_request
def start_monitoring_sessions():
    print("Montioring the Sessions...")
    monitor_sessions() 

def load_engagement_scores():
    """Load engagement scores from file."""
    if os.path.exists(ENGAGEMENT_SCORES_FILE):
        with open(ENGAGEMENT_SCORES_FILE, "r") as file:
            return json.load(file)
    return []

def capture_photo(photo_number):
    """Capture a photo using the camera and save it to the upload folder."""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        raise Exception("Could not open camera")
    
    ret, frame = cap.read()
    
    if not ret:
        cap.release()
        raise Exception("Failed to capture image")

    photo_path = os.path.join(PHOTO_UPLOAD_DIR, f"photo_{photo_number}.jpg")
    cv2.imwrite(photo_path, frame)
    cap.release()
    
    print(f"Photo {photo_number} captured and saved to {photo_path}")
    return photo_path

def save_engagement_scores(scores):
    """Save engagement scores to file."""
    with open(ENGAGEMENT_SCORES_FILE, "w") as file:
        json.dump(scores, file, indent=4)

def analyze_photo(photo_path):
    """Analyze a photo using FaceAnalyzer.py and engagement.py."""
    try:
        # Step 1: Run FaceAnalyzer.py
        face_analyzer_command = ["python3", FACE_ANALYZER_SCRIPT, photo_path]
        subprocess.run(face_analyzer_command, check=True)

        # Step 2: Run engagement.py
        engagement_command = ["python3", ENGAGEMENT_SCRIPT]
        result = subprocess.run(engagement_command, capture_output=True, text=True, check=True)

        return float(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        return f"Error during photo analysis: {e}"

# Routes for Classroom Monitoring
@app.route("/", methods=["GET", "POST"])
def login():
    """Handle login."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "teacher" and password == "password123":  # Simplified for demonstration
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    """Dashboard showing engagement scores."""
    if "user" not in session:
        return redirect(url_for("login"))
    engagement_scores = load_engagement_scores()
    return render_template("dashboard.html", scores=engagement_scores)


@app.route("/start-session", methods=['GET', "POST"])
def start_session(session_id):
    """Start the session and analyze engagement at regular intervals."""
    engagement_scores = []

    # Convert to datetime objects
    start_time = Session.start_time.strftime("%H:%M")
    end_time = Session.end_time.strftime("%H:%M")
    

    # Calculate the difference in minutes
    time_diff = end_time - start_time
    minutes = time_diff.total_seconds() / 60


    with app.app_context():
        # Process each photo for 5 minutes (capturing a photo every minute)
        for i in range(int(minutes)):
            # Capture photo at 1-minute intervals
            photo_path = capture_photo(i + 1)
            
            # Initialize the FaceAnalyzer and analyze the captured photo
            face_analyzer = FaceAnalyzer(photo_path)
            num_faces = face_analyzer.analyze_faces()
            
            # Save the results to a CSV (this is the face_data CSV)
            face_data_csv = os.path.join(output_folder, f"face_data_{i + 1}.csv")
            face_analyzer.save_results(output_image_path=f"{output_folder}/annotated_image_{i + 1}.jpg", output_csv_path=face_data_csv)
            
            # Calculate engagement based on the newly saved face_data CSV
            engagement_df, overall_engagement_score = calculate_engagement(face_data_csv)
            
            # Log engagement score
            print(f"Engagement Score for photo {i + 1}: {overall_engagement_score}")
            print(engagement_df)

            engagement_scores.append(overall_engagement_score)
            
            # Emit real-time engagement score to dashboard
            socketio.emit("score_update", {"photo_number": i + 1, "engagement_score": overall_engagement_score})
            
            # Wait for 1 minute before capturing the next photo
            if i < 1:
                print("Waiting for 1 minute before the next capture...")
                time.sleep(60)
        
        # Final session score (average of all engagement scores)
        session_engagement_score = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0


        # Update engagement scores file
        all_scores = load_engagement_scores()
        all_scores.append({"session": f"Session {len(all_scores) + 1}", "score": session_engagement_score})
        save_engagement_scores(all_scores)

        try:
            llm_response = analyze_classroom(photo_path)
        except Exception as e:
            return jsonify({"success": False, "error": f"LLM Analysis failed: {str(e)}"})
        # Save LLM report
        report_path = "static/classroom_analysis_report.json"
        with open(report_path, "w") as f:
            json.dump(llm_response, f, indent=4)

        llm_content = llm_response["choices"][0]["message"]["content"]

                # Store the engagement report in the database
        session = Session.query.get(session_id)
        if session:
            engagement_report = EngagementReport(
                session_id=session.id,
                score=session_engagement_score,
                report_content=llm_content,  # You can replace with actual report content
            )
            db.session.add(engagement_report)
            db.session.commit()

@app.route('/session_report')
def session_report():
    # Fetch all sessions from the database
    sessions = Session.query.all()
    return render_template('session_report.html', sessions=sessions)

@app.route('/view_report/<int:session_id>')
def view_report(session_id):
    # Fetch session data
    session = Session.query.get_or_404(session_id)
    
    # Path to CSV and JSON files for this session
    face_data_csv = os.path.join(output_folder, f"face_data_1.csv")

    # Load face data and engagement DataFrame
    if os.path.exists(face_data_csv):
        face_data = pd.read_csv(face_data_csv)
    else:
        return jsonify({"error": "Face data not found"}), 404

    # Calculate engagement_df for visualization
    engagement_df, institution_engagement_score = calculate_engagement(face_data_csv)

    overall_engagement_score = db.session.query(
        func.avg(EngagementReport.score)
    ).filter_by(session_id=session_id).scalar()
    report = EngagementReport.query.get_or_404(session_id)
    return render_template(
        'view_report.html',
        session=session,
        engagement_report=report,
        face_data=face_data.to_dict(orient='records'),
        engagement_df=engagement_df.to_dict(orient='records'),
        overall_engagement_score=overall_engagement_score,
    )

@app.route("/logout")
def logout():
    """Logout user."""
    session.pop("user", None)
    return redirect(url_for("login"))

# Routes for Database Management
@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/schedule', methods=['GET', 'POST'])
def schedule_session():
    if request.method == 'POST':
        session_data = request.form
        # Convert the date string to a datetime object
        session_date = datetime.strptime(session_data['date'], '%Y-%m-%d').date()

        new_session = Session(
            name=session_data['name'],
            trainer_id=session_data['trainer_id'],
            date=session_date,  # Pass the datetime.date object here
            start_time=session_data['start_time'],
            end_time=session_data['end_time']
        )
        db.session.add(new_session)
        db.session.commit()
        return redirect(url_for('dashboard'))  # Redirect to dashboard or a success page
    trainers = Trainer.query.all()
    return render_template('schedule_sessions.html', trainers=trainers)

@app.route('/add-trainer', methods=['GET', 'POST'])
def add_trainer():
    if request.method == 'POST':
        trainer_data = request.form
        new_trainer = Trainer(
            name=trainer_data['name'],
            email=trainer_data['email'],
            expertise=trainer_data['expertise']
        )
        db.session.add(new_trainer)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_trainer.html')

@app.route('/students', methods=['GET', 'POST'])
def manage_students():
    if request.method == 'POST':
        student_data = request.form
        new_student = Student(
            name=student_data['name'],
            email=student_data['email']
        )
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('manage_students'))
    students = Student.query.all()
    return render_template('student_management.html', students=students)

@app.route('/attendance')
def attendance():
    attendance_data = Attendance.query.all()
    return render_template('attendance.html', attendance=attendance_data)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
