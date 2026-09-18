import pandas as pd
import networkx as nx

# Load the stop_times.txt with all the trips
df = pd.read_csv("data/gtfs_subway/stop_times.txt")

# Sort by stop sequence to ensure all trips are in the right order
df = df.sort_values(["trip_id", "stop_sequence"])

nyc_metro = nx.Graph()

# Group all trip ID rows together and retrieve the unique stop_id values
trip_stops = df.groupby("trip_id")["stop_id"].unique()

# Iterate over each trip to stops mapping
for trip, stops in trip_stops.items():
    prev_stop = None

    for stop in stops:
        parent_stop = stop.removesuffix("N").removesuffix("S")
        # Add an edge between the previous stop and 
        # your current stop in the trip
        if prev_stop is not None:
            nyc_metro.add_edge(prev_stop, parent_stop)
        
        prev_stop = parent_stop
