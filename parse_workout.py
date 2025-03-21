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
        print(distances)       
        return distances, zones
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None
    

# Plotting function with per-zone distances and annotations
def plot_workout(distances, zones):
    if not distances or not zones:
        print("No data to plot.")
        return
    
    zone_colors = {
        1: 'cyan',
        2: 'blue',
        3: 'purple',
        4: 'pink',
        5: 'red'
    }
    
    plt.figure(figsize=(10, 6))
    current_x = 0
    
    # Store handles for legend
    legend_handles = {}
    
    for i, (dist_pair, zone) in enumerate(zip(distances, zones)):
        x = [current_x, current_x + dist_pair[1]]
        y = [zone, zone]
        color = zone_colors[zone]
        
        plt.step(x, y, where='pre', color='black', linewidth=1.5)
        line, = plt.plot(x, y, color=color)  # Capture the line object
        plt.fill_between(x, 0, y, color=color, alpha=0.6)
        
        mid_x = (x[0] + x[1]) / 2
        plt.annotate(f'{dist_pair[1]:.2f} km', (mid_x, zone), textcoords="offset points", 
                     xytext=(0, 10), ha='center', fontsize=10)
        
        # Add to legend handles if not already present
        if zone not in legend_handles:
            legend_handles[zone] = line
        
        current_x = x[1]
    
    zone_distances = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for dist_pair, zone in zip(distances, zones):
        zone_distances[zone] += dist_pair[1]
    
    legend_labels = [f'Zone {zone}: {zone_distances[zone]:.2f} km' for zone in sorted(zone_distances.keys()) if zone_distances[zone] > 0]
    plt.legend(handles=[legend_handles[zone] for zone in sorted(zone_distances.keys()) if zone_distances[zone] > 0], 
               labels=legend_labels, loc='upper right')
    
    total_distance = sum(dist_pair[1] for dist_pair in distances)
    plt.text(0.5, -0.1, f'Total Distance: {total_distance:.2f} km', ha='center', va='center', 
             transform=plt.gca().transAxes, fontsize=12)
    
    plt.xlabel('Distance (km)')
    plt.ylabel('Zone')
    plt.title('Workout Intensity Zones with Per-Zone Distance')
    plt.yticks([1, 2, 3, 4, 5])
    plt.grid(True)
    plt.tight_layout()
    plt.show()


#file_path = 'RHR9.FIT'
file_path = 'RLSP5.fit'
# read_fit_file(file_path)
distances, zones = extract_workout_data(file_path)
plot_workout(distances, zones)