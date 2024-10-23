import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import folium

def plot_station_availability(merged_data, station_id):
    station_data = merged_data[merged_data['station_id'] == station_id]
    fig = px.scatter(station_data, x='last_reported', y=['num_bikes_available', 'num_docks_available'],
                     title=f'Bike and Dock Availability for Station {station_id}')
    return fig

def plot_hourly_usage(merged_data):
    hourly_data = merged_data.groupby('hour').agg({
        'num_bikes_available': 'mean',
        'num_docks_available': 'mean'
    }).reset_index()
    
    chart = alt.Chart(hourly_data).mark_line().encode(
        x='hour:O',
        y=alt.Y('num_bikes_available:Q', title='Average Number Available'),
        color=alt.value('blue')
    ).properties(
        title='Average Hourly Bike Availability'
    ) + alt.Chart(hourly_data).mark_line().encode(
        x='hour:O',
        y=alt.Y('num_docks_available:Q', title='Average Number Available'),
        color=alt.value('red')
    )
    
    return chart

def create_station_map(stations_info):
    center_lat = stations_info['lat'].mean()
    center_lon = stations_info['lon'].mean()
    station_map = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    
    for _, station in stations_info.iterrows():
        folium.Marker(
            location=[station['lat'], station['lon']],
            popup=f"Station ID: {station['station_id']}",
            tooltip=f"Station ID: {station['station_id']}"
        ).add_to(station_map)
    
    return station_map

def plot_weekly_heatmap(merged_data):
    weekly_data = merged_data.groupby(['day_of_week', 'hour'])['num_bikes_available'].mean().reset_index()
    weekly_data['day_of_week'] = weekly_data['day_of_week'].map({0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'})
    
    fig = px.density_heatmap(weekly_data, x='day_of_week', y='hour', z='num_bikes_available',
                             title='Weekly Heatmap of Bike Availability',
                             labels={'num_bikes_available': 'Avg Bikes Available'})
    return fig