import matplotlib.pyplot as plt
from fitparse import FitFile
import os

def extract_run_data(file_path):
    distances = []
    speeds = []  # We'll use speed to calculate pace
    
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return None, None
        
        with open(file_path, 'rb') as f:
            fitfile = FitFile(f)
            for record in fitfile.get_messages('record'):
                distance = record.get_value('distance')  # meters
                speed = record.get_value('enhanced_speed') or record.get_value('speed')  # m/s
                
                if distance is not None and speed is not None and speed > 0:  # Avoid division by zero
                    distances.append(distance / 1000)  # Convert to km
                    speeds.append(speed)
                
        return distances, speeds
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def plot_run(distances, speeds):
    if not distances or not speeds:
        print("No data to plot.")
        return
    
    # Calculate pace in minutes per kilometer
    paces = [60 / (speed * 3.6) for speed in speeds]  # min/km
    
    plt.figure(figsize=(12, 6))
    
    # Plot pace over distance
    plt.plot(distances, paces, color='blue', label='Pace')
    plt.fill_between(distances, 0, paces, color='blue', alpha=0.2)
    
    # Convert pace to min:sec for y-axis labels
    pace_min = [int(p) for p in paces]
    pace_sec = [int((p % 1) * 60) for p in paces]
    y_ticks = [p for p in range(int(min(paces)), int(max(paces)) + 1)]  # Whole minute range
    y_labels = [f"{m}:00" for m in y_ticks]  # Format as MM:00
    
    plt.yticks(y_ticks, y_labels)
    plt.gca().invert_yaxis()  # Invert so slowest (highest) pace is at bottom
    
    total_distance = distances[-1] - distances[0]
    avg_pace = sum(paces) / len(paces)
    avg_min = int(avg_pace)
    avg_sec = int((avg_pace % 1) * 60)
    plt.text(0.5, -0.15, f'Total Distance: {total_distance:.2f} km\nAvg Pace: {avg_min}:{avg_sec:02d} min/km', 
             ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
    
    plt.xlabel('Distance (km)')
    plt.ylabel('Pace (min:sec/km)')
    plt.title('Run Pace Over Distance')
    plt.grid(True)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()

# Usage
file_path = 'morning_run.fit'
distances, speeds = extract_run_data(file_path)
plot_run(distances, speeds)

