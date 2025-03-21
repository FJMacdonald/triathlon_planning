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
    paces = [60 / (speed * 3.6) for speed in speeds]  # Convert m/s to km/h (x3.6), then to min/km
    
    plt.figure(figsize=(12, 6))
    
    # Plot pace over distance
    plt.plot(distances, paces, color='blue', label='Pace')
    plt.fill_between(distances, 0, paces, color='blue', alpha=0.2)
    
    # Set reasonable y-axis limits based on typical running paces
    plt.ylim(min(paces) - 1, max(paces) + 1)  # Add padding
    
    total_distance = distances[-1] - distances[0]
    avg_pace = sum(paces) / len(paces)  # Simple average for display
    plt.text(0.5, -0.1, f'Total Distance: {total_distance:.2f} km\nAvg Pace: {int(avg_pace)}:{int((avg_pace % 1) * 60):02d} min/km', 
             ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
    
    plt.xlabel('Distance (km)')
    plt.ylabel('Pace (min/km)')
    plt.title('Run Pace Over Distance')
    plt.grid(True)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()

# Usage
file_path = 'morning_run.fit'
distances, speeds = extract_run_data(file_path)
plot_run(distances, speeds)

