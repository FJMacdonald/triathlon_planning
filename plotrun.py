import matplotlib.pyplot as plt
from fitparse import FitFile
import os


def extract_run_data(file_path):
    distances = []
    speeds = []
    
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return None, None
        
        with open(file_path, 'rb') as f:
            fitfile = FitFile(f)
            for i, record in enumerate(fitfile.get_messages('record')):
                distance = record.get_value('distance')
                speed = record.get_value('enhanced_speed') or record.get_value('speed')
                
                if distance is not None and speed is not None and speed > 0:
                    distances.append(distance / 1000)
                    speeds.append(speed)
                    if i < 5:
                        print(f"Record {i}: distance={distance} m, speed={speed} m/s")
                if speed > 10:
                    print(f"Warning: Unrealistic speed: {speed} m/s at distance {distance} m")
    
        print(f"Extracted speeds (first 5): {speeds[:5]}")
        return distances, speeds
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def plot_run(distances, speeds):
    if not distances or not speeds:
        print("No data to plot.")
        return
    
    paces = [60 / (speed * 3.6) for speed in speeds]
    paces_clipped = [min(p, 8) for p in paces]  # Cap at 8:00
    
    print(f"Speeds (first 5): {speeds[:5]}")
    print(f"Paces (min/km): {[f'{int(p)}:{int((p % 1) * 60):02d}' for p in paces[:5]]}")
    print(f"Clipped paces: {[f'{int(p)}:{int((p % 1) * 60):02d}' for p in paces_clipped[:5]]}")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(distances, paces_clipped, color='blue', label='Pace')
    ax.fill_between(distances, 8, paces_clipped, color='blue', alpha=0.2)
    
    min_pace = min(paces_clipped)
    y_ticks = [p for p in range(int(min_pace), 9)]
    y_labels = [f"{m}:00" for m in y_ticks]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.invert_yaxis()
    
    def format_coord(x, y):
        pace_min = int(y)
        pace_sec = int((y % 1) * 60)
        return f'x={x:.2f} km, y={pace_min}:{pace_sec:02d} min/km'
    ax.format_coord = format_coord
    
    total_distance = distances[-1] - distances[0]
    avg_pace = sum(paces) / len(paces)  # Unclipped avg
    avg_min = int(avg_pace)
    avg_sec = int((avg_pace % 1) * 60)
    print(f"Calculated avg pace: {avg_min}:{avg_sec:02d}")
    
    ax.text(0.5, -0.15, f'Total Distance: {total_distance:.2f} km\nAvg Pace: {avg_min}:{avg_sec:02d} min/km', 
            ha='center', va='center', transform=ax.transAxes, fontsize=12)
    
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('Pace (min:sec/km)')
    ax.set_title('Run Pace Over Distance')
    ax.grid(True)
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.show()

file_path = 'morning_run.fit'
distances, speeds = extract_run_data(file_path)
plot_run(distances, speeds)