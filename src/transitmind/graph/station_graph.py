import pandas as pd
import networkx as nx
import pickle


def build_station_graph() -> nx.Graph:
    # Load the stop_times.txt with all the trips
    df_stop_times = pd.read_csv("data/gtfs_subway/stop_times.txt")

    # Sort by stop sequence to ensure all trips are in the right order
    df_stop_times = df_stop_times.sort_values(["trip_id", "stop_sequence"])

    # Load the stops.txt for each stop info
    df_stops = pd.read_csv("data/gtfs_subway/stops.txt")

    # Set index on "stop_id" column to make searching O(1)
    df_stops = df_stops.set_index("stop_id")

    metro = nx.Graph()

    # Group all trip ID rows together and retrieve the unique stop_id values
    trip_stops = df_stop_times.groupby("trip_id")["stop_id"].unique()

    # Iterate over each trip to stops mapping
    for trip, stops in trip_stops.items():
        prev_stop = None

        for stop in stops:
            parent_stop = df_stops.loc[stop, "parent_station"]
            # Add an edge between the previous stop and 
            # your current stop in the trip
            if prev_stop is not None:
                metro.add_edge(prev_stop, parent_stop)
            
            prev_stop = parent_stop

    return metro

if __name__ == "__main__":
    G = build_station_graph()
    with open("data/graph.pkl", "wb") as wf:
        pickle.dump(G, wf)
    with open("data/graph.pkl", "rb") as rf:
        metro_graph = pickle.load(rf) 

    print(nx.shortest_path(metro_graph, "F02", "F15"))