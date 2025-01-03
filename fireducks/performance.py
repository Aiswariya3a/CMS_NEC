import pandas as pd
import numpy as np
import time
from typing import Dict, List, Tuple
import random

class PerformanceAnalyzer:
    def __init__(self):
        pass
    
    def time_operation(self, func, *args, **kwargs) -> Tuple[any, float]:
        """Time the execution of a function."""
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time
    
    def benchmark_groupby_operations(self, df_pd, df_fd):
        """Benchmark groupby operations."""
        # Using correct column names from your face data
        pandas_time = {}
        fireducks_time = {}
        
        # Test 1: Group by zone and calculate mean pose values
        _, pandas_time['zone_pose'] = self.time_operation(
            lambda: df_pd.groupby('zone')[['pose.pitch', 'pose.yaw', 'pose.roll']].mean()
        )
        
        _, fireducks_time['zone_pose'] = self.time_operation(
            lambda: df_fd.groupby('zone')[['pose.pitch', 'pose.yaw', 'pose.roll']].mean()
        )
        
        # Test 2: Group by emotion and calculate confidence stats
        _, pandas_time['emotion_conf'] = self.time_operation(
            lambda: df_pd.groupby('emotion')['confidence'].agg(['mean', 'std'])
        )
        
        _, fireducks_time['emotion_conf'] = self.time_operation(
            lambda: df_fd.groupby('emotion')['confidence'].agg(['mean', 'std'])
        )
        
        return pandas_time, fireducks_time

    def benchmark_filter_operations(self, df_pd, df_fd):
        """Benchmark filter operations."""
        pandas_time = {}
        fireducks_time = {}
        
        # Test 1: Filter by confidence threshold
        _, pandas_time['high_conf'] = self.time_operation(
            lambda: df_pd[df_pd['confidence'] > 0.8]
        )
        
        _, fireducks_time['high_conf'] = self.time_operation(
            lambda: df_fd[df_fd['confidence'] > 0.8]
        )
        
        # Test 2: Complex filtering
        _, pandas_time['complex'] = self.time_operation(
            lambda: df_pd[
                (df_pd['confidence'] > 0.8) & 
                (df_pd['pose.confidence'] > 0.9) & 
                (df_pd['emotion'] == 'neutral')
            ]
        )
        
        _, fireducks_time['complex'] = self.time_operation(
            lambda: df_fd[
                (df_fd['confidence'] > 0.8) & 
                (df_fd['pose.confidence'] > 0.9) & 
                (df_fd['emotion'] == 'neutral')
            ]
        )
        
        return pandas_time, fireducks_time

class EnhancedEngagementAnalyzer:
    def __init__(self, data: pd.DataFrame):
        """Initialize with the face data DataFrame."""
        self.data = data
        self.performance = PerformanceAnalyzer()
        self.prepare_data()
        
    def prepare_data(self):
        """Prepare pandas and fireducks DataFrames."""
        try:
            import fireducks.pandas as fpd
            self.scores_pandas = self.data.copy()
            self.scores_fireducks = fpd.DataFrame(self.data)
        except ImportError:
            print("Warning: fireducks not installed. Only pandas analysis will be available.")
            self.scores_fireducks = None
            
    def run_performance_analysis(self) -> Dict:
        """Run performance analysis on both pandas and fireducks."""
        results = {
            'groupby_operations': {},
            'filter_operations': {}
        }
        
        # Run groupby benchmarks
        pd_groupby, fd_groupby = self.performance.benchmark_groupby_operations(
            self.scores_pandas, self.scores_fireducks
        )
        results['groupby_operations'] = {
            'pandas': pd_groupby,
            'fireducks': fd_groupby
        }
        
        # Run filter benchmarks
        pd_filter, fd_filter = self.performance.benchmark_filter_operations(
            self.scores_pandas, self.scores_fireducks
        )
        results['filter_operations'] = {
            'pandas': pd_filter,
            'fireducks': fd_filter
        }
        
        return results

def generate_mock_face_data(num_rows: int = 20000) -> pd.DataFrame:
    """Generate mock face data matching your CSV structure."""
    zones = ['left', 'center', 'right']
    emotions = ['neutral', 'happy', 'sad', 'angry', 'surprise', 'fear', 'disgust']
    
    data = {
        'face_id': [f'face_{i}' for i in range(num_rows)],
        'zone': [random.choice(zones) for _ in range(num_rows)],
        'emotion': [random.choice(emotions) for _ in range(num_rows)],
        'confidence': [random.uniform(0.5, 1.0) for _ in range(num_rows)],
        'created_at': [
            f'2025-01-03 {random.randint(9,17):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}'
            for _ in range(num_rows)
        ],
        'position.x1': [random.randint(0, 1920) for _ in range(num_rows)],
        'position.y1': [random.randint(0, 1080) for _ in range(num_rows)],
        'position.x2': [random.randint(0, 1920) for _ in range(num_rows)],
        'position.y2': [random.randint(0, 1080) for _ in range(num_rows)],
        'position.center_x': [random.randint(0, 1920) for _ in range(num_rows)],
        'position.center_y': [random.randint(0, 1080) for _ in range(num_rows)],
        'pose.pitch': [random.uniform(-90, 90) for _ in range(num_rows)],
        'pose.yaw': [random.uniform(-90, 90) for _ in range(num_rows)],
        'pose.roll': [random.uniform(-90, 90) for _ in range(num_rows)],
        'pose.confidence': [random.uniform(0.5, 1.0) for _ in range(num_rows)]
    }
    
    return pd.DataFrame(data)

def main():
    # Generate mock data
    print("Generating mock data...")
    data = generate_mock_face_data(20000)
    
    # Initialize analyzer
    print("Initializing analyzer...")
    analyzer = EnhancedEngagementAnalyzer(data)
    
    # Run performance analysis
    print("Running performance analysis...")
    results = analyzer.run_performance_analysis()
    
    # Print results
    print("\nPerformance Analysis Results:")
    print("=" * 50)
    
    print("\nGroupBy Operations:")
    print("-" * 30)
    for op_name, times in results['groupby_operations']['pandas'].items():
        pd_time = times
        fd_time = results['groupby_operations']['fireducks'][op_name]
        improvement = ((pd_time - fd_time) / pd_time) * 100
        print(f"\n{op_name}:")
        print(f"Pandas: {pd_time:.4f} seconds")
        print(f"Fireducks: {fd_time:.4f} seconds")
        print(f"Improvement: {improvement:.1f}%")
    
    print("\nFilter Operations:")
    print("-" * 30)
    for op_name, times in results['filter_operations']['pandas'].items():
        pd_time = times
        fd_time = results['filter_operations']['fireducks'][op_name]
        improvement = ((pd_time - fd_time) / pd_time) * 100
        print(f"\n{op_name}:")
        print(f"Pandas: {pd_time:.4f} seconds")
        print(f"Fireducks: {fd_time:.4f} seconds")
        print(f"Improvement: {improvement:.1f}%")

if __name__ == "__main__":
    main()