import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import engagement

class RegionalCollegeDataGenerator:
    def __init__(self):
        # Define regions and their colleges
        self.college_data = {
            'North': {
                'IIT Delhi': {'size_range': (80, 120)},
                'DTU Delhi': {'size_range': (90, 130)},
                'NIT Kurukshetra': {'size_range': (85, 125)},
                'IIIT Delhi': {'size_range': (70, 100)},
                'Punjab Engineering College': {'size_range': (75, 115)}
            },
            'South': {
                'IIT Madras': {'size_range': (85, 125)},
                'NIT Trichy': {'size_range': (90, 130)},
                'VIT Vellore': {'size_range': (100, 150)},
                'PSG Tech Coimbatore': {'size_range': (80, 120)},
                'CEG Chennai': {'size_range': (85, 125)}
            },
            'East': {
                'IIT Kharagpur': {'size_range': (85, 125)},
                'NIT Durgapur': {'size_range': (80, 120)},
                'KIIT Bhubaneswar': {'size_range': (90, 130)},
                'Jadavpur University': {'size_range': (85, 125)},
                'BIT Mesra': {'size_range': (75, 115)}
            },
            'West': {
                'IIT Bombay': {'size_range': (85, 125)},
                'VJTI Mumbai': {'size_range': (80, 120)},
                'BITS Pilani': {'size_range': (90, 130)},
                'NIT Surat': {'size_range': (85, 125)},
                'COEP Pune': {'size_range': (80, 120)}
            }
        }

        # Emotion probabilities (based on typical classroom behavior)
        self.emotion_probs = {
            'neutral': 0.50,    # Most common
            'happy': 0.15,      # Positive engagement
            'sad': 0.10,        # Some disengagement
            'angry': 0.05,      # Rare
            'surprise': 0.10,   # Occasional
            'fear': 0.05,       # Rare
            'disgust': 0.05     # Rare
        }

        # Zone distribution (center tends to have more students)
        self.zone_probs = {
            'left': 0.30,
            'center': 0.40,
            'right': 0.30
        }

    def generate_student_data(self, num_records=500000):
        """Generate mock face detection data for students across regions and colleges."""
        data = []
        student_count = 0

        # Calculate records per region (approximately equal distribution)
        records_per_region = num_records // len(self.college_data)

        for region, colleges in self.college_data.items():
            records_remaining = records_per_region
            
            while records_remaining > 0:
                # Randomly select a college from the region
                college_name = random.choice(list(colleges.keys()))
                college_info = colleges[college_name]
                
                # Generate a batch of students for this college
                batch_size = min(
                    random.randint(*college_info['size_range']),
                    records_remaining
                )
                
                # Generate data for each student in the batch
                for _ in range(batch_size):
                    student_count += 1
                    
                    # Generate base data
                    zone = random.choices(
                        list(self.zone_probs.keys()),
                        weights=list(self.zone_probs.values())
                    )[0]
                    
                    emotion = random.choices(
                        list(self.emotion_probs.keys()),
                        weights=list(self.emotion_probs.values())
                    )[0]

                    # Generate position based on zone
                    if zone == 'left':
                        x1 = random.randint(100, 300)
                    elif zone == 'center':
                        x1 = random.randint(301, 600)
                    else:  # right
                        x1 = random.randint(601, 800)

                    y1 = random.randint(100, 400)
                    width = random.randint(100, 150)
                    height = random.randint(120, 180)
                    x2 = x1 + width
                    y2 = y1 + height
                    center_x = x1 + width // 2
                    center_y = y1 + height // 2

                    # Generate pose data based on zone
                    if zone == 'left':
                        yaw = random.normalvariate(15, 5)  # Looking slightly right
                    elif zone == 'center':
                        yaw = random.normalvariate(0, 5)   # Looking straight
                    else:  # right
                        yaw = random.normalvariate(-15, 5) # Looking slightly left

                    data.append({
                        'face_id': f'face_{student_count}',
                        'region': region,
                        'college_name': college_name,
                        'zone': zone,
                        'emotion': emotion,
                        'confidence': round(random.uniform(0.85, 1.0), 2),
                        'created_at': (
                            datetime.now() + 
                            timedelta(
                                minutes=random.randint(-120, 120)
                            )
                        ).strftime('%Y-%m-%d %H:%M:%S'),
                        'position.x1': x1,
                        'position.y1': y1,
                        'position.x2': x2,
                        'position.y2': y2,
                        'position.center_x': center_x,
                        'position.center_y': center_y,
                        'pose.pitch': round(random.normalvariate(5, 10), 2),  # Slight upward tilt
                        'pose.yaw': round(yaw, 2),
                        'pose.roll': round(random.normalvariate(0, 5), 2),  # Mostly level heads
                        'pose.confidence': round(random.uniform(0.9, 1.0), 2)
                    })
                
                records_remaining -= batch_size

        return pd.DataFrame(data)

def main():
    # Initialize the generator
    generator = RegionalCollegeDataGenerator()
    
    # Generate 500,000 records
    print("Generating 500,000 records of face data...")
    df = generator.generate_student_data(500000)
    
    # Save to CSV
    output_file = "regional_face_data_500k.csv"
    df.to_csv(output_file, index=False)
    print(f"\nData saved to {output_file}")
    
    # Print summary statistics
    print("\nData Summary:")
    print("-" * 50)
    print("\nRecords per region:")
    print(df['region'].value_counts())
    
    print("\nRecords per college (top 5):")
    print(df['college_name'].value_counts().head())
    
    print("\nEmotion distribution:")
    print(df['emotion'].value_counts(normalize=True).round(3) * 100, "%")
    
    print("\nZone distribution:")
    print(df['zone'].value_counts(normalize=True).round(3) * 100, "%")
    
    # Calculate engagement using the provided function
    try:
        print("\nCalculating engagement scores...")
        engagement_df, overall_score = engagement.calculate_engagement(output_file)
        print(f"\nOverall engagement score: {overall_score:.2f}")
        
        # Print engagement statistics by region
        print("\nEngagement scores by region:")
        region_scores = df.merge(engagement_df[['face_id', 'engagement_score']], on='face_id')
        print(region_scores.groupby('region')['engagement_score'].mean().round(2))
        
    except Exception as e:
        print(f"Error calculating engagement: {str(e)}")

if __name__ == "__main__":
    main()