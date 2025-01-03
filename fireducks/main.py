import fireducks.pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class CollegeEngagementSystem:
    def __init__(self):
        # Define college names and their typical class sizes
        self.colleges = {
            'IIT Delhi': {'size_range': (80, 120), 'sessions_per_day': 6},
            'IIT Bombay': {'size_range': (75, 110), 'sessions_per_day': 6},
            'NIT Trichy': {'size_range': (90, 130), 'sessions_per_day': 5},
            'BITS Pilani': {'size_range': (85, 125), 'sessions_per_day': 5},
            'VIT Vellore': {'size_range': (100, 150), 'sessions_per_day': 7},
            'MIT Manipal': {'size_range': (95, 140), 'sessions_per_day': 6},
            'SRM Chennai': {'size_range': (100, 145), 'sessions_per_day': 6},
            'DTU Delhi': {'size_range': (90, 135), 'sessions_per_day': 5}
        }
        
        # Session timings (24-hour format)
        self.session_timings = {
            1: ('09:00', '10:30'),
            2: ('10:45', '12:15'),
            3: ('12:30', '14:00'),
            4: ('14:15', '15:45'),
            5: ('16:00', '17:30'),
            6: ('17:45', '19:15'),
            7: ('19:30', '21:00')
        }

    def generate_mock_data(self, num_days=5):
        """Generate mock face data for multiple colleges and sessions."""
        all_data = []
        base_date = datetime.now().date() - timedelta(days=num_days)

        for _ in range(num_days):
            current_date = base_date + timedelta(days=_)
            
            # Generate data for each college
            for college_name, college_info in self.colleges.items():
                num_sessions = college_info['sessions_per_day']
                
                # Generate data for each session
                for session in range(1, num_sessions + 1):
                    session_start, session_end = self.session_timings[session]
                    num_students = random.randint(*college_info['size_range'])
                    
                    # Generate individual student data
                    session_data = self._generate_session_data(
                        num_students,
                        current_date,
                        session_start,
                        session_end,
                        college_name,
                        session
                    )
                    all_data.extend(session_data)

        return pd.DataFrame(all_data)

    def _generate_session_data(self, num_students, date, start_time, end_time, college_name, session_num):
        """Generate data for a single session."""
        zones = ['left', 'center', 'right']
        zone_weights = [0.3, 0.4, 0.3]
        emotions = ['neutral', 'happy', 'sad', 'angry', 'surprise', 'fear', 'disgust']
        emotion_weights = [0.5, 0.2, 0.1, 0.05, 0.1, 0.025, 0.025]

        session_data = []
        session_start = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        session_end = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")

        for student_idx in range(num_students):
            timestamp = session_start + timedelta(
                minutes=random.randint(0, int((session_end - session_start).total_seconds() / 60))
            )

            zone = np.random.choice(zones, p=zone_weights)
            x1 = np.random.randint(100, 800)
            y1 = np.random.randint(100, 400)
            width = np.random.randint(100, 150)
            height = np.random.randint(120, 180)

            session_data.append({
                'face_id': f'face_{college_name.replace(" ", "")}_{session_num}_{student_idx+1}',
                'college_name': college_name,
                'session_number': session_num,
                'zone': zone,
                'emotion': np.random.choice(emotions, p=emotion_weights),
                'confidence': round(np.random.uniform(0.85, 1.0), 2),
                'created_at': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'position.x1': x1,
                'position.y1': y1,
                'position.x2': x1 + width,
                'position.y2': y1 + height,
                'position.center_x': x1 + width // 2,
                'position.center_y': y1 + height // 2,
                'pose.pitch': round(np.random.normal(5, 10), 2),
                'pose.yaw': round(np.random.normal(0, 15), 2),
                'pose.roll': round(np.random.normal(0, 5), 2),
                'pose.confidence': round(np.random.uniform(0.9, 1.0), 2)
            })

        return session_data

    def generate_engagement_report(self, data):
        """Generate comprehensive engagement report from the data."""
        report = {
            'overall_stats': self._calculate_overall_stats(data),
            'college_stats': self._calculate_college_stats(data),
            'session_stats': self._calculate_session_stats(data),
            'emotion_stats': self._calculate_emotion_stats(data)
        }
        return report

    def _calculate_overall_stats(self, data):
        """Calculate overall engagement statistics."""
        return {
            'total_records': len(data),
            'unique_colleges': data['college_name'].nunique(),
            'average_confidence': data['confidence'].mean(),
            'overall_engagement': self._calculate_engagement_score(data)
        }

    def _calculate_college_stats(self, data):
        """Calculate college-wise statistics."""
        return data.groupby('college_name').agg({
            'confidence': 'mean',
            'pose.confidence': 'mean',
            'face_id': 'count'
        }).round(2).to_dict('index')

    def _calculate_session_stats(self, data):
        """Calculate session-wise statistics."""
        return data.groupby(['college_name', 'session_number']).agg({
            'confidence': 'mean',
            'face_id': 'count'
        }).round(2).to_dict('index')

    def _calculate_emotion_stats(self, data):
        """Calculate emotion distribution statistics."""
        return data.groupby(['college_name', 'emotion']).size().unstack(fill_value=0).to_dict('index')

    def _calculate_engagement_score(self, data):
        """Calculate overall engagement score."""
        # Simplified engagement score calculation
        emotion_weights = {
            'neutral': 0.7,
            'happy': 1.0,
            'sad': 0.3,
            'angry': 0.2,
            'surprise': 0.6,
            'fear': 0.3,
            'disgust': 0.2
        }
        
        data['emotion_score'] = data['emotion'].map(emotion_weights)
        engagement_score = (
            (data['confidence'] * 0.3) +
            (data['pose.confidence'] * 0.3) +
            (data['emotion_score'] * 0.4)
        ).mean() * 100
        
        return round(engagement_score, 2)

    def save_to_csv(self, data, filename="college_face_data.csv"):
        """Save the generated data to CSV."""
        data.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def generate_report_file(self, report, filename="engagement_report.txt"):
        """Generate a formatted report file."""
        with open(filename, 'w') as f:
            f.write("COLLEGE ENGAGEMENT ANALYSIS REPORT\n")
            f.write("=" * 40 + "\n\n")
            
            # Overall Statistics
            f.write("OVERALL STATISTICS\n")
            f.write("-" * 20 + "\n")
            for key, value in report['overall_stats'].items():
                f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            f.write("\n")
            
            # College-wise Statistics
            f.write("COLLEGE-WISE STATISTICS\n")
            f.write("-" * 20 + "\n")
            for college, stats in report['college_stats'].items():
                f.write(f"\n{college}:\n")
                for metric, value in stats.items():
                    f.write(f"  {metric.replace('_', ' ').title()}: {value}\n")
            
            # Session-wise Statistics
            f.write("\nSESSION-WISE STATISTICS\n")
            f.write("-" * 20 + "\n")
            for (college, session), stats in report['session_stats'].items():
                f.write(f"\n{college} - Session {session}:\n")
                for metric, value in stats.items():
                    f.write(f"  {metric.replace('_', ' ').title()}: {value}\n")

def main():
    # Initialize the system
    system = CollegeEngagementSystem()
    
    # Generate mock data
    print("Generating mock data...")
    data = system.generate_mock_data(num_days=5)
    
    # Save raw data to CSV
    system.save_to_csv(data)
    
    # Generate and save report
    print("Generating engagement report...")
    report = system.generate_engagement_report(data)
    system.generate_report_file(report)
    
    print("Analysis complete! Check engagement_report.txt for detailed results.")

if __name__ == "__main__":
    main()