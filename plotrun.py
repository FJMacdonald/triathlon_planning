import matplotlib.pyplot as plt
from fitparse import FitFile
import os
def extract_run_data(file_path):
    distances = []
    heart_rates = []
    timestamps = []
    
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return None, None
        
        with open(file_path, 'rb') as f:
            fitfile = FitFile(f)
            for record in fitfile.get_messages('record'):
                distance = record.get_value('distance')  # meters
                hr = record.get_value('heart_rate')  # bpm
                timestamp = record.get_value('timestamp')
                
                if distance is not None and hr is not None and timestamp is not None:
                    distances.append(distance / 1000)  # Convert to km
                    heart_rates.append(hr)
                    timestamps.append(timestamp)
                
        return distances, heart_rates
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def plot_run(distances, heart_rates):
    if not distances or not heart_rates:
        print("No data to plot.")
        return
    
    # Estimate zones based on heart rate (assuming max HR = 200, adjust as needed)
    max_hr = 200  # Placeholder; replace with your actual max HR if known
    zones = [min(5, max(1, int(hr / max_hr * 5) + 1)) for hr in heart_rates]
    zone_colors = {1: 'blue', 2: 'green', 3: 'orange', 4: 'red', 5: 'purple'}
    
    # Calculate distance covered in each zone for legend
    zone_distances = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for i in range(1, len(distances)):
        dist_diff = distances[i] - distances[i-1]
        zone_distances[zones[i]] += dist_diff
    
    plt.figure(figsize=(12, 6))  # Wider for detailed run data
    legend_handles = {}
    
    # Plot each segment
    for i in range(1, len(distances)):
        x = [distances[i-1], distances[i]]
        y = [zones[i], zones[i]]  # Use zone as y-value
        color = zone_colors[zones[i]]
        
        plt.step(x, y, where='pre', color='black', linewidth=1)
        line, = plt.plot(x, y, color=color)
        plt.fill_between(x, 0, y, color=color, alpha=0.3)
        
        if zones[i] not in legend_handles:
            legend_handles[zones[i]] = line
    
    legend_labels = [f'Zone {zone}: {zone_distances[zone]:.2f} km' for zone in sorted(zone_distances.keys()) if zone_distances[zone] > 0]
    plt.legend(handles=[legend_handles[zone] for zone in sorted(zone_distances.keys()) if zone_distances[zone] > 0], 
               labels=legend_labels, loc='upper right')
    
    total_distance = distances[-1] - distances[0]
    plt.text(0.5, -0.1, f'Total Distance: {total_distance:.2f} km', ha='center', va='center', 
             transform=plt.gca().transAxes, fontsize=12)
    
    plt.xlabel('Distance (km)')
    plt.ylabel('Heart Rate Zone')
    plt.title('Run Heart Rate Zones Over Distance')
    plt.yticks([1, 2, 3, 4, 5])
    plt.grid(True)
    plt.tight_layout()
    plt.show()
file_path = 'morning_run.fit'
distances, heart_rates = extract_run_data(file_path)
plot_run(distances, heart_rates)

