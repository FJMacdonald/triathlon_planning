import matplotlib.pyplot as plt
from fitparse import FitFile
import os

def read_fit_file(file_path):
    try:
        # Check if file exists and is accessible
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return
        
        # Read the file as binary (bytes)
        with open(file_path, 'rb') as f:
            fitfile = FitFile(f)
            
            # Iterate over all messages in the file
            for record in fitfile.get_messages():
                print(f"\nMessage: {record.name}")
                
                # Print all fields in the message
                for data in record:
                    print(f"{data.name}: {data.value} ({data.units if data.units else 'no units'})")
                
    except Exception as e:
        print(f"An error occurred: {e}")




# Function to extract workout steps with per-zone distances
def extract_workout_data(file_path):
    distances = []  # Distance within each zone
    zones = []
    
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return None, None
        
        with open(file_path, 'rb') as f:
            fitfile = FitFile(f)
            for record in fitfile.get_messages('workout_step'):
                distance = record.get_value('duration_distance')
                intensity = record.get_value('intensity')
                notes = record.get_value('notes')
                
                # Skip steps without distance (e.g., repeat steps)
                if distance is None:
                    continue
                
                # Map intensity/notes to zone numbers
                if intensity == 'warmup' or intensity == 'cooldown' or (notes and 'Zone 1' in notes):
                    zone = 1
                elif notes and 'Zone 2' in notes:
                    zone = 2
                elif notes and 'Zone 3' in notes:
                    zone = 3
                elif intensity == '4':
                    zone = 4
                else:
                    zone = 1  # Default to Zone 1 if unclear
                
                distances.append([0, distance / 1000])  # Convert to km
                zones.append(zone)
                
        return distances, zones
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None
    

# Plotting function with per-zone distances and annotations
def plot_workout(distances, zones):
    if not distances or not zones:
        print("No data to plot.")
        return
    
    plt.figure(figsize=(10, 6))  # Wider figure for clarity
    current_x = 0  # Track position for non-overlapping steps
    
    for i, (dist_pair, zone) in enumerate(zip(distances, zones)):
        x = [current_x, current_x + dist_pair[1]]  # Start at current_x, end at current_x + distance
        y = [zone, zone]  # Constant zone height
        plt.step(x, y, where='post', label=f'Zone {zone}' if i == 0 else "")
        # Annotate the distance at the end of the step
        plt.annotate(f'{dist_pair[1]:.2f} km', (x[1], y[1]), textcoords="offset points", xytext=(0, 10), ha='center')
        current_x = x[1]  # Move to the end of this step for the next one
    
    plt.xlabel('Distance (km)')
    plt.ylabel('Zone')
    plt.title('Workout Intensity Zones with Per-Zone Distance')
    plt.yticks([1, 2, 3, 4, 5])  # Zones 1-5
    plt.grid(True)
    plt.legend()
    plt.show()

file_path = 'RHR9.FIT'
# read_fit_file(file_path)
distances, zones = extract_workout_data(file_path)
plot_workout(distances, zones)