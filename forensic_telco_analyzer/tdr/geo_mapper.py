import folium
import pandas as pd
from geopy.distance import geodesic
import os

class GeoMapper:
    def __init__(self, tower_data):
        self.tower_data = tower_data
        self.tower_locations = {}
    
    def load_tower_locations(self, tower_location_file):
        """Load tower location data from CSV"""
        try:
            # Check if file exists
            if not os.path.exists(tower_location_file):
                print(f"Error: Tower location file '{tower_location_file}' not found")
                return False
                
            locations = pd.read_csv(tower_location_file)
            
            # Create dictionary of tower_id -> (lat, lon)
            for _, row in locations.iterrows():
                self.tower_locations[row['cell_id']] = (row['latitude'], row['longitude'])
            
            return True
        except Exception as e:
            print(f"Error loading tower locations: {e}")
            return False
    
    def create_movement_map(self, imsi, start_time=None, end_time=None):
        """Create a map showing movement of a specific IMSI"""
        # Filter data for the specific IMSI
        imsi_data = self.tower_data[self.tower_data['imsi'] == imsi]
        
        # Apply time filters if provided
        if start_time:
            imsi_data = imsi_data[imsi_data['timestamp'] >= start_time]
        if end_time:
            imsi_data = imsi_data[imsi_data['timestamp'] <= end_time]
        
        # Sort by timestamp
        imsi_data = imsi_data.sort_values('timestamp')
        
        # Check if we have any data
        if len(imsi_data) == 0:
            print(f"No data found for IMSI {imsi}")
            # Return a default map centered on India
            return folium.Map(location=[20.5937, 78.9629], zoom_start=5)
        
        # Create map centered on first tower
        first_tower = imsi_data.iloc[0]['cell_id']
        if first_tower in self.tower_locations:
            center_lat, center_lon = self.tower_locations[first_tower]
        else:
            # Default center if tower location unknown
            center_lat, center_lon = 20.5937, 78.9629  # India coordinates
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        
        # Add markers for each tower ping
        points = []
        for _, row in imsi_data.iterrows():
            tower_id = row['cell_id']
            if tower_id in self.tower_locations:
                lat, lon = self.tower_locations[tower_id]
                timestamp = row['timestamp']
                
                folium.Marker(
                    location=[lat, lon],
                    popup=f"IMSI: {imsi}<br>Time: {timestamp}<br>Tower: {tower_id}",
                    icon=folium.Icon(color='blue')
                ).add_to(m)
                
                points.append((lat, lon))
        
        # Connect points with a line
        if len(points) > 1:
            folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)
        
        return m
    
    def calculate_movement_speed(self, imsi):
        """Calculate movement speed between tower pings"""
        # Filter data for the specific IMSI
        imsi_data = self.tower_data[self.tower_data['imsi'] == imsi].sort_values('timestamp')
        
        speeds = []
        for i in range(len(imsi_data) - 1):
            current = imsi_data.iloc[i]
            next_row = imsi_data.iloc[i + 1]
            
            current_tower = current['cell_id']
            next_tower = next_row['cell_id']
            
            # Skip if tower locations unknown
            if current_tower not in self.tower_locations or next_tower not in self.tower_locations:
                continue
            
            # Calculate distance in kilometers
            distance = geodesic(
                self.tower_locations[current_tower],
                self.tower_locations[next_tower]
            ).kilometers
            
            # Calculate time difference in hours
            time_diff = (next_row['timestamp'] - current['timestamp']).total_seconds() / 3600
            
            # Calculate speed in km/h
            if time_diff > 0:
                speed = distance / time_diff
                speeds.append({
                    'from_tower': current_tower,
                    'to_tower': next_tower,
                    'timestamp': current['timestamp'],
                    'distance_km': distance,
                    'time_hours': time_diff,
                    'speed_kmh': speed
                })
        
        return pd.DataFrame(speeds)
