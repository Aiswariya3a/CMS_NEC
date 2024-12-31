# FaceAnalyzer Application

## Overview
The **FaceAnalyzer** application is an AI-powered tool for analyzing faces in an image. It uses advanced facial detection and analysis techniques to extract information such as:
- Emotion detection with confidence scores
- Head pose estimation (pitch, yaw, roll)
- Zone classification to determine which section of the image the face is located in

This project leverages libraries like OpenCV, DeepFace, NumPy, and Pandas for processing images, analyzing emotions, and generating detailed reports. 

## Features
- **Face Detection**: Identifies faces and their positions in an image.
- **Emotion Analysis**: Detects the dominant emotion for each face.
- **Head Pose Estimation**: Calculates pitch, yaw, and roll angles for each face.
- **Zone Detection**: Determines the location of the face (left, center, or right zones).
- **Annotated Output**: Saves an annotated image with visual markers for analysis.
- **CSV Report**: Generates a CSV file containing face analysis data.

---

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