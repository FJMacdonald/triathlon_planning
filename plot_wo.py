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

# def plot_run(distances, heart_rates):
#     if not distances or not heart_rates:
#         print("No data to plot.")
#         return
    
#     # Estimate zones based on heart rate (assuming max HR = 200, adjust as needed)
#     max_hr = 200  # Placeholder; replace with your actual max HR if known
#     zones = [min(5, max(1, int(hr / max_hr * 5) + 1)) for hr in heart_rates]
#     zone_colors = {1: 'blue', 2: 'green', 3: 'orange', 4: 'red', 5: 'purple'}
    
#     # Calculate distance covered in each zone for legend
#     zone_distances = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
#     for i in range(1, len(distances)):
#         dist_diff = distances[i] - distances[i-1]
#         zone_distances[zones[i]] += dist_diff
    
#     plt.figure(figsize=(12, 6))  # Wider for detailed run data
#     legend_handles = {}
    
#     # Plot each segment
#     for i in range(1, len(distances)):
#         x = [distances[i-1], distances[i]]
#         y = [zones[i], zones[i]]  # Use zone as y-value
#         color = zone_colors[zones[i]]
        
#         plt.step(x, y, where='pre', color='black', linewidth=1)
#         line, = plt.plot(x, y, color=color)
#         plt.fill_between(x, 0, y, color=color, alpha=0.3)
        
#         if zones[i] not in legend_handles:
#             legend_handles[zones[i]] = line
    
#     legend_labels = [f'Zone {zone}: {zone_distances[zone]:.2f} km' for zone in sorted(zone_distances.keys()) if zone_distances[zone] > 0]
#     plt.legend(handles=[legend_handles[zone] for zone in sorted(zone_distances.keys()) if zone_distances[zone] > 0], 
#                labels=legend_labels, loc='upper right')
    
#     total_distance = distances[-1] - distances[0]
#     plt.text(0.5, -0.1, f'Total Distance: {total_distance:.2f} km', ha='center', va='center', 
#              transform=plt.gca().transAxes, fontsize=12)
    
#     plt.xlabel('Distance (km)')
#     plt.ylabel('Heart Rate Zone')
#     plt.title('Run Heart Rate Zones Over Distance')
#     plt.yticks([1, 2, 3, 4, 5])
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()






# def extract_run_data(file_path):
#     distances = []
#     speeds = []  # We'll use speed to calculate pace
    
#     try:
#         if not os.path.exists(file_path):
#             print(f"Error: File '{file_path}' not found.")
#             return None, None
        
#         with open(file_path, 'rb') as f:
#             fitfile = FitFile(f)
#             for record in fitfile.get_messages('record'):
#                 distance = record.get_value('distance')  # meters
#                 speed = record.get_value('enhanced_speed') or record.get_value('speed')  # m/s
                
#                 if distance is not None and speed is not None and speed > 0:  # Avoid division by zero
#                     distances.append(distance / 1000)  # Convert to km
#                     speeds.append(speed)
                
#         return distances, speeds
    
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None, None

# def plot_run(distances, speeds):
#     if not distances or not speeds:
#         print("No data to plot.")
#         return
    
#     # Calculate pace in minutes per kilometer
#     paces = [60 / (speed * 3.6) for speed in speeds]  # Convert m/s to km/h (x3.6), then to min/km
    
#     plt.figure(figsize=(12, 6))
    
#     # Plot pace over distance
#     plt.plot(distances, paces, color='blue', label='Pace')
#     plt.fill_between(distances, 0, paces, color='blue', alpha=0.2)
    
#     # Set reasonable y-axis limits based on typical running paces
#     plt.ylim(min(paces) - 1, max(paces) + 1)  # Add padding
    
#     total_distance = distances[-1] - distances[0]
#     avg_pace = sum(paces) / len(paces)  # Simple average for display
#     plt.text(0.5, -0.1, f'Total Distance: {total_distance:.2f} km\nAvg Pace: {int(avg_pace)}:{int((avg_pace % 1) * 60):02d} min/km', 
#              ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
    
#     plt.xlabel('Distance (km)')
#     plt.ylabel('Pace (min/km)')
#     plt.title('Run Pace Over Distance')
#     plt.grid(True)
#     plt.legend(loc='upper right')
#     plt.tight_layout()
#     plt.show()

# # Usage
# file_path = 'morning_run.fit'
# distances, speeds = extract_run_data(file_path)
# plot_run(distances, speeds)

# def plot_run(distances, speeds):
#     if not distances or not speeds:
#         print("No data to plot.")
#         return
    
#     # Calculate pace in minutes per kilometer
#     paces = [60 / (speed * 3.6) for speed in speeds]  # min/km
    
#     plt.figure(figsize=(12, 6))
    
#     # Plot pace over distance
#     plt.plot(distances, paces, color='blue', label='Pace')
#     plt.fill_between(distances, 0, paces, color='blue', alpha=0.2)
    
#     # Convert pace to min:sec for y-axis labels
#     pace_min = [int(p) for p in paces]
#     pace_sec = [int((p % 1) * 60) for p in paces]
#     y_ticks = [p for p in range(int(min(paces)), int(max(paces)) + 1)]  # Whole minute range
#     y_labels = [f"{m}:00" for m in y_ticks]  # Format as MM:00
    
#     plt.yticks(y_ticks, y_labels)
#     plt.gca().invert_yaxis()  # Invert so slowest (highest) pace is at bottom
    
#     total_distance = distances[-1] - distances[0]
#     avg_pace = sum(paces) / len(paces)
#     avg_min = int(avg_pace)
#     avg_sec = int((avg_pace % 1) * 60)
#     plt.text(0.5, -0.15, f'Total Distance: {total_distance:.2f} km\nAvg Pace: {avg_min}:{avg_sec:02d} min/km', 
#              ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
    
#     plt.xlabel('Distance (km)')
#     plt.ylabel('Pace (min:sec/km)')
#     plt.title('Run Pace Over Distance')
#     plt.grid(True)
#     plt.legend(loc='upper right')
#     plt.tight_layout()
#     plt.show()

# def extract_run_data(file_path):
#     distances = []
#     speeds = []
    
#     try:
#         if not os.path.exists(file_path):
#             print(f"Error: File '{file_path}' not found.")
#             return None, None
        
#         with open(file_path, 'rb') as f:
#             fitfile = FitFile(f)
#             for i, record in enumerate(fitfile.get_messages('record')):
#                 distance = record.get_value('distance')
#                 # Explicitly target speed fields
#                 speed = record.get_value('enhanced_speed')
#                 if speed is None:
#                     speed = record.get_value('speed')
                
#                 if distance is not None and speed is not None and speed > 0:
#                     # Log raw values
#                     if i < 5:
#                         print(f"Record {i}: distance={distance} m, speed={speed} m/s (raw), "
#                               f"cadence={record.get_value('cadence')} rpm, "
#                               f"unknown_88={record.get_value('unknown_88')}")
#                     # Check magnitude
#                     if speed > 10:
#                         print(f"Warning: High speed: {speed} m/s at distance {distance} m")
#                     elif speed < 0.1:
#                         print(f"Warning: Low speed: {speed} m/s - possible scaling issue")
#                     distances.append(distance / 1000)
#                     speeds.append(speed)
    
#         print(f"Extracted speeds (first 5): {speeds[:5]}")
#         return distances, speeds
    
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None, None
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
                    distances.append(distance / 1000)  # meters to km
                    speeds.append(speed)  # m/s
                    if i < 5:
                        print(f"Record {i}: distance={distance} m, speed={speed} m/s")
    
        return distances, speeds
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

