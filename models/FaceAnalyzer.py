import cv2
import numpy as np
import pandas as pd
from . import face_detection
from datetime import datetime
from scipy.spatial.transform import Rotation
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class FaceAnalyzer:
    def __init__(self, image_path):
        """Initialize the FaceAnalyzer with an image path."""
        self.image_path = image_path
        self.original_image = self.load_image()
        self.image_height, self.image_width = self.original_image.shape[:2]
        self.face_data = []
        self.zones = self.define_zones()

    def load_image(self):
        """Load and validate the input image."""
        image = cv2.imread(self.image_path)
        if image is None:
            raise ValueError(f"Could not load image from {self.image_path}")
        
        # min_size = 224  # Minimum size for reliable face detection
        # if image.shape[0] < min_size or image.shape[1] < min_size:
        #     image = cv2.resize(image, (min_size, min_size))
        #     logger.warning("Image was resized to minimum dimensions for reliable detection")
        # enhanced_image = self.enhance_image(image)
        return image


    def define_zones(self):
        """Define zones based on the image width."""
        third_width = self.image_width // 3
        return {
            "left": (0, third_width),
            "center": (third_width, 2 * third_width),
            "right": (2 * third_width, self.image_width)
        }

    def calculate_head_pose(self, landmarks):
        """Calculate head pose angles using PnP."""
        try:
            model_points = np.array([
                (0.0, 0.0, 0.0),          # Nose tip
                (0.0, -330.0, -65.0),     # Chin
                (-225.0, 170.0, -135.0),  # Left eye corner
                (225.0, 170.0, -135.0),   # Right eye corner
                (-150.0, -150.0, -125.0), # Left mouth corner
                (150.0, -150.0, -125.0)   # Right mouth corner
            ])

            image_points = [
                landmarks["nose"],
                landmarks.get("chin", landmarks["nose"]),
                landmarks["left_eye"],
                landmarks["right_eye"],
                landmarks.get("mouth_left", landmarks["left_eye"]),
                landmarks.get("mouth_right", landmarks["right_eye"])
            ]
            image_points = np.array(image_points, dtype="double")

            focal_length = self.image_width
            center = (self.image_width / 2, self.image_height / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype="double")
            dist_coeffs = np.zeros((4, 1))

            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
            )
            if not success:
                raise ValueError("PnP solution failed.")

            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            rotation = Rotation.from_matrix(rotation_matrix)
            euler_angles = rotation.as_euler("xyz", degrees=True)
            pitch, yaw, roll = euler_angles

            return {
                "pitch": round(pitch, 2),
                "yaw": round(yaw, 2),
                "roll": round(roll, 2),
                "confidence": 1.0
            }
        except Exception as e:
            logger.warning(f"PnP head pose calculation failed: {str(e)}")
            return {"pitch": 0.0, "yaw": 0.0, "roll": 0.0, "confidence": 0.0}

    def detect_emotion(self, face_image):
        """Detect emotion with confidence score."""
        try:
            analysis = face_detection.analyze(
                face_image, actions="emotion", enforce_detection=False, silent=True, 
            )
            emotions = analysis[0]["emotion"]
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])
            return {"emotion": dominant_emotion[0], "confidence": round(dominant_emotion[1] / 100, 2)}
        except Exception as e:
            logger.error(f"Emotion detection error: {str(e)}")
            return {"emotion": "unknown", "confidence": 0.0}

    def determine_zone(self, center_x):
        """Determine which zone the student is located in based on x-coordinate."""
        for zone, (start, end) in self.zones.items():
            if start <= center_x < end:
                return zone
        return "unknown"

    def analyze_faces(self):
        """Main method to detect and analyze faces in the image."""
        try:
            faces = face_detection.detect_faces(self.original_image)
            for face_id, face in faces.items():
                x1, y1, x2, y2 = face["facial_area"]
                face_image = self.original_image[y1:y2, x1:x2]

                pose = self.calculate_head_pose(face["landmarks"])
                emotion_data = self.detect_emotion(face_image)
                zone = self.determine_zone((x1 + x2) // 2)

                face_data = {
                    "face_id": face_id,
                    "position": {
                        "x1": x1, "y1": y1,
                        "x2": x2, "y2": y2,
                        "center_x": (x1 + x2) // 2,
                        "center_y": (y1 + y2) // 2
                    },
                    "zone": zone,
                    "pose": pose,
                    "emotion": emotion_data["emotion"],
                    "confidence": emotion_data["confidence"],
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.face_data.append(face_data)
                self.draw_face_analysis(face_data)

            return len(self.face_data)
        except Exception as e:
            logger.error(f"Face analysis failed: {str(e)}")
            return 0

    def draw_face_analysis(self, face_data):
        """Draw analysis results on the image."""
        pos = face_data["position"]
        zone = face_data["zone"]
        text_lines = [
            f"Emotion: {face_data['emotion']} ({face_data['confidence']:.2f})",
            f"Zone: {zone}",
        ]
        for i, text in enumerate(text_lines):
            y = pos["y1"] - 10 - (i * 20)
            if y > 0:
                cv2.putText(self.original_image, text, (pos["x1"], y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    def save_results(self, output_image_path, output_csv_path):
        """Save the annotated image and CSV."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_image_path = output_image_path or f"face_analysis_{timestamp}.jpg"
        output_csv_path = output_csv_path or f"face_data_{timestamp}.csv"

        # Save annotated image
        cv2.imwrite(output_image_path, self.original_image)
        logger.info(f"Annotated image saved to {output_image_path}")

        # Save face data to CSV only if data exists
        if self.face_data:
            df = pd.json_normalize(self.face_data)
            df.to_csv(output_csv_path, index=False)
            logger.info(f"Face data saved to {output_csv_path}")
        else:
            logger.warning("No face data available to save to CSV. Saving a placeholder file with default values.")
            
            # Create a placeholder DataFrame with default values
            placeholder_columns = ["face_id", "zone", "pose.pitch", "pose.yaw", "pose.roll", "confidence", "emotion"]
            placeholder_data = [{
                "face_id": 0,
                "zone": "unknown",
                "pose.pitch": "None",
                "pose.yaw": "None",
                "pose.roll": "None",
                "confidence": "None",
                "emotion": "None"
            }]
            placeholder_df = pd.DataFrame(placeholder_data, columns=placeholder_columns)
            placeholder_df.to_csv(output_csv_path, index=False)
            logger.info(f"Placeholder face data saved to {output_csv_path}")