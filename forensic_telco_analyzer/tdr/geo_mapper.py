import folium
import pandas as pd
from geopy.distance import geodesic
import os
from folium.plugins import HeatMap, MarkerCluster, TimestampedGeoJson
from datetime import datetime, timedelta
import json

class GeoMapper:
    def __init__(self, tower_data):
        self.tower_data = tower_data
        self.tower_locations = {}
        self.colors = ['blue', 'red', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
    
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
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Create a marker cluster for tower locations
        tower_cluster = MarkerCluster(name="Cell Towers").add_to(m)
        
        # Add markers for each tower ping
        points = []
        timestamps = []
        for _, row in imsi_data.iterrows():
            tower_id = row['cell_id']
            if tower_id in self.tower_locations:
                lat, lon = self.tower_locations[tower_id]
                timestamp = row['timestamp']
                timestamps.append(timestamp)
                
                # Create popup with detailed information
                popup_html = f"""
                <div style="font-family: Arial; width: 250px;">
                    <h4>Tower Ping Details</h4>
                    <b>IMSI:</b> {imsi}<br>
                    <b>Time:</b> {timestamp}<br>
                    <b>Tower ID:</b> {tower_id}<br>
                """
                
                # Add call details if available
                if 'destination_number' in row:
                    popup_html += f"<b>Called Number:</b> {row['destination_number']}<br>"
                if 'duration' in row:
                    popup_html += f"<b>Call Duration:</b> {row['duration']} seconds<br>"
                
                popup_html += "</div>"
                
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color='blue', icon='antenna', prefix='fa'),
                    tooltip=f"Tower: {tower_id} - {timestamp}"
                ).add_to(tower_cluster)
                
                points.append((lat, lon))
        
        # Connect points with a line showing movement path
        if len(points) > 1:
            folium.PolyLine(
                points, 
                color="red", 
                weight=3, 
                opacity=0.7, 
                tooltip=f"Movement path of IMSI: {imsi}",
                name=f"Movement Path - {imsi}"
            ).add_to(m)
        
        # Add time slider if we have timestamps
        if len(points) > 1 and all(timestamps):
            self._add_timestamped_geojson(m, imsi_data, imsi)
        
        return m
    
    def _add_timestamped_geojson(self, map_obj, imsi_data, imsi):
        """Add a time slider to visualize movement over time"""
        features = []
        
        for _, row in imsi_data.iterrows():
            tower_id = row['cell_id']
            if tower_id not in self.tower_locations:
                continue
                
            lat, lon = self.tower_locations[tower_id]
            timestamp = row['timestamp']
            
            # Convert timestamp to string format required by TimestampedGeoJson
            time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [lon, lat]  # GeoJSON uses [lon, lat] order
                },
                'properties': {
                    'time': time_str,
                    'icon': 'circle',
                    'iconstyle': {
                        'fillColor': 'red',
                        'fillOpacity': 0.8,
                        'stroke': 'true',
                        'radius': 7
                    },
                    'popup': f"IMSI: {imsi}<br>Time: {time_str}<br>Tower: {tower_id}"
                }
            }
            
            features.append(feature)
        
        # Create the TimestampedGeoJson layer
        TimestampedGeoJson(
            {
                'type': 'FeatureCollection',
                'features': features
            },
            period='PT1H',  # One hour period
            duration='PT1M',  # One minute transition duration
            add_last_point=True,
            auto_play=False,
            loop=False,
            max_speed=10,
            loop_button=True,
            date_options='YYYY-MM-DD HH:mm:ss',
            time_slider_drag_update=True,
        ).add_to(map_obj)
    
    def create_heatmap(self, output_dir=None):
        """Create a heatmap of all tower activity"""
        # Check if we have tower locations
        if not self.tower_locations:
            print("Error: No tower locations loaded")
            return None
        
        # Count activity at each tower
        tower_activity = self.tower_data['cell_id'].value_counts()
        
        # Create data for heatmap
        heat_data = []
        for tower_id, count in tower_activity.items():
            if tower_id in self.tower_locations:
                lat, lon = self.tower_locations[tower_id]
                # Add weight based on activity count
                heat_data.append([lat, lon, count])
        
        # Create map centered on India
        m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
        
        # Add heatmap layer
        HeatMap(heat_data, name="Tower Activity Heatmap").add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save map if output directory provided
        if output_dir:
            map_path = os.path.join(output_dir, 'tower_activity_heatmap.html')
            m.save(map_path)
            print(f"Heatmap saved to {map_path}")
        
        return m
    
    def create_multi_imsi_map(self, imsis, output_dir=None):
        """Create a map showing multiple IMSIs for comparison"""
        # Check if we have tower locations
        if not self.tower_locations:
            print("Error: No tower locations loaded")
            return None
        
        # Create map centered on India
        m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
        
        # Add each IMSI with a different color
        for i, imsi in enumerate(imsis):
            color = self.colors[i % len(self.colors)]
            
            # Filter data for this IMSI
            imsi_data = self.tower_data[self.tower_data['imsi'] == imsi]
            
            # Sort by timestamp
            imsi_data = imsi_data.sort_values('timestamp')
            
            # Skip if no data
            if len(imsi_data) == 0:
                continue
            
            # Create feature group for this IMSI
            fg = folium.FeatureGroup(name=f"IMSI: {imsi}")
            
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
                        icon=folium.Icon(color=color),
                        tooltip=f"IMSI: {imsi}"
                    ).add_to(fg)
                    
                    points.append((lat, lon))
            
            # Connect points with a line
            if len(points) > 1:
                folium.PolyLine(
                    points, 
                    color=color, 
                    weight=3, 
                    opacity=0.7,
                    tooltip=f"Movement path of IMSI: {imsi}"
                ).add_to(fg)
            
            # Add the feature group to the map
            fg.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save map if output directory provided
        if output_dir:
            map_path = os.path.join(output_dir, 'multi_imsi_comparison.html')
            m.save(map_path)
            print(f"Multi-IMSI map saved to {map_path}")
        
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
