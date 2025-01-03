import os
import cv2
import numpy as np
from face_detection import detect_faces  # replace your_module with the actual module name

def test_detection():
    # Test image path - update this to your image path
    image_path = "photo_1.jpg"
    
    try:
        # Read image directly using cv2
        img = cv2.imread(image_path)
        if img is None:
            raise Exception(f"Could not read image from {image_path}")
            
        # Try face detection
        faces = detect_faces(img, threshold=0.7)
        
        if faces:
            print(f"Found {len(faces)} faces!")
            
            # Draw rectangles around detected faces
            for face_id, face_info in faces.items():
                facial_area = face_info['facial_area']
                cv2.rectangle(
                    img,
                    (facial_area[0], facial_area[1]),
                    (facial_area[2], facial_area[3]),
                    (0, 255, 0),
                    2
                )
                
            # Save the output
            output_path = "detected_faces.jpg"
            cv2.imwrite(output_path, img)
            print(f"Saved result to {output_path}")
        else:
            print("No faces detected")
            
    except Exception as e:
        print(f"Error during detection: {e}")

if __name__ == "__main__":
    test_detection()