# capture_windows.py
import cv2
import sys
import os

def capture_windows():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        sys.exit("Failed to open camera")
    
    ret, frame = cap.read()
    if not ret:
        cap.release()
        sys.exit("Failed to capture image")
    
    # Save to a location accessible by both Windows and WSL
    photo_path = os.path.abspath(sys.argv[1])
    cv2.imwrite(photo_path, frame)
    cap.release()

if __name__ == "__main__":
    capture_windows()