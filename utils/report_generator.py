import pandas as pd
from database.models import Session, Student, Attendance

def generate_report(session_id):
    # Fetch the session by its ID
    session = Session.query.get(session_id)

    if not session:
        return None  # Session not found

    # Fetch all the students and their attendance for the session
    attendance_data = Attendance.query.filter_by(session_id=session_id).all()
    
    # Prepare data for the report
    data = []
    for attendance in attendance_data:
        student = Student.query.get(attendance.student_id)
        data.append({
            'Student Name': student.name,
            'Student Email': student.email,
            'Present': 'Yes' if attendance.present else 'No'
        })

    # Create a DataFrame for the report
    df = pd.DataFrame(data)

    # Add session details
    report = {
        'Session Name': session.name,
        'Trainer': session.trainer.name,
        'Date': session.date,
        'Start Time': session.start_time,
        'End Time': session.end_time,
        'Attendance': df
    }

    return report