# def plot_run(distances, speeds):
#     if not distances or not speeds:
#         print("No data to plot.")
#         return
    
#     paces = [60 / (speed * 3.6) for speed in speeds]  # min/km
    
#     print(f"Paces (min/km): {[f'{int(p)}:{int((p % 1) * 60):02d}' for p in paces[:5]]}")
    
#     plt.figure(figsize=(12, 6))
#     plt.plot(distances, paces, color='blue', label='Pace')
#     plt.fill_between(distances, 0, paces, color='blue', alpha=0.2)
    
#     min_pace, max_pace = min(paces), max(paces)
#     y_ticks = [p for p in range(int(min_pace), int(max_pace) + 1)]
#     y_labels = [f"{m}:00" for m in y_ticks]
#     plt.yticks(y_ticks, y_labels)
#     plt.gca().invert_yaxis()
    
#     total_distance = distances[-1] - distances[0]
#     avg_pace = sum(paces) / len(paces)
#     avg_min = int(avg_pace)
#     avg_sec = int((avg_pace % 1) * 60)
    
#     plt.text(0.5, -0.15, f'Total Distance: {total_distance:.2f} km\nAvg Pace: {avg_min}:{avg_sec:02d} min/km', 
#              ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
    
#     plt.xlabel('Distance (km)')
#     plt.ylabel('Pace (min:sec/km)')
#     plt.title('Run Pace Over Distance')
#     plt.grid(True)
#     plt.legend(loc='upper right')
#     plt.tight_layout()
#     plt.show()


# # Usage (assuming extract_run_data is unchanged)
# file_path = 'morning_run.fit'
# distances, speeds = extract_run_data(file_path)
# plot_run(distances, speeds)


import matplotlib.pyplot as plt
from matplotlib import ticker

def plot_run(distances, speeds):
    if not distances or not speeds:
        print("No data to plot.")
        return
    
    # Calculate pace in min/km
    paces = [60 / (speed * 3.6) for speed in speeds]
    # Clip paces slower than 8:00 to 8:00
    paces_clipped = [min(p, 8) for p in paces]  # 8 min/km = max displayed
    
    print(f"Paces (min/km): {[f'{int(p)}:{int((p % 1) * 60):02d}' for p in paces[:5]]}")
    print(f"Clipped paces: {[f'{int(p)}:{int((p % 1) * 60):02d}' for p in paces_clipped[:5]]}")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(distances, paces_clipped, color='blue', label='Pace')
    ax.fill_between(distances, 8, paces_clipped, color='blue', alpha=0.2)  # Fill from 8:00
    
    # Y-axis: 8:00 (slowest) to fastest pace (e.g., 4:00)
    min_pace = min(paces_clipped)
    y_ticks = [p for p in range(int(min_pace), 9)]  # Up to 8:00
    y_labels = [f"{m}:00" for m in y_ticks]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.invert_yaxis()  # Fastest (lower numbers) at top
    
    # Tooltip formatter
    def format_coord(x, y):
        pace_min = int(y)
        pace_sec = int((y % 1) * 60)
        return f'x={x:.2f} km, y={pace_min}:{pace_sec:02d} min/km'
    ax.format_coord = format_coord
    
    total_distance = distances[-1] - distances[0]
    avg_pace = sum(paces) / len(paces)  # Use unclipped for avg
    avg_min = int(avg_pace)
    avg_sec = int((avg_pace % 1) * 60)
    ax.text(0.5, -0.15, f'Total Distance: {total_distance:.2f} km\nAvg Pace: {avg_min}:{avg_sec:02d} min/km', 
            ha='center', va='center', transform=ax.transAxes, fontsize=12)
    
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('Pace (min:sec/km)')
    ax.set_title('Run Pace Over Distance')
    ax.grid(True)
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.show()

# Usage
file_path = 'morning_run.fit'
distances, heart_rates = extract_run_data(file_path)
plot_run(distances, heart_rates)


