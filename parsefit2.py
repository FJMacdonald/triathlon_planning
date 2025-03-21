import matplotlib.pyplot as plt
from fitparse import FitFile
import os


def extract_workout_data(file_path):
    durations = []  # Will store [start, end] pairs (either time in minutes or distance in km)
    zones = []
    is_time_based = False
    
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return None, None, None
        
        with open(file_path, 'rb') as f:
            fitfile = FitFile(f)
            for record in fitfile.get_messages('workout_step'):
                distance = record.get_value('duration_distance')
                time = record.get_value('duration_time')
                duration_type = record.get_value('duration_type')
                intensity = record.get_value('intensity')
                notes = record.get_value('notes')
                
                # Skip steps without a usable duration (e.g., repeat steps)
                if duration_type == 'repeat_until_steps_cmplt':
                    continue
                
                # Determine if this is time-based or distance-based
                if time is not None and distance is None:
                    duration = time / 60  # Convert seconds to minutes
                    is_time_based = True
                elif distance is not None and time is None:
                    duration = distance / 1000  # Convert meters to kilometers
                    is_time_based = False
                else:
                    continue  # Skip if neither or both are present (ambiguous)
                
                # Map intensity/notes to zone numbers
                if intensity == 'warmup' or intensity == 'cooldown' or (notes and 'Zone 1' in notes):
                    zone = 1
                elif notes and 'Zone 2' in notes:
                    zone = 2
                elif notes and 'Zone 3' in notes:
                    zone = 3
                elif intensity == '4' or (notes and 'Zone 4' in notes):
                    zone = 4
                elif notes and 'Zone 5' in notes:
                    zone = 5
                else:
                    zone = 1  # Default to Zone 1 if unclear
                
                durations.append([0, duration])
                zones.append(zone)
                
        return durations, zones, is_time_based
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None

# Updated plot_workout to handle both
def plot_workout(durations, zones, is_time_based):
    if not durations or not zones:
        print("No data to plot.")
        return
    
    # zone_colors = {1: 'blue', 2: 'green', 3: 'orange', 4: 'red', 5: 'purple'}
    zone_colors = {
        1: 'cyan',
        2: 'blue',
        3: 'purple',
        4: 'pink',
        5: 'red'
    }
    zone_distances = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for dur_pair, zone in zip(durations, zones):
        zone_distances[zone] += dur_pair[1]
    
    plt.figure(figsize=(10, 6))
    current_x = 0
    legend_handles = {}
    
    for i, (dur_pair, zone) in enumerate(zip(durations, zones)):
        x = [current_x, current_x + dur_pair[1]]
        y = [zone, zone]
        color = zone_colors[zone]
        
        plt.step(x, y, where='pre', color='black', linewidth=1.5)
        line, = plt.plot(x, y, color=color)
        plt.fill_between(x, 0, y, color=color, alpha=0.8)
        
        mid_x = (x[0] + x[1]) / 2
        plt.annotate(f'{dur_pair[1]:.2f} {"min" if is_time_based else "km"}', (mid_x, zone), 
                     textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10)
        
        if zone not in legend_handles:
            legend_handles[zone] = line
        
        current_x = x[1]
    
    unit = "min" if is_time_based else "km"
    legend_labels = [f'Zone {zone}: {zone_distances[zone]:.2f} {unit}' for zone in sorted(zone_distances.keys()) if zone_distances[zone] > 0]
    plt.legend(handles=[legend_handles[zone] for zone in sorted(zone_distances.keys()) if zone_distances[zone] > 0], 
               labels=legend_labels, loc='upper right')
    
    total = sum(dur_pair[1] for dur_pair in durations)
    plt.text(0.5, -0.1, f'Total: {total:.2f} {unit}', ha='center', va='center', 
             transform=plt.gca().transAxes, fontsize=12)
    
    plt.xlabel('Time (min)' if is_time_based else 'Distance (km)')
    plt.ylabel('Zone')
    plt.title(f'Workout Intensity Zones by {"Time" if is_time_based else "Distance"}')
    plt.yticks([1, 2, 3, 4, 5])
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Usage
#file_path = 'RHR9.FIT'
file_path = 'RMI2.FIT'
durations, zones, is_time_based = extract_workout_data(file_path)
plot_workout(durations, zones, is_time_based)