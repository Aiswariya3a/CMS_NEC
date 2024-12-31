# FaceAnalyzer Application

## Overview
**CMS** is a real-time system that tracks student engagement in classrooms using facial expressions and head movements. 
It provides trainers and institutions with feedback on attention levels and generates reports.
This system helps regulatory bodies monitor and improve educational sessions effectively.


This project leverages libraries like OpenCV, NumPy, and Pandas for processing images, analyzing emotions, and generating detailed reports. 


## Features
- Combines facial expression recognition and head pose estimation to calculate an engagement score that accurately reflects students' attention levels and emotional states in real time.
- Provides immediate feedback to Institutions through an intuitive interface, enabling dynamic adjustment of teaching methods based on student engagement and focus levels during the session.
---

## Technical Stack
- **Face Detection** - Resnet50
- **Facial Expression Analysis** - VGG16-Face
- **Pose Estimation** - PnP Head pose estimation
- **LLM Integration** - NVDIA Neva
- **Framework** - Flask
- **Database** - Sqlite

## Getting Started
Follow these steps to clone and run the application locally.

### Prerequisites
- Python 3.7 or above
- Git

---

### Installation Steps

#### 1. Clone the Repository
```bash
git clone <repository_url>
cd <repository_name>
```

#### 2. Create a Virtual Environment
```bash
python -m venv venv
```

#### 3. Activate the Virtual Environment
- **Windows**:
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

#### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### Start the Application
Run the following command to start the application:
```bash
python app.py
```

---

## Project Structure
```
project/
│
├── app.py               # Flask app entry point
├── templates/           # HTML templates for rendering pages
│   ├── dashboard.html
│   ├── schedule_sessions.html
│   ├── add_trainer.html
│   ├── view_report.html
│   ├── student_management.html
│   ├── attendance.html
│
├── static/              # CSS, JS, images
│   ├── css/
│   ├── js/
│
├── models/              # Machine learning models
│   ├── face_analyzer.py
│   ├── engagement.py
│
├── database/            # Database and related scripts
│   ├── database_setup.py
│   ├── models.py
│
├── utils/               # Helper functions
│   ├── report_generator.py  # For generating Pandas reports
│
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

---

## Contributing
If you wish to contribute to this project, feel free to submit a pull request or open an issue for discussion.