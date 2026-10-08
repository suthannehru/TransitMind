import networkx as nx
import pandas as pd
import pickle

def build_station_graph() -> nx.DiGraph:
    # Load the stop_times.txt with all the trips
    df_stop_times = pd.read_csv("data/gtfs_subway/stop_times.txt")

    # Sort by stop sequence to ensure all trips are in the right order
    df_stop_times = df_stop_times.sort_values(["trip_id", "stop_sequence"])

    # Load the stops.txt for each stop info
    df_stops = pd.read_csv("data/gtfs_subway/stops.txt")

    # Set index on "stop_id" column to make searching O(1)
    df_stops = df_stops.set_index("stop_id")

    # Use trips.txt to determine the appropriate lines between edges
    df_trips = pd.read_csv("data/gtfs_subway/trips.txt")
    trip_info = df_trips.set_index("trip_id")

    # Load the transfers between stations
    df_transfers = pd.read_csv("data/gtfs_subway/transfers.txt")

    transfers = df_transfers[df_transfers["from_stop_id"] != df_transfers["to_stop_id"]]

    metro = nx.DiGraph()

    # Group all trip ID rows together and retrieve the unique stop_id values
    trip_stops = df_stop_times.groupby("trip_id")["stop_id"].unique()

    # Iterate over each trip to stops mapping
    for trip, stops in trip_stops.items():
        prev_stop = None

        for stop in stops:
            direction = stop[-1]
            parent_stop = df_stops.loc[stop, "parent_station"]
            stop_name = df_stops.loc[stop, "stop_name"]
            metro.add_node(parent_stop, name=stop_name)
            # Add an edge between the previous stop and 
            # your current stop in the trip
            if prev_stop is not None:
                line = trip_info.loc[trip, "route_id"]
                head_sign = trip_info.loc[trip, "trip_headsign"]
                if metro.has_edge(prev_stop, parent_stop):
                    metro.edges[prev_stop, parent_stop]["lines"].add(line)
                    metro.edges[prev_stop, parent_stop]["head_sign"].setdefault(line, set()).add(head_sign)
                else:
                    metro.add_edge(prev_stop, parent_stop, direction=direction, head_sign={line: {head_sign}}, lines={line})
            
            prev_stop = parent_stop

    # Adding edges between stations with transfers
    for transfer in transfers.itertuples():
        metro.add_edge(transfer.from_stop_id, transfer.to_stop_id, transfer=True)
        metro.add_edge(transfer.to_stop_id, transfer.from_stop_id, transfer=True)

    return metro

if __name__ == "__main__":
    G = build_station_graph()
    with open("data/graph.pkl", "wb") as f:
        pickle.dump(G, f)