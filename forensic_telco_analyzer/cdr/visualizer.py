import matplotlib.pyplot as plt
import pandas as pd

class CDRVisualizer:
    def __init__(self, cdr_data):
        self.data = cdr_data

    def plot_call_frequency(self, top_n=10):
        cdr_data = self.data
        # Find the column containing destination numbers
        dest_col = None
        for col in ['destination_number', 'dest_number', 'called_number', 'to_number']:
            if col in cdr_data.columns:
                dest_col = col
                break
                
        if dest_col is None:
            print("Warning: Could not find destination number column")
            return None
            
        plt.figure(figsize=(12, 6))
        call_counts = cdr_data.groupby(dest_col).size().sort_values(ascending=False).head(top_n)
        call_counts.plot(kind='bar')
        plt.title('Top Called Numbers')
        plt.xlabel('Phone Number')
        plt.ylabel('Number of Calls')
        plt.tight_layout()
        return plt

    def plot_call_duration_histogram(self):
        cdr_data = self.data
        """Plot histogram of call durations"""
        # Find the column containing call duration
        duration_col = None
        for col in ['duration', 'call_duration', 'duration_s']:
            if col in cdr_data.columns:
                duration_col = col
                break
                
        if duration_col is None:
            print("Warning: Could not find call duration column")
            return None
            
        plt.figure(figsize=(10, 6))
        cdr_data[duration_col].hist(bins=50)
        plt.title('Distribution of Call Durations')
        plt.xlabel('Duration (seconds)')
        plt.ylabel('Frequency')
        plt.tight_layout()
        return plt